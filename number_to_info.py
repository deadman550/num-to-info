import telebot
import requests
import json
import os
import time
from telebot import types
from datetime import datetime
import payment_plugin

# --- CONFIGURATION ---
BOT_TOKEN = '8724276185:AAEBW_yMm9GYW3s1BNUM34QbJHi5Jju7tWU'
ADMIN_ID = 7066124462
OWNER_USERNAME = "@Lexluther_supreme"
API_BASE_URL = "https://cyber-osint-num-infos.vercel.app/api/numinfo?key=Prime01&num="
DB_FILE = "users_data.json"
CP_FILE = "coupons.json"
SETTING_FILE = "settings.json"
HIST_FILE = "history.json"

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

payment_plugin.setup_payment_handlers(bot, ADMIN_ID)

print("🔗 Linking Plugin...")
payment_plugin.setup_payment_handlers(bot, ADMIN_ID)
print("🔗 Plugin Linked!")

# --- DATABASE HANDLERS ---
def load_db(file):
    if not os.path.exists(file): return {}
    try:
        with open(file, "r") as f: return json.load(f)
    except: return {}

def save_db(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

def get_user(uid, name="Unknown"):
    db = load_db(DB_FILE)
    suid = str(uid)
    if suid not in db:
        db[suid] = {"name": name, "credits": 3, "is_vip": False, "total_search": 0, "last_bonus": 0}
        save_db(DB_FILE, db)
    return db[suid]

# --- KEYBOARDS ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 ɪɴғᴏ ʟᴏᴏᴋᴜᴘ", "👤 ᴍʏ ɪᴅ")
    markup.row("🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "💰 ᴅᴀɪʟʏ ʙᴏɴᴜs")
    markup.row("👨‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ")
    if uid == ADMIN_ID: markup.row("🛠 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")
    return markup

# --- START COMMAND (UNIQUE COMMAND CENTER UI) ---
@bot.message_handler(commands=['start'])
def start(message):
    get_user(message.from_user.id, message.from_user.first_name)
    user_states[message.from_user.id] = None
    
    # Custom Small-Caps Style and Technical Phrasing
    welcome = (
        f"<b>WELCOMW TO DETOR OSINT BOT  // V1.5</b>\n"
        f"──────────────────────────────\n"
        f"🛰️ ᴜsᴇʀ <code> {message.from_user.first_name}</code>\n"
        f"📡 sʏsᴛᴇᴍ ᴘʀᴏᴛᴏᴄᴏʟ: <code>ᴀᴄᴛɪᴠᴇ [sᴇᴄᴜʀᴇ]</code>\n"
        f"📟 ᴜsᴇʀ ɪᴅ:<code>{message.from_user.id}</code>\n"
        f"──────────────────────────────\n\n"
        f"📂 <b>ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ ᴅɪʀᴇᴄᴛɪᴠᴇs:</b>\n"
        f"├─ ⚡ <b>ǫᴜɪᴄᴋ sᴇᴀʀᴄʜ:</b> Tap 'Info Lookup'\n"
        f"├─ 🔐 <b>ᴅᴀᴛᴀ sᴀғᴇᴛʏ:</b> End-to-End Encrypted\n"
        f"└─  🎁<b>ᴄʀᴇᴅɪᴛs</b> Credits updated daily\n\n"
        f"<b>sᴇʟᴇᴄᴛ ᴀ ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ɪɴɪᴛɪᴀᴛᴇ...</b>\n"
        f"──────────────────────────────\n"
        f"🛡️ <b>ᴏwɴᴇr:</b> {OWNER_USERNAME}"
    )
    
    video_url = "https://graph.org/file/72bb6bd41e981d66d1cdb-a1436c7780a84951af.mp4"

    try:
        bot.send_video(
            message.chat.id, 
            video_url, 
            caption=welcome, 
            parse_mode="HTML", 
            reply_markup=main_menu(message.from_user.id)
        )
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
        
        
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    uid = message.from_user.id
    state = user_states.get(uid, "")
    
    if state.startswith("sending_ss"):
        credits = state.split("|")[1]
        user_states[uid] = None
        
        # User ko notification
        bot.reply_to(message, "⏳ <b>ᴠᴇʀɪғʏɪɴɢ...</b>\nʏᴏᴜʀ ᴘʀᴏᴏғ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴ.", parse_mode="HTML")
        
        # Admin ko screenshot bhejna
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"p_app_{uid}_{credits}"),
            types.InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"p_rej_{uid}_0")
        )
        
        caption = f"💰 <b>ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ ʀᴇǫᴜᴇsᴛ</b>\n👤 ᴜsᴇʀ: {message.from_user.first_name} ({uid})\n🎫 ᴘʟᴀɴ: {credits} ᴄʀᴇᴅɪᴛs"
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="HTML", reply_markup=markup)
        

