import telebot
import requests
import json
import os
import time
from telebot import types
from datetime import datetime
import payment_plugin
import pymongo
from pymongo import MongoClient

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7066124462
OWNER_USERNAME = "@Lexluther_supreme"
API_BASE_URL = os.getenv("API_BASE_URL")

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("⚠️ WARNING: MONGO_URI not found in Environment Variables!")
else:
    print("✅ MONGO_URI detected, connecting to database...")

client = MongoClient(MONGO_URI)
db_mongo = client['detor_osint_bot']

# Collections (Centralized Variables)
USERS_COL = "users"
COUPONS_COL = "coupons"
PLANS_COL = "plans"
HIST_COL = "history"
SETTING_COL = "settings" # Fixed: Missing variable added

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# Plugin Linking
print("🔗 Linking Plugin...")
payment_plugin.setup_payment_handlers(bot, ADMIN_ID)
print("🔗 Plugin Linked!")

# --- MONGODB DATABASE HANDLERS ---

def load_db(collection_name):
    col = db_mongo[collection_name]
    data = {}
    try:
        for item in col.find():
            uid = str(item.pop('_id')) 
            data[uid] = item
    except Exception as e:
        print(f"❌ Database Load Error ({collection_name}): {e}")
    return data

def save_db(collection_name, uid, data_to_save):
    col = db_mongo[collection_name]
    try:
        # Create a copy to avoid modifying original dict in-place
        temp_data = data_to_save.copy()
        if '_id' in temp_data:
            temp_data.pop('_id')
        
        col.update_one({'_id': str(uid)}, {'$set': temp_data}, upsert=True)
    except Exception as e:
        print(f"❌ Database Save Error ({collection_name}): {e}")

def get_user(uid, name="Unknown"):
    suid = str(uid)
    col = db_mongo[USERS_COL]
    user = col.find_one({'_id': suid})
    
    if not user:
        new_user = {
            "name": name, 
            "credits": 3, 
            "is_vip": False, 
            "total_search": 0, 
            "last_bonus": 0
        }
        save_db(USERS_COL, suid, new_user)
        return new_user
    return user

