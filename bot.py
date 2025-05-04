import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

# استرداد التوكن ومعرف الإداري من المتغيرات البيئية
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# إعداد البوت
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# دالة الترحيب عند بدء البوت
def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="مرحبًا! أنا بوت Ehsas. كيف يمكنني مساعدتك؟")

# دالة لإرسال الرسائل إلى الإداري
def forward_to_admin(update, context):
    user_message = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"رسالة جديدة من {user_name} (ID: {user_id}):\n{user_message}")

# دالة للرد على الأوامر غير المعروفة
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="عذرًا، لم أفهم هذا الأمر.")

# إضافة المعالجات
start_handler = CommandHandler('start', start)
forward_handler = MessageHandler(Filters.text & (~Filters.command), forward_to_admin)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(forward_handler)
dispatcher.add_handler(unknown_handler)

# بدء البوت
updater.start_polling()
updater.idle()
