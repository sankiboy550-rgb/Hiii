#!/usr/bin/env python3
# EXPLOITS LOOKUP BOT - PUBLIC VERSION
# Buy Bot: @ExploitsLookupBot
# Developer: @Cyb3rS0ldier

import os
import json
import time
import sqlite3
import requests
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ CONFIGURATION ============
BOT_TOKEN = '8791374022:AAF7VlXSJ-SVYwu3WmgV4tppBFDaPVoQ_O4'  # <-- YAHAN APNA BOT TOKEN DALO
ADMIN_ID = 6586305227
FREE_LIMIT = 1

# ============ API LINKS (EXAMPLE KE LIYE) ============
# 🔥 YAHAN APNE API LINKS DALO 🔥
# EXAMPLE: https://anishexploits.com/api/anish.php?exploits={}
# { } IS JAGAH NUMBER AA JAYEGA

API_NUMBER = 'https://example.com/api/number.php?={}'
API_AADHAAR = 'https://example.com/api/aadhaar.php?={}'
API_PINCODE = 'https://example.com/api/pincode.php?={}'
API_PAKPHONE = 'https://example.com/api/?number={}'
API_FAMILY = 'https://example.com/api/family.php?={}'
API_TELEGRAM = 'https://example.com/api/?username={}'

# ============ DATABASE SETUP ============
DB_FILE = 'bot_database.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        count INTEGER DEFAULT 0,
        join_date INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# ============ HELPER FUNCTIONS ============
def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)',
              (user_id, username, first_name, int(time.time())))
    conn.commit()
    conn.close()

def update_usage(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE users SET count = count + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_free_remaining(user_id):
    user = get_user(user_id)
    if not user:
        return FREE_LIMIT
    used = user[3] or 0
    remaining = FREE_LIMIT - used
    return remaining if remaining > 0 else 0

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    return users

def get_total_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count

# ============ API REQUEST FUNCTION ============
def api_lookup(api_type, query):
    # 🔥 YAHAN API TYPE KE HISAB SE URL SELECT HOGA
    if api_type == 'number':
        url = API_NUMBER.format(query)
    elif api_type == 'aadhaar':
        url = API_AADHAAR.format(query)
    elif api_type == 'pincode':
        url = API_PINCODE.format(query)
    elif api_type == 'pakphone':
        url = API_PAKPHONE.format(query)
    elif api_type == 'family':
        url = API_FAMILY.format(query)
    elif api_type == 'telegram':
        url = API_TELEGRAM.format(query)
    else:
        return "❌ Invalid API type"
    
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        if response.status_code == 200:
            data = response.text
            formatted = f"🔍 <b>Lookup Result for {query}</b>\n\n"
            formatted += f"<pre>{data}</pre>\n\n"
            formatted += "━━━━━━━━━━━━━━━━━━━━\n"
            formatted += "⚡ <b>Powered by: @Cyb3rS0ldier</b>\n"
            formatted += "📨 <b>Buy Bot: @ExploitsLookupBot</b>"
            return formatted
        else:
            return f"❌ API Error: {response.status_code}\n\n📨 Buy Bot: @ExploitsLookupBot"
            
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}\n\n📨 Buy Bot: @ExploitsLookupBot"