# --- KEYBOARDS ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 ɪɴғᴏ ʟᴏᴏᴋᴜᴘ", "👤 ᴍʏ ɪᴅ")
    markup.row("🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "💰 ᴅᴀɪʟʏ ʙᴏɴᴜs")
    markup.row("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ")
    if uid == ADMIN_ID: markup.row("🛠 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    get_user(message.from_user.id, message.from_user.first_name)
    user_states[message.from_user.id] = None
    
    welcome = (
        f"<b>WELCOME TO DETOR OSINT BOT  // V1.5</b>\n"
        f"──────────────────────────────\n"
        f"🛰️ ᴜsᴇʀ <code> {message.from_user.first_name}</code>\n"
        f"📡 sʏsᴛᴇᴍ ᴘʀᴏᴛᴏᴄᴏʟ: <code>ᴀᴄᴛɪᴠᴇ [sᴇᴄᴜʀᴇ]</code>\n"
        f"📟 ᴜsᴇʀ ɪᴅ: <code>{message.from_user.id}</code>\n"
        f"──────────────────────────────\n\n"
        f"📂 <b>ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ ᴅɪʀᴇᴄᴛɪᴠᴇs:</b>\n"
        f"├─ ⚡ <b>ǫᴜɪᴄᴋ sᴇᴀʀᴄʜ:</b> Tap 'Info Lookup'\n"
        f"├─ 🔐 <b>ᴅᴀᴛᴀ sᴀғᴇᴛʏ:</b> End-to-End Encrypted\n"
        f"└─ 🎁 <b>ᴄʀᴇᴅɪᴛs:</b> Credits updated daily\n\n"
        f"<b>sᴇʟᴇᴄᴛ ᴀ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ɪɴɪᴛɪᴀᴛᴇ...</b>\n"
        f"──────────────────────────────\n"
        f"🛡️ <b>ᴏᴡɴᴇʀ:</b> {OWNER_USERNAME}"
    )
    
    video_url = "https://graph.org/file/72bb6bd41e981d66d1cdb-a1436c7780a84951af.mp4"
    try:
        bot.send_video(message.chat.id, video_url, caption=welcome, parse_mode="HTML", reply_markup=main_menu(message.from_user.id))
    except:
        bot.send_message(message.chat.id, welcome, parse_mode="HTML", reply_markup=main_menu(message.from_user.id))

# --- BUTTON HANDLERS ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    text = message.text
    
    if text == "🔍 ɪɴғᴏ ʟᴏᴏᴋᴜᴘ":
        user_states[uid] = "waiting_number"
        lookup_prompt = (
            "<b>🛰️ ᴇxᴛʀᴀᴄᴛɪᴏɴ ᴘʀᴏᴛᴏᴄᴏʟ: ᴀᴄᴛɪᴠᴇ</b>\n"
            "──────────────────────────────\n"
            "📥 <b>ɪɴᴘᴜᴛ ʀᴇǫᴜɪʀᴇᴅ:</b>\n"
            "ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ɴᴜᴍʙᴇʀ.\n\n"
            "📝 <b>ғᴏʀᴍᴀᴛ:</b> <code>10 DIGITS ONLY</code>\n"
            "🛡️ <b>sᴛᴀᴛᴜs:</b> ᴀᴡᴀɪᴛɪɴɢ ᴅᴀᴛᴀ...\n"
            "──────────────────────────────\n"
            "⚠️ <i>Do not include +91 or any spaces.</i>"
        )
        bot.send_message(message.chat.id, lookup_prompt, parse_mode="HTML")
    
    elif text == "👤 ᴍʏ ɪᴅ":
        u = get_user(uid)
        role = "👑 Owner" if uid == ADMIN_ID else ("💎 VIP" if u['is_vip'] else "👤 User")
        res = f"<b>👤 My Profile</b>\n━━━━━━━━━━━━━━\n<b>Role:</b> {role}\n<b>Credits:</b> {u['credits'] if not u['is_vip'] else 'Unlimited'}\n<b>Searches:</b> {u['total_search']}\n<b>ID:</b> <code>{uid}</code>"
        bot.send_message(message.chat.id, res, parse_mode="HTML")

    elif text == "💰 ᴅᴀɪʟʏ ʙᴏɴᴜs":
        claim_bonus(message)

    elif text == "🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ":
        user_states[uid] = "waiting_redeem"
        bot.send_message(message.chat.id, "🎟 <b>Enter Coupon Code:</b>", parse_mode="HTML")

    elif text == "👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ":
        bot.send_message(message.chat.id, f"<b>Message me here:</b> {OWNER_USERNAME}", parse_mode="HTML")

    elif text == "🛠 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ" and uid == ADMIN_ID:
        show_admin_panel(message)

    elif user_states.get(uid) == "waiting_number":
        if text.isdigit() and len(text) == 10:
            process_lookup(message, text)
            user_states[uid] = None
        else:
            bot.reply_to(message, "❌ Invalid! 10 digit number bhejein.")

    elif user_states.get(uid) == "waiting_redeem":
        process_redeem(message, text)
        user_states[uid] = None

# --- CORE FUNCTIONS ---
def claim_bonus(message):
    uid = str(message.from_user.id)
    settings_db = load_db(SETTING_COL) 
    settings = settings_db.get('global', {}) 
    bonus_amt = settings.get("current_bonus", 0)
    
    if bonus_amt <= 0:
        return bot.send_message(message.chat.id, "<b>🎁 Bonus Inactive.</b>", parse_mode="HTML")
    
    u = get_user(uid, message.from_user.first_name)
    current_time = time.time()
    
    if current_time - u.get('last_bonus', 0) > 86400:
        u['credits'] += bonus_amt
        u['last_bonus'] = current_time
        save_db(USERS_COL, uid, u)
        bot.reply_to(message, f"✅ <b>Success!</b> {bonus_amt} credits added.", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ <b>Already Claimed!</b> Come back later.", parse_mode="HTML")

def process_redeem(message, code):
    uid = str(message.from_user.id)
    code = code.upper().strip()
    cp_db = load_db(COUPONS_COL)
    u = get_user(uid, message.from_user.first_name)
    
    if code in cp_db:
        cp = cp_db[code]
        if uid in cp.get('users', []): bot.reply_to(message, "❌ Already claimed.")
        elif cp.get('uses', 0) <= 0: bot.reply_to(message, "❌ Expired.")
        else:
            cp['uses'] -= 1
            if 'users' not in cp: cp['users'] = []
            cp['users'].append(uid)
            u['credits'] += cp['amount']
            save_db(COUPONS_COL, code, cp)
            save_db(USERS_COL, uid, u)
            bot.reply_to(message, f"✅ Success! {cp['amount']} credits added.")
    else: bot.reply_to(message, "❌ Invalid Coupon.")

def process_lookup(message, num):
    uid = str(message.from_user.id)
    u_name = message.from_user.first_name
    u = get_user(uid, u_name)

    if u['credits'] <= 0 and not u['is_vip']: 
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 ʙᴜʏ ᴄʀᴇᴅɪᴛs", callback_data="buy_credits"))
        return bot.send_message(message.chat.id, "<b>⚠️ 0 Credits!</b>", parse_mode="HTML", reply_markup=markup)

    wait = bot.send_message(message.chat.id, "🔍 Searching...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(f"{API_BASE_URL}{num}", headers=headers, timeout=20)
        res = response.json()
        
        if res.get("status") in [True, "true", "True"]:
            results = res.get("results", [])
            if results:
                if not u['is_vip']: u['credits'] -= 1
                u['total_search'] += 1
                save_db(USERS_COL, uid, u)

                for item in results:
                    log_entry = {"timestamp": datetime.now().strftime('%d/%m %H:%M'), "uid": uid, "u_name": u_name, "target": num}
                    save_db(HIST_COL, f"log_{int(time.time()*1000)}", log_entry)

                    output = (
        f"👤 <b>REAL NAME:</b> <code>{target_name}</code>\n"
        f"👨 <b>FATHER NAME:</b> <code>{item.get('fname', 'N/A')}</code>\n"
        f"🆔 <b>ADHAAR ID:</b> <code>[Redacted]</code>\n" # Security rule
        f"📱 <b>PRIMARY:</b> <code>{item.get('MOBILE', num)}</code>\n"
        f"📞 <b>ALTERNATE:</b> <code>{item.get('alt', 'N/A')}</code>\n"
        f"📧 <b>EMAIL:</b> <code>{item.get('EMAIL', 'N/A')}</code>\n"
        f"📍 <b>CIRCLE/SIM:</b> <code>{item.get('circle', 'N/A')}</code>\n"
        f"🏠 <b>ADDRESS:</b> <code>{item.get('ADDRESS', 'N/A')}</code>\n\n"
        f"✨ <b>Powered by: {OWNER_USERNAME}</b>"
    )
    bot.send_message(message.chat.id, output, parse_mode="HTML")
# --- ADMIN PANEL & STEPS ---
def show_admin_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Add Credit", callback_data="adm_add"),
        types.InlineKeyboardButton("👑 Add VIP", callback_data="adm_vip"),
        types.InlineKeyboardButton("🎟 Gen Coupon", callback_data="adm_gen"),
        types.InlineKeyboardButton("📜 History", callback_data="adm_hist"),
        types.InlineKeyboardButton("📊 Stats", callback_data="adm_stats"),
        types.InlineKeyboardButton("💰 Set Bonus", callback_data="adm_bonus")
    )
    bot.send_message(message.chat.id, "🛠 <b>ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "adm_add":
        msg = bot.send_message(call.message.chat.id, "Enter ID and Amount:")
        bot.register_next_step_handler(msg, admin_add_credit)
    elif call.data == "adm_vip":
        msg = bot.send_message(call.message.chat.id, "Enter User ID for VIP:")
        bot.register_next_step_handler(msg, admin_add_vip)
    elif call.data == "adm_gen":
        msg = bot.send_message(call.message.chat.id, "Format: CODE AMOUNT USERS")
        bot.register_next_step_handler(msg, admin_gen_coupon)
    elif call.data == "adm_bonus":
        msg = bot.send_message(call.message.chat.id, "Enter Bonus Amount:")
        bot.register_next_step_handler(msg, admin_set_bonus)
    elif call.data == "adm_hist":
        hist_db = load_db(HIST_COL)
        res = "📜 <b>LATEST LOGS</b>\n"
        sorted_logs = sorted(hist_db.values(), key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
        for log in sorted_logs:
            res += f"🕒 {log['timestamp']} | {log['u_name']} | {log['target']}\n"
        bot.send_message(call.message.chat.id, res, parse_mode="HTML")
    elif call.data == "adm_stats":
        db = load_db(USERS_COL)
        bot.send_message(call.message.chat.id, f"📊 <b>Total Users:</b> {len(db)}", parse_mode="HTML")

def admin_add_credit(message):
    try:
        tid, amt = message.text.split()
        user = get_user(tid)
        user['credits'] += int(amt)
        save_db(USERS_COL, tid, user)
        bot.reply_to(message, f"✅ Added {amt} credits.")
    except: bot.reply_to(message, "❌ Error.")

def admin_add_vip(message):
    try:
        tid = message.text.strip()
        user = get_user(tid)
        user['is_vip'] = True
        save_db(USERS_COL, tid, user)
        bot.reply_to(message, f"👑 {tid} is VIP.")
    except: bot.reply_to(message, "❌ Error.")

def admin_gen_coupon(message):
    try:
        code, amt, uses = message.text.split()
        save_db(COUPONS_COL, code.upper(), {"amount": int(amt), "uses": int(uses), "users": []})
        bot.reply_to(message, f"🎟 Coupon {code.upper()} Created.")
    except: bot.reply_to(message, "❌ Error.")

def admin_set_bonus(message):
    if message.text.isdigit():
        save_db(SETTING_COL, "global", {"current_bonus": int(message.text)})
        bot.reply_to(message, "💰 Bonus Updated.")

if __name__ == "__main__":
    print("🚀 Bot is flying...")
    bot.infinity_polling()
    
