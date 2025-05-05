import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
)
import os
import logging

# Enable logging (optional but good practice)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# --- Command Handlers ---
def start(update: Update, context: CallbackContext) -> int:
    """Sends a welcome message with inline buttons."""
    keyboard = [
        [InlineKeyboardButton("🌙 تفسير أحلام", callback_data='interpret')],
        [InlineKeyboardButton("📖 الرقية الشرعية", callback_data='ruqyah')],
        [InlineKeyboardButton("💬 استشارات نسائية", callback_data='consult')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Use reply_text for new message, not edit_message_text if called from /start
    update.message.reply_text(
        "مرحبًا بك في بوت Ehsas! ✨\n\n"
        "اختر أحد الأقسام التالية للمتابعة:",
        reply_markup=reply_markup
    )
    # Clear any previous section selection
    context.user_data.pop('current_section', None)
    return ConversationHandler.END # Indicate end of conversation or no state needed here

# --- Callback Query Handler ---
def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and prompts user for message."""
    query = update.callback_query
    query.answer() # Answer callback query

    section_map = {
        'interpret': '🌙 تفسير أحلام',
        'ruqyah': '📖 الرقية الشرعية',
        'consult': '💬 استشارات نسائية'
    }
    section_key = query.data
    section_name = section_map.get(section_key)

    if section_name:
        context.user_data['current_section'] = section_name
        # Edit the message the button was attached to
        query.edit_message_text(text=f"لقد اخترت قسم: {section_name}\n\n"
                                     f"الرجاء إرسال رسالتك/حلمك/استشارتك الآن.")
    else:
        query.edit_message_text(text="حدث خطأ. الرجاء المحاولة مرة أخرى بالضغط على /start.")
        context.user_data.pop('current_section', None) # Clear section if error

# --- Message Handler ---
def forward_message(update: Update, context: CallbackContext) -> None:
    """Forwards user message to admin, including section if selected."""
    user_message = update.message.text
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
    username_mention = f"@{user.username}" if user.username else "لا يوجد"

    section = context.user_data.get('current_section')

    if section:
        admin_message = (
            f"📬 رسالة جديدة في قسم: {section}\n\n"
            f"👤 من: {user_name}\n"
            f"🆔 ID: {user_id}\n"
            f"🔗 اسم المستخدم: {username_mention}\n\n"
            f"📜 الرسالة:\n{user_message}"
        )
        try:
            context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
            update.message.reply_text("✅ تم إرسال رسالتك بنجاح. سيتم التواصل معك قريبًا إن شاء الله.")
            logger.info(f"Forwarded message from {user_id} in section {section}")
        except Exception as e:
            logger.error(f"Failed to forward message to admin {ADMIN_CHAT_ID}: {e}")
            update.message.reply_text("حدث خطأ أثناء إرسال رسالتك. الرجاء المحاولة مرة أخرى لاحقًا.")
        finally:
            context.user_data.pop('current_section', None) # Clear section after attempting to send
    else:
        # If user sends text without selecting a section via button
        update.message.reply_text("الرجاء اختيار أحد الأقسام أولاً باستخدام الأمر /start ثم إرسال رسالتك.")


# --- Unknown Command Handler ---
def unknown(update: Update, context: CallbackContext) -> None:
    """Handles unknown commands."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="عذرًا، لم أفهم هذا الأمر. استخدم /start للبدء.")

def main() -> None:
    """Run the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set.")
        return
    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID environment variable not set.")
        return
    else:
        try:
            # Try converting to int to ensure it's a valid ID
            int(ADMIN_CHAT_ID)
        except ValueError:
            logger.error(f"ADMIN_CHAT_ID is not a valid integer: {ADMIN_CHAT_ID}")
            return

    # Create the Updater and pass it your bot's token.
    updater = Updater(token=BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button)) # Handles button clicks
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), forward_message)) # Handles text messages after button click
    dispatcher.add_handler(MessageHandler(Filters.command, unknown)) # Handles unknown commands

    # Start the Bot
    logger.info("Starting bot polling...")
    updater.start_polling()

    # Keep the bot running until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()

