import logging
import sqlite3
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
BOT_TOKEN = ""
WEB_APP_URL = "telegram-mini-app-ten-red.vercel.app"  # Your hosted web app URL
CPAGRIP_LINK = "https://www.cpagrip.com/offer.php?offer_id=12345&user_id={user_id}"

# --- Setup Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('user_wallets.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            coins INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect('user_wallets.db')
    cur = conn.cursor()
    cur.execute('SELECT user_id, username, first_name, coins FROM users WHERE user_id = ?', (user_id,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        return {
            'user_id': result[0],
            'username': result[1],
            'first_name': result[2],
            'coins': result[3]
        }
    return None

def update_user_coins(user_id, username, first_name, amount, description=""):
    conn = sqlite3.connect('user_wallets.db')
    cur = conn.cursor()
    
    # Insert or update user
    cur.execute('''
        INSERT INTO users (user_id, username, first_name, coins)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
            username = excluded.username,
            first_name = excluded.first_name,
            coins = coins + excluded.coins
    ''', (user_id, username, first_name, amount))
    
    # Record transaction
    cur.execute('''
        INSERT INTO transactions (user_id, amount, description)
        VALUES (?, ?, ?)
    ''', (user_id, amount, description))
    
    conn.commit()
    conn.close()

# --- Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message with Web App button"""
    user = update.effective_user
    update_user_coins(user.id, user.username, user.first_name, 0, "Initial registration")
    
    keyboard = [
        [InlineKeyboardButton(
            "🚀 Open Earn App", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! 🎉",
        reply_markup=reply_markup
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from Web App"""
    user = update.effective_user
    data = json.loads(update.effective_message.web_app_data.data)
    
    if data.get('type') == 'complete_offer':
        reward = data.get('reward', 0)
        offer_id = data.get('offer_id')
        
        update_user_coins(
            user.id, 
            user.username, 
            user.first_name, 
            reward, 
            f"Completed offer {offer_id}"
        )
        
        # Send confirmation back to user
        await update.message.reply_text(
            f"✅ You earned {reward} coins! Your offer has been processed."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user = update.effective_user
    
    keyboard = [[InlineKeyboardButton(
        "🚀 Open Earn App", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Tap the button below to open the earning app!",
        reply_markup=reply_markup
    )

# --- Main Application ---
def main():
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(CallbackQueryHandler(lambda u, c: None))  # Placeholder

    print("Mini App Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
