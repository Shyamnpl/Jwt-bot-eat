from flask import Flask, request
import threading

# Flask app for webhook
flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return 'OK', 200

@flask_app.route('/')
def index():
    return "Bot is running!", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

def main():
    """Start the bot"""
    # ✅ FIX: Create and set event loop properly
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except RuntimeError:
        # Loop already exists
        pass
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start bot
    print("🤖 Bot is starting... Press Ctrl+C to stop")
    print("👨‍💻 Developer: @ShamNpl")
    print("📢 Channel: @FFbotsALL")
    print("🌍 From Nepal 🇳🇵")
    
    # ✅ FIX: Use run_polling with proper arguments
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Set webhook
    webhook_url = "https://your-app.onrender.com/webhook"
    asyncio.run(application.bot.set_webhook(webhook_url))
    
    # Run Flask in a thread
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Keep main thread alive
    while True:
        import time
        time.sleep(60)