# --- CORE FUNCTIONS ---
def claim_bonus(message):
    settings = load_db(SETTING_FILE)
    bonus_amt = settings.get("current_bonus", 0)
    channel_link = "https://t.me/detorlab"
    
    if bonus_amt <= 0:
        no_bonus_text = (
            "<b>🎁 Bonus Status: Inactive</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "There are no active bonuses available at the moment.\n\n"
            "📢 <b>Update:</b> Check our official channel for promo codes and credit giveaways.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📡 <b>Channel:</b> <a href='{channel_link}'>Detor Lab</a>"
        )
        return bot.send_message(message.chat.id, no_bonus_text, parse_mode="HTML", disable_web_page_preview=True)
    
    # Registration Safety Check added to prevent KeyError
    get_user(message.from_user.id, message.from_user.first_name)
    db = load_db(DB_FILE)
    uid = str(message.from_user.id)
    current_time = time.time()
    
    if current_time - db[uid].get('last_bonus', 0) > 86400:
        db[uid]['credits'] += bonus_amt
        db[uid]['last_bonus'] = current_time
        save_db(DB_FILE, db)
        bot.reply_to(message, f"✅ <b>Success!</b> {bonus_amt} credits have been added to your balance.", parse_mode="HTML")
    else:
        bot.reply_to(message, "❌ <b>Limit Exceeded:</b> You have already claimed your daily bonus. Please return in 24 hours.", parse_mode="HTML")

def process_redeem(message, code):
    cp_db = load_db(CP_FILE)
    user_db = load_db(DB_FILE)
    uid = str(message.from_user.id)
    code = code.upper().strip()
    
    if code in cp_db:
        cp = cp_db[code]
        if uid in cp['users']: bot.reply_to(message, "❌ Already claimed.")
        elif cp['uses'] <= 0: bot.reply_to(message, "❌ Expired.")
        else:
            cp['uses'] -= 1
            cp['users'].append(uid)
            user_db[uid]['credits'] += cp['amount']
            save_db(CP_FILE, cp_db); save_db(DB_FILE, user_db)
            bot.reply_to(message, f"✅ Success! {cp['amount']} credits added.")
    else: bot.reply_to(message, "❌ Invalid Coupon.")

