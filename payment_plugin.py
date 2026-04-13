import telebot
from telebot import types
import json
import os

print("🚀 Payment Plugin: Loading...")

# --- SETTINGS ---
DB_FILE = "users_data.json"
PLANS_FILE = "plans.json"
UPI_ID = "avanishpal080@oksbi" # Apni UPI id yahan dalein
QR_PATH = "my_qr.jpg" # Agar QR image hai toh uska path

def load_data(file):
    if not os.path.exists(file): return {}
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

def setup_payment_handlers(bot, ADMIN_ID):
    
    # --- ADMIN: ADD PLAN ---
    @bot.message_handler(commands=['addplan'], func=lambda m: m.from_user.id == ADMIN_ID)
    def add_plan(message):
        try:
            # Format: /addplan Name|Credits|Price
            _, data = message.text.split(" ", 1)
            name, credits, price = data.split("|")
            plans = load_data(PLANS_FILE)
            plans[name] = {"credits": int(credits), "price": price}
            save_data(PLANS_FILE, plans)
            bot.reply_to(message, f"✅ ᴘʟᴀɴ '{name}' ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!")
        except:
            bot.reply_to(message, "❌ ᴜsᴇ ғᴏʀᴍᴀᴛ: <code>/addplan Starter|10|50</code>", parse_mode="HTML")
     
         # --- ADMIN: VIEW ALL PLANS ---
    @bot.message_handler(commands=['plans'], func=lambda m: m.from_user.id == ADMIN_ID)
    def view_plans(message):
        plans = load_data(PLANS_FILE)
        if not plans:
            return bot.reply_to(message, "❌ No plans found in database.")
        
        res = "<b>📋 CURRENT ACTIVE PLANS:</b>\n──────────────────\n"
        for name, info in plans.items():
            res += f"🔹 <b>{name}</b>: {info['credits']} Cr | ₹{info['price']}\n"
        
        bot.send_message(message.chat.id, res, parse_mode="HTML")
        
    # --- USER: VIEW PLANS ---
    @bot.callback_query_handler(func=lambda call: call.data == "buy_credits")
    def show_plans(call):
        plans = load_data(PLANS_FILE)
        if not plans:
            return bot.answer_callback_query(call.id, "ɴᴏ ᴘʟᴀɴs ᴀᴠᴀɪʟᴀʙʟᴇ ʏᴇᴛ.")
        
        markup = types.InlineKeyboardMarkup()
        for name, info in plans.items():
            markup.add(types.InlineKeyboardButton(f"🎫 {name} ({info['credits']} ᴄʀ) - ₹{info['price']}", callback_data=f"pay_{name}"))
        
        bot.edit_message_text("<b>💳 sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴘᴜʀᴄʜᴀsᴇ ᴘʟᴀɴ</b>\n──────────────────", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

    # --- USER: INSTRUCTIONS ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
    def send_payment_info(call):
        plan_name = call.data.split("_")[1]
        plans = load_data(PLANS_FILE)
        plan = plans.get(plan_name)
        
        instr = (
            f"<b>✨ ᴘʟᴀɴ sᴇʟᴇᴄᴛᴇᴅ: {plan_name}</b>\n"
            f"💰 ᴀᴍᴏᴜɴᴛ ᴛᴏ ᴘᴀʏ: <b>₹{plan['price']}</b>\n"
            f"──────────────────\n"
            f"🔗 ᴜᴘɪ ɪᴅ: <code>{UPI_ID}</code>\n\n"
            f"📝 ɪɴsᴛʀᴜᴄᴛɪᴏɴs:\n"
            f"1. ᴘᴀʏ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ ᴠɪᴀ ᴀɴʏ ᴜᴘɪ ᴀᴘᴘ.\n"
            f"2. ᴛᴀᴋᴇ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴏғ ᴛʜᴇ sᴜᴄᴄᴇssғᴜʟ ᴘᴀʏᴍᴇɴᴛ.\n"
            f"3. sᴇɴᴅ ᴛʜᴇ sᴄʀᴇᴇɴsʜᴏᴛ ʜᴇʀᴇ ɴᴏᴡ.\n"
            f"──────────────────\n"
            f"⚠️ sʏsᴛᴇᴍ ɪs ᴀᴡᴀɪᴛɪɴɢ ʏᴏᴜʀ ᴘʀᴏᴏғ..."
        )
        
        # Save state so we know they are sending a screenshot for this plan
        from __main__ import user_states
        user_states[call.from_user.id] = f"sending_ss|{plan['credits']}"
        
        if os.path.exists(QR_PATH):
            with open(QR_PATH, 'rb') as qr:
                bot.send_photo(call.message.chat.id, qr, caption=instr, parse_mode="HTML")
        else:
            bot.send_message(call.message.chat.id, instr, parse_mode="HTML")

    # --- ADMIN: APPROVAL LOGIC ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
    def admin_approval(call):
        _, action, uid, credits = call.data.split("_")
        
        if action == "app": # Approve
            db = load_data(DB_FILE)
            if uid in db:
                db[uid]['credits'] += int(credits)
                save_data(DB_FILE, db)
                bot.send_message(uid, f"✅ <b>ᴘᴀʏᴍᴇɴᴛ ᴀᴘᴘʀᴏᴠᴇᴅ!</b>\n{credits} ᴄʀᴇᴅɪᴛs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.", parse_mode="HTML")
                bot.edit_message_caption(f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ {credits} ᴄʀ for {uid}", call.message.chat.id, call.message.message_id)
        else: # Reject
            bot.send_message(uid, "❌ <b>ᴘᴀʏᴍᴇɴᴛ ʀᴇᴊᴇᴄᴛᴇᴅ!</b>\nɪɴᴠᴀʟɪᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴏʀ ғᴀɪʟᴇᴅ ᴛʀᴀɴsᴀᴄᴛɪᴏɴ.", parse_mode="HTML")
            bot.edit_message_caption(f"❌ ʀᴇᴊᴇᴄᴛᴇᴅ for {uid}", call.message.chat.id, call.message.message_id)
