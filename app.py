#!/usr/bin/env python3
"""
Free Fire Token Bot - Premium Version (API Based)
Developer: @ShamNpl
Channel: @FFbotsALL
Country: Nepal 🇳🇵
"""

import logging
import httpx
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask, request
import threading
import time

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8792414945:AAHRGCQinm2LebmPIoCNHIw8CJ67QZraLTU"
PORT = int(os.environ.get('PORT', 8080))  # Render assigns PORT automatically

# API Endpoints
EAT_API_URL = "https://eat-access-eight.vercel.app/Eat"
JWT_API_URL = "https://access-jwt-delta.vercel.app/access-jwt"

# User session storage
user_sessions = {}

# Flask app for health checks and port binding
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return """
    <h1>🤖 Free Fire Token Bot is Running!</h1>
    <p>Developer: @ShamNpl</p>
    <p>Channel: @FFbotsALL</p>
    <p>Status: ✅ Active</p>
    <p>Uptime: Bot is running 24/7</p>
    """

@flask_app.route('/health')
def health():
    return {"status": "healthy", "timestamp": time.time()}

@flask_app.route('/ping')
def ping():
    return "pong"

def run_flask():
    """Run Flask server in a separate thread"""
    flask_app.run(host='0.0.0.0', port=PORT)

# ==================== API Functions ====================