def process_lookup(message, num):
    uid = str(message.from_user.id)
    u_name = message.from_user.first_name
    db = load_db(DB_FILE)
    u = db[uid]
    channel_link = "https://t.me/detorlab"

    if u['credits'] <= 0 and not u['is_vip']: 
        # 1. Pehle button banayein
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 ʙᴜʏ ᴄʀᴇᴅɪᴛs", callback_data="buy_credits"))
        no_credit_msg = (
            "<b>⚠️ Access Denied!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Your account has <b>0 Credits</b> remaining.\n\n"
            "<b>Refill Options:</b>\n"
            "1. 💰 Claim daily rewards via <b>Bonus</b>.\n"
            "2. 🎟 Use a <b>Redeem</b> code from our channel.\n"
            "3. 👨‍💻 Contact the administrator for top-up.\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📡 <b>Official:</b> <a href='{channel_link}'>Detor Lab</a>"
        )
        return bot.send_message(message.chat.id, no_credit_msg, parse_mode="HTML", disable_web_page_preview=True,reply_markup=markup)

    wait = bot.send_message(message.chat.id, "🔍 Searching in Global Database...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(f"{API_BASE_URL}{num}", headers=headers, timeout=20)
        res = response.json()
        
        if res.get("status") == True or str(res.get("status")).lower() == "true":
            results = res.get("results", [])
            if results:
                if not u['is_vip']: db[uid]['credits'] -= 1
                db[uid]['total_search'] += 1
                save_db(DB_FILE, db)

                for item in results:
                    target_name = item.get('NAME', 'N/A')
                    hist = load_db(HIST_FILE)
                    if "logs" not in hist: hist["logs"] = []
                    hist["logs"].append(f"{datetime.now().strftime('%d/%m %H:%M')} | {uid} | {u_name} | searched {num} ({target_name})")
                    save_db(HIST_FILE, hist)

                    output = (
                        f"👤 <b>REAL NAME:</b> <code>{target_name}</code>\n"
                        f"👨 <b>FATHER NAME:</b> <code>{item.get('fname', 'N/A')}</code>\n"
                        f"🆔 <b>ADHAAR ID:</b> <code>[Redacted]</code>\n"
                        f"📱 <b>PRIMARY:</b> <code>{item.get('MOBILE', num)}</code>\n"
                        f"📞 <b>ALTERNATE:</b> <code>{item.get('alt', 'N/A')}</code>\n"
                        f"📧 <b>EMAIL:</b> <code>{item.get('EMAIL', 'N/A')}</code>\n"
                        f"📍 <b>CIRCLE/SIM:</b> <code>{item.get('circle', 'N/A')}</code>\n"
                        f"🏠 <b>ADDRESS:</b> <code>{item.get('ADDRESS', 'N/A')}</code>\n\n"
                        f"✨ <b>Powered by: {OWNER_USERNAME}</b>"
                    )
                    bot.send_message(message.chat.id, output, parse_mode="HTML")
                bot.delete_message(message.chat.id, wait.message_id)
            else: bot.edit_message_text("❌ No records found.", message.chat.id, wait.message_id)
        else: bot.edit_message_text("❌ API Error.", message.chat.id, wait.message_id)
    except: bot.edit_message_text("⚠️ Connection Error.", message.chat.id, wait.message_id)

# --- ADMIN PANEL ---
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
        hist_data = load_db(HIST_FILE).get("logs", [])
        if not hist_data: return bot.send_message(call.message.chat.id, "Empty History.")
        res = "📜 <b>LATEST SEARCH LOGS</b>\n━━━━━━━━━━━━━━\n"
        for entry in reversed(hist_data[-10:]):
            try:
                p = entry.split(" | ")
                user_lnk = f"<a href='tg://user?id={p[1]}'>{p[2]}</a>"
                res += f"🕒 <code>{p[0]}</code>\n👤 {user_lnk}\n➔ {p[3].replace('searched', '🔍')}\n\n"
            except: res += f"• {entry}\n\n"
        bot.send_message(call.message.chat.id, res + "━━━━━━━━━━━━━━", parse_mode="HTML")

    elif call.data == "adm_stats":
        db = load_db(DB_FILE)
        cp = load_db(CP_FILE)
        total_searches = sum(u.get('total_search', 0) for u in db.values())
        stats_msg = (
            "📊 <b>DETOR SYSTEM STATS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Total Users:</b> <code>{len(db)}</code>\n"
            f"👑 <b>VIP Members:</b> <code>{sum(1 for u in db.values() if u.get('is_vip'))}</code>\n"
            f"🔍 <b>Total Queries:</b> <code>{total_searches}</code>\n"
            f"🎟 <b>Active Coupons:</b> <code>{len(cp)}</code>\n━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>Status:</b> <code>Online</code>"
        )
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="HTML")

# --- ADMIN STEP HANDLERS ---
def admin_add_credit(message):
    try:
        tid, amt = message.text.split()
        db = load_db(DB_FILE)
        if tid in db:
            db[tid]['credits'] += int(amt)
            save_db(DB_FILE, db)
            bot.reply_to(message, f"✅ Added {amt} credits.")
    except: bot.reply_to(message, "❌ Error.")

def admin_add_vip(message):
    try:
        tid = message.text.strip()
        db = load_db(DB_FILE)
        if tid in db:
            db[tid]['is_vip'] = True
            save_db(DB_FILE, db)
            bot.reply_to(message, f"👑 {tid} is VIP.")
    except: bot.reply_to(message, "❌ Error.")

def admin_gen_coupon(message):
    try:
        code, amt, uses = message.text.split()
        cp = load_db(CP_FILE)
        cp[code.upper()] = {"amount": int(amt), "uses": int(uses), "users": []}
        save_db(CP_FILE, cp)
        bot.reply_to(message, f"🎟 Coupon {code.upper()} Created.")
    except: bot.reply_to(message, "❌ Error.")

def admin_set_bonus(message):
    if not message.text.isdigit(): return
    st = load_db(SETTING_FILE)
    st['current_bonus'] = int(message.text)
    save_db(SETTING_FILE, st)
    bot.reply_to(message, "💰 Bonus Updated.")

print("Bot is flying...")
bot.infinity_polling()
