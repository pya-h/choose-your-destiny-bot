from vector_database import CassandraDatabase
import time
from controller import GameController
from decouple import config
from telegram import *
from telegram.ext import *


open_ai_api_key = config('OPENAI_API_KEY')
token_json_path = config('TOKEN_JSON_PATH')
bundle_zip_path = config('BUNDLE_ZIP_PATH')
astra_db_keyspace = config('ASTRA_DB_KEYSPACE')
BOT_TOKEN = config('BOT_TOKEN')

database = CassandraDatabase(token=token_json_path, bundle=bundle_zip_path, astra_db_keyspace=astra_db_keyspace)
games = dict()

async def cmd_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not chat_id in games:
        result = database.connect(chat_id=chat_id)
        game = GameController(memory=database.chats_history, openai_api_key=open_ai_api_key)

async def handle_messages(update: Update, context: CallbackContext):
    if update and update.message:
        msg = update.message.text
        chat_id = update.effective_chat.id
        if chat_id in games and chat_id in CassandraDatabase.Conversations:
            response, is_game_ended = games[chat_id].react(msg)
            if is_game_ended:
                del games[chat_id]
                del CassandraDatabase.Conversations[chat_id]
            await update.message.reply_text(msg + "\n\nWhat do you do?")
        else:
            await update.message.reply_text('You haven\'t started any game yet. Press /start')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))

    # app.add_handler(MessageHandler(filters.ALL, handle_messages))
    app.add_handler(CallbackQueryHandler(handle_inline_keyboard_callbacks))

    print("Server is up and running...")
    # print(WEBHOOK_URL, WEBHOOK_PORT)
    app.run_polling(poll_interval=1, timeout=50)
    # app.run_webhook(listen="0.0.0.0", port=WEBHOOK_PORT, webhook_url=f"{WEBHOOK_URL}", stop_signals=None)

if __name__ == '__main__':
    main()