async def call_eat_api(eat_token: str):
    """Call Eat token API and return formatted data"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = f"{EAT_API_URL}?eat_token={eat_token}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "account_id": data.get("account_id"),
                        "account_nickname": data.get("account_nickname"),
                        "open_id": data.get("open_id"),
                        "access_token": data.get("access_token"),
                        "region": data.get("region", "N/A")
                    }
                else:
                    return {"success": False, "error": "Invalid response from API"}
            else:
                return {"success": False, "error": f"API returned status {response.status_code}"}
                
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

async def call_jwt_api(access_token: str):
    """Call JWT API and return formatted data"""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            url = f"{JWT_API_URL}?access_token={access_token}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "access_token": data.get("access_token"),
                        "account_id": data.get("account_id"),
                        "account_name": data.get("account_name"),
                        "open_id": data.get("open_id"),
                        "platform": data.get("platform"),
                        "region": data.get("region", "N/A"),
                        "token": data.get("token")
                    }
                else:
                    return {"success": False, "error": "Invalid response from API"}
            else:
                return {"success": False, "error": f"API returned status {response.status_code}"}
                
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

# ==================== Telegram Bot Handlers ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with inline buttons"""
    welcome_text = (
        "🌟 *Welcome to Free Fire Token Bot* 🌟\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Premium Token Converter* ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 *Eat-Access_token* → Convert Eat Token to Access Token\n"
        "🔹 *Access-JWT* → Convert Access Token to JWT Token\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👤 *Your Information:*\n"
        "├ 🆔 User ID: `{}`\n"
        "├ 👤 Name: {}\n"
        "└ 🌍 Country: Nepal 🇳🇵\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚡ *Select an option below to get started!*"
    ).format(update.effective_user.id, update.effective_user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("🍽️ Eat-Access_token", callback_data="eat_token"),
            InlineKeyboardButton("🔑 Access-JWT", callback_data="access_jwt")
        ],
        [
            InlineKeyboardButton("📋 About", callback_data="about"),
            InlineKeyboardButton("🆘 Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "eat_token":
        user_sessions[user_id] = {"mode": "eat_token"}
        await query.edit_message_text(
            "🍽️ *Eat Token Converter Selected*\n\n"
            "Please send me your *Eat Token* to process.\n\n"
            "📝 *Example:*\n"
            "`c706668ccafb90b670beda197f73eca9e280dbe1f8dc69edc9fa91cf1d6e7c44ebbe5d4e4cc8eadca82c281c8bb0cd43090d6b5b60b2ee43a9cf5522f938f3afb55d1c74e23484d17fd3a5299609b16a`\n\n"
            "⏳ I'll process it and return your Access Token!",
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data == "access_jwt":
        user_sessions[user_id] = {"mode": "access_jwt"}
        await query.edit_message_text(
            "🔑 *Access-JWT Converter Selected*\n\n"
            "Please send me your *Access Token* to convert to JWT.\n\n"
            "📝 *Example:*\n"
            "`b5fabb1abcff70dda15561530e69291d4e0effda5e87f0b27f06bed053981605`\n\n"
            "⏳ I'll process it and return your JWT Token!",
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data == "about":
        about_text = (
            "📌 *About This Bot*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🤖 *Free Fire Token Converter*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ *Features:*\n"
            "├ 🍽️ Eat Token → Access Token\n"
            "├ 🔑 Access Token → JWT Token\n"
            "├ ⚡ Fast Cloud Processing\n"
            "├ 🔒 Secure API Based\n"
            "└ 🆓 100% Free\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👨‍💻 *Developer Information:*\n"
            "├ 📝 Username: @ShamNpl\n"
            "├ 📢 Channel: @FFbotsALL\n"
            "├ 🌍 Country: Nepal 🇳🇵\n"
            "└ 💻 Professional Developer\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ *Version:* 3.0 (Cloud API)\n"
            "📅 *Last Updated:* 2026"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(about_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    elif query.data == "help":
        help_text = (
            "🆘 *Help & Support*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📖 *How to Use:*\n\n"
            "1️⃣ *Eat-Access_token*\n"
            "   • Click the 🍽️ Eat Token button\n"
            "   • Paste your Eat Token\n"
            "   • Get Access Token instantly\n\n"
            "2️⃣ *Access-JWT*\n"
            "   • Click the 🔑 Access-JWT button\n"
            "   • Paste your Access Token\n"
            "   • Get JWT Token instantly\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "❓ *Need Help?*\n"
            "Contact: @ShamNpl\n"
            "Channel: @FFbotsALL\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

    elif query.data == "back_to_menu":
        welcome_text = (
            "🌟 *Welcome Back to Free Fire Token Bot* 🌟\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ *Premium Token Converter* ✨\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔹 *Eat-Access_token* → Convert Eat Token to Access Token\n"
            "🔹 *Access-JWT* → Convert Access Token to JWT Token\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 *Your Information:*\n"
            "├ 🆔 User ID: `{}`\n"
            "├ 👤 Name: {}\n"
            "└ 🌍 Country: Nepal 🇳🇵\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚡ *Select an option below to get started!*"
        ).format(query.from_user.id, query.from_user.first_name)

        keyboard = [
            [
                InlineKeyboardButton("🍽️ Eat-Access_token", callback_data="eat_token"),
                InlineKeyboardButton("🔑 Access-JWT", callback_data="access_jwt")
            ],
            [
                InlineKeyboardButton("📋 About", callback_data="about"),
                InlineKeyboardButton("🆘 Help", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages based on selected mode"""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()

    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ *Please select an option first!*\n\nUse /start to see the menu.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    mode = user_sessions[user_id].get("mode")

    if mode == "eat_token":
        # Processing message
        processing_msg = await update.message.reply_text(
            "🔄 *Processing your Eat Token...*\n\n"
            "⏳ Calling API...\n"
            "🔍 Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Call Eat API
        result = await call_eat_api(user_input)

        if not result.get("success"):
            error_text = (
                f"❌ *Error:* {result.get('error', 'Unknown error')}\n\n"
                "📝 *Please check:*\n"
                "├ Token is valid and not expired\n"
                "├ Try again later\n"
                "└ Contact @ShamNpl for support"
            )
            await processing_msg.edit_text(error_text, parse_mode=ParseMode.MARKDOWN)
        else:
            success_text = (
                "✅ *Eat Token Converted Successfully!*\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 *Account Details:*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👤 *User Information:*\n"
                f"├ 🆔 Account ID: `{result['account_id']}`\n"
                f"├ 📝 Nickname: `{result['account_nickname']}`\n"
                f"└ 🌍 Region: `{result['region']}`\n\n"
                "🔑 *Access Token (Tap to copy):*\n"
                f"`{result['access_token']}`\n\n"
                "🆔 *Open ID (Tap to copy):*\n"
                f"`{result['open_id']}`\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "✨ *Tokens are copyable - just tap on them!*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👨‍💻 Developer: @ShamNpl\n"
                "📢 Channel: @FFbotsALL\n"
                "🌍 From Nepal 🇳🇵"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Convert Another Eat Token", callback_data="eat_token")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await processing_msg.edit_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

    elif mode == "access_jwt":
        # Processing message
        processing_msg = await update.message.reply_text(
            "🔄 *Processing your Access Token...*\n\n"
            "⏳ Calling JWT API...\n"
            "🔍 Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Call JWT API
        result = await call_jwt_api(user_input)

        if not result.get("success"):
            error_text = (
                f"❌ *Error:* {result.get('error', 'Unknown error')}\n\n"
                "📝 *Please check:*\n"
                "├ Token is valid and not expired\n"
                "├ Try again later\n"
                "└ Contact @ShamNpl for support"
            )
            await processing_msg.edit_text(error_text, parse_mode=ParseMode.MARKDOWN)
        else:
            success_text = (
                "✅ *Access Token Converted to JWT Successfully!*\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "📋 *Account Details:*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👤 *User Information:*\n"
                f"├ 🆔 Account ID: `{result['account_id']}`\n"
                f"├ 📝 Name: `{result['account_name']}`\n"
                f"├ 🔗 Platform: `{result['platform']}`\n"
                f"└ 🌍 Region: `{result['region']}`\n\n"
                "🔑 *Access Token (Tap to copy):*\n"
                f"`{result['access_token']}`\n\n"
                "🎫 *JWT Token (Tap to copy):*\n"
                f"`{result['token']}`\n\n"
                "🆔 *Open ID (Tap to copy):*\n"
                f"`{result['open_id']}`\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "✨ *All tokens are copyable - just tap on them!*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👨‍💻 Developer: @ShamNpl\n"
                "📢 Channel: @FFbotsALL\n"
                "🌍 From Nepal 🇳🇵"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Convert Another Access Token", callback_data="access_jwt")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await processing_msg.edit_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

    # Clear session after processing
    if user_id in user_sessions:
        del user_sessions[user_id]

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ *An error occurred!*\n\n"
                "Please try again later or contact @ShamNpl for support.\n"
                "Join @FFbotsALL for updates!",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

def run_bot():
    """Run the Telegram bot"""
    # Create and set event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except RuntimeError:
        pass
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start bot
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Free Fire Token Bot")
    print("👨‍💻 Developer: @ShamNpl")
    print("📢 Channel: @FFbotsALL")
    print("🌍 From Nepal 🇳🇵")
    print("=" * 50)
    
    # Start Flask in a separate thread for port binding
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"✅ Web server started on port {PORT}")
    
    # Run the bot in the main thread
    run_bot()