# ============ KEYBOARDS ============
def get_user_keyboard():
    keyboard = [
        [KeyboardButton("📱 NUMBER LOOKUP"), KeyboardButton("🪪 AADHAAR LOOKUP")],
        [KeyboardButton("📍 PINCODE LOOKUP"), KeyboardButton("🇵🇰 PAK PHONE")],
        [KeyboardButton("👨‍👩‍👧 FAMILY INFO"), KeyboardButton("📞 TELEGRAM LOOKUP")],
        [KeyboardButton("🎁 FREE USE"), KeyboardButton("📜 PLANS & PRICING")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("📱 NUMBER LOOKUP"), KeyboardButton("🪪 AADHAAR LOOKUP")],
        [KeyboardButton("📍 PINCODE LOOKUP"), KeyboardButton("🇵🇰 PAK PHONE")],
        [KeyboardButton("👨‍👩‍👧 FAMILY INFO"), KeyboardButton("📞 TELEGRAM LOOKUP")],
        [KeyboardButton("👥 USERS SUMMARY"), KeyboardButton("📊 STATS")],
        [KeyboardButton("📢 BROADCAST"), KeyboardButton("🎁 FREE USE")],
        [KeyboardButton("📜 PLANS & PRICING")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [[KeyboardButton("↩️ BACK")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============ COMMAND HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    add_user(chat_id, user.username, user.first_name)
    
    welcome = f"👋 <b>Welcome {user.first_name}!</b>\n\n"
    welcome += "🤖 <b>EXPLOITS LOOKUP BOT</b>\n"
    welcome += "━━━━━━━━━━━━━━━━━━━━\n"
    welcome += "✅ Multiple Lookup Services\n"
    welcome += f"✅ {FREE_LIMIT} Free Use for New Users\n"
    welcome += "✅ Fast & Accurate Results\n"
    welcome += "━━━━━━━━━━━━━━━━━━━━\n"
    welcome += "⚡ <b>Powered by: @Cyb3rS0ldier</b>\n"
    welcome += "📨 <b>Buy Bot: @ExploitsLookupBot</b>"
    
    if chat_id == ADMIN_ID:
        await update.message.reply_text(welcome + "\n\n👑 ADMIN PANEL ACTIVE", 
                                       reply_markup=get_admin_keyboard(), parse_mode='HTML')
    else:
        await update.message.reply_text(welcome, reply_markup=get_user_keyboard(), parse_mode='HTML')

async def free_use(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    remaining = get_free_remaining(chat_id)
    
    if remaining > 0:
        await update.message.reply_text(f"🎁 Free Uses Remaining: {remaining}\n\n⚡ @Cyb3rS0ldier", parse_mode='HTML')
    else:
        await plans_pricing(update, context)

async def plans_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    caption = f"<b>🚀 EXPLOITS LOOKUP BOT</b>\n"
    caption += f"<b>Developer: @Cyb3rS0ldier</b>\n\n"
    caption += "━━━━━━━━━━━━━━━━━━━━\n\n"
    caption += "<b>💎 Premium Membership Plans</b>\n"
    caption += "• ₹149 – 7 Days\n"
    caption += "• ₹199 – 15 Days\n"
    caption += "• ₹249 – 30 Days\n"
    caption += "• ₹299 – 3 Months\n"
    caption += "• ₹499 – 6 Months\n\n"
    caption += "━━━━━━━━━━━━━━━━━━━━\n\n"
    caption += "<b>💳 UPI ID:</b> <code>example@okhdfcbank</code>\n\n"
    caption += "━━━━━━━━━━━━━━━━━━━━\n\n"
    caption += f"<b>🆔 Your Chat ID:</b>\n<code>{chat_id}</code>\n\n"
    caption += "━━━━━━━━━━━━━━━━━━━━\n"
    caption += "⚡ <b>Bot by: @Cyb3rS0ldier</b>\n"
    caption += "📨 <b>Buy Bot: @ExploitsLookupBot</b>"
    
    await update.message.reply_text(caption, parse_mode='HTML')

# ============ LOOKUP HANDLERS ============
async def number_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'number'
    await update.message.reply_text("📱 Send 10 digit mobile number:\n\nExample: 9876543210", 
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

async def aadhaar_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'aadhaar'
    await update.message.reply_text("🪪 Send 12 digit Aadhaar number:\n\nExample: 718602632114",
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

async def pincode_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'pincode'
    await update.message.reply_text("📍 Send 6 digit pincode:\n\nExample: 848115",
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

async def pakphone_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'pakphone'
    await update.message.reply_text("🇵🇰 Send Pakistan phone number:\n\nExample: 923494758914",
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

async def family_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'family'
    await update.message.reply_text("👨‍👩‍👧 Send Aadhaar number for family info:\n\nExample: 962397300673",
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

async def telegram_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lookup_type'] = 'telegram'
    await update.message.reply_text("📞 Send Telegram ID or Username:\n\nExample: 7210696155 or @username",
                                   reply_markup=get_back_keyboard(), parse_mode='HTML')

# ============ PROCESS LOOKUP ============
async def process_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    
    if text == '↩️ BACK':
        if chat_id == ADMIN_ID:
            await update.message.reply_text("Back to main menu.", reply_markup=get_admin_keyboard())
        else:
            await update.message.reply_text("Back to main menu.", reply_markup=get_user_keyboard())
        context.user_data.clear()
        return
    
    lookup_type = context.user_data.get('lookup_type')
    if not lookup_type:
        return
    
    remaining = get_free_remaining(chat_id)
    
    if chat_id != ADMIN_ID and remaining <= 0:
        await update.message.reply_text("❌ No free uses left!\n\n📜 Click 'PLANS & PRICING' to see plans.\n\n📨 Buy Bot: @ExploitsLookupBot", parse_mode='HTML')
        context.user_data.clear()
        return
    
    await update.message.reply_text(f"🔍 Fetching information for {text}...", parse_mode='HTML')
    
    result = api_lookup(lookup_type, text)
    await update.message.reply_text(result, parse_mode='HTML')
    
    if chat_id != ADMIN_ID:
        update_usage(chat_id)
        new_remaining = get_free_remaining(chat_id)
        await update.message.reply_text(f"✅ Free lookup used. Remaining: {new_remaining}\n\n📨 Buy Bot: @ExploitsLookupBot", parse_mode='HTML')
    
    context.user_data.clear()

# ============ ADMIN COMMANDS ============
async def admin_users_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return
    
    total_users = get_total_users()
    summary = f"👥 <b>USER SUMMARY</b>\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
    summary += f"📊 Total Users: {total_users}\n"
    summary += f"🎁 Free Limit: {FREE_LIMIT}\n\n"
    summary += "━━━━━━━━━━━━━━━━━━━━\n"
    summary += "⚡ @Cyb3rS0ldier"
    
    await update.message.reply_text(summary, parse_mode='HTML')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return
    
    total_users = get_total_users()
    stats = f"📊 <b>BOT STATS</b>\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
    stats += f"👥 Total Users: {total_users}\n"
    stats += f"🎁 Free Limit: {FREE_LIMIT}\n"
    stats += f"🤖 Bot Status: 🟢 Active\n\n"
    stats += "━━━━━━━━━━━━━━━━━━━━\n"
    stats += "⚡ @Cyb3rS0ldier"
    
    await update.message.reply_text(stats, parse_mode='HTML')

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return
    await update.message.reply_text("📢 Send your broadcast message:", reply_markup=get_back_keyboard(), parse_mode='HTML')
    context.user_data['admin_state'] = 'broadcast'

async def admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return
    
    text = update.message.text.strip()
    admin_state = context.user_data.get('admin_state')
    
    if text == '↩️ BACK':
        await update.message.reply_text("Back to admin panel.", reply_markup=get_admin_keyboard())
        context.user_data['admin_state'] = None
        return
    
    if admin_state == 'broadcast':
        users = get_all_users()
        count = 0
        for user in users:
            try:
                await context.bot.send_message(user[0], f"📢 <b>BROADCAST</b>\n\n{text}\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ @Cyb3rS0ldier", parse_mode='HTML')
                count += 1
            except:
                pass
        await update.message.reply_text(f"✅ Broadcast sent to {count} users!", reply_markup=get_admin_keyboard(), parse_mode='HTML')
        context.user_data['admin_state'] = None

# ============ MAIN ============
def main():
    print("🤖 Starting EXPLOITS LOOKUP BOT...")
    print("⚡ Developer: @Cyb3rS0ldier")
    print("📨 Buy Bot: @ExploitsLookupBot")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.Text("📱 NUMBER LOOKUP"), number_lookup))
    app.add_handler(MessageHandler(filters.Text("🪪 AADHAAR LOOKUP"), aadhaar_lookup))
    app.add_handler(MessageHandler(filters.Text("📍 PINCODE LOOKUP"), pincode_lookup))
    app.add_handler(MessageHandler(filters.Text("🇵🇰 PAK PHONE"), pakphone_lookup))
    app.add_handler(MessageHandler(filters.Text("👨‍👩‍👧 FAMILY INFO"), family_lookup))
    app.add_handler(MessageHandler(filters.Text("📞 TELEGRAM LOOKUP"), telegram_lookup))
    app.add_handler(MessageHandler(filters.Text("🎁 FREE USE"), free_use))
    app.add_handler(MessageHandler(filters.Text("📜 PLANS & PRICING"), plans_pricing))
    
    # Admin handlers
    app.add_handler(MessageHandler(filters.Text("👥 USERS SUMMARY"), admin_users_summary))
    app.add_handler(MessageHandler(filters.Text("📊 STATS"), admin_stats))
    app.add_handler(MessageHandler(filters.Text("📢 BROADCAST"), admin_broadcast))
    
    # Process lookup
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_lookup))
    app.add_handler(MessageHandler(filters.Text("↩️ BACK"), process_lookup))
    
    # Admin process
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_process))
    
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()