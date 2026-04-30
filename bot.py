import telebot
from telebot import types
import requests
import json
import os
import random
from datetime import datetime
from gtts import gTTS
import threading
import time

TOKEN = "8700350848:AAFjCmHteNFx2EldRGxtvEXfaRWxS9RsIk4"
ADMINS = [8271084626, 8665885943]

bot = telebot.TeleBot(TOKEN)

# لیست ری‌اکشن‌ها
REACTIONS = ["🔥", "👾", "🎃"]

# ========== دکمه‌های رنگی ==========
def send_colored(chat_id, text, keyboard_data):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": keyboard_data}
    requests.post(url, json=payload, timeout=10)

def edit_colored(chat_id, msg_id, text, keyboard_data):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown", "reply_markup": keyboard_data}
    requests.post(url, json=payload, timeout=10)

def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "🎤 تبدیل متن به ویس", "callback_data": "voice", "style": "success"}, {"text": "📊 اطلاعات کاربر", "callback_data": "info", "style": "primary"}],
            [{"text": "📞 پشتیبانی", "callback_data": "support", "style": "primary"}, {"text": "⚙️ پنل ادمین", "callback_data": "admin", "style": "danger"}]
        ]
    }

def back_btn():
    return {"inline_keyboard": [[{"text": "🔙 بازگشت", "callback_data": "back", "style": "danger"}]]}

# ========== ری‌اکشن خودکار ==========
def send_reaction(chat_id, message_id):
    time.sleep(0.3)
    try:
        reaction = random.choice(REACTIONS)
        url = f"https://api.telegram.org/bot{TOKEN}/setMessageReaction"
        payload = {"chat_id": chat_id, "message_id": message_id, "reaction": [{"type": "emoji", "emoji": reaction}]}
        requests.post(url, json=payload, timeout=5)
    except:
        pass

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_all_messages(msg):
    if not msg.from_user.is_bot:
        threading.Thread(target=send_reaction, args=(msg.chat.id, msg.message_id)).start()
        if msg.text.startswith('/start'):
            start(msg)

# ========== START ==========
@bot.message_handler(commands=['start'])
def start(msg):
    text = "✨ **به ربات تست خوش آمدی!** ✨\n\nاز دکمه‌های زیر استفاده کن:"
    send_colored(msg.chat.id, text, main_menu())

# ========== تبدیل متن به ویس ==========
@bot.callback_query_handler(func=lambda call: call.data == "voice")
def voice_menu(call):
    bot.answer_callback_query(call.id, "🎤 لطفاً متن خود را بفرست:", show_alert=True)
    msg = bot.send_message(call.message.chat.id, "🎤 **لطفاً متنی که می‌خوای به ویس تبدیل بشه رو بفرست:**\n\n💡 متن باید به فارسی باشد.", parse_mode="Markdown")
    bot.register_next_step_handler(msg, convert_to_voice)

def convert_to_voice(msg):
    text = msg.text
    if len(text) > 200:
        bot.reply_to(msg, "❌ متن خیلی بلنده! حداکثر ۲۰۰ کاراکتر مجاز است.")
        return
    try:
        tts = gTTS(text=text, lang="fa")
        tts.save("voice.mp3")
        with open("voice.mp3", "rb") as audio:
            bot.send_voice(msg.chat.id, audio, caption=f"🎤 **ویس شما:**\n{text[:100]}", parse_mode="Markdown")
        os.remove("voice.mp3")
    except:
        bot.reply_to(msg, "❌ خطا در تبدیل متن به ویس!")

# ========== اطلاعات کاربر ==========
@bot.callback_query_handler(func=lambda call: call.data == "info")
def user_info(call):
    user = call.from_user
    now = datetime.now()
    text = f"""📊 **اطلاعات کاربر**

🆔 **ایدی عددی:** `{user.id}`
👤 **نام:** {user.first_name}
🔗 **یوزرنیم:** @{user.username if user.username else 'ندارد'}
📅 **تاریخ امروز:** {now.strftime('%Y/%m/%d')}
🕐 **ساعت:** {now.strftime('%H:%M:%S')}

🔹 از دکمه بازگشت استفاده کن."""
    send_colored(call.message.chat.id, text, back_btn())
    bot.delete_message(call.message.chat.id, call.message.id)

# ========== پشتیبانی ==========
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    text = "📞 **پشتیبانی**\n\n🆔 @Xiisas3\n⏰ ۲۴ ساعته"
    send_colored(call.message.chat.id, text, back_btn())
    bot.delete_message(call.message.chat.id, call.message.id)

# ========== پنل ادمین ==========
@bot.callback_query_handler(func=lambda call: call.data == "admin")
def admin(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    text = "⚙️ **پنل ادمین**\n\n📊 **آمار ربات:**\n🔹 در حال توسعه..."
    send_colored(call.message.chat.id, text, back_btn())
    bot.delete_message(call.message.chat.id, call.message.id)

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    send_colored(call.message.chat.id, "✨ منوی اصلی:", main_menu())
    bot.delete_message(call.message.chat.id, call.message.id)

# ========== MAIN ==========
print("=" * 50)
print("🔥 ربات تست با قابلیت ویس + اطلاعات کاربر")
print(f"👑 ادمین‌ها: {ADMINS}")
print("=" * 50)
bot.infinity_polling()
