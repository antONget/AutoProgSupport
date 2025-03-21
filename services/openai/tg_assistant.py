import os
import openai
import time
from config_data.config import load_config, Config
config: Config = load_config()


# from telegram import Update
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

OPENAI_API_KEY = config.tg_bot.api_key_openai
ASSISTANT_ID = config.tg_bot.assistant_id
TELEGRAM_BOT_TOKEN = config.tg_bot.token

# Проверка наличия API-ключей
if not OPENAI_API_KEY or not ASSISTANT_ID or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Ошибка: Не указаны ключи API в .env файле!")

# Создаем OpenAI клиент
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Глобальный словарь для хранения нити беседы для каждого пользователя
user_threads = {}


def create_or_get_thread(user_id):
    """Создает новую нить для пользователя или использует существующую"""
    if user_id not in user_threads:
        thread = client.beta.threads.create()
        user_threads[user_id] = thread.id
    return user_threads[user_id]


def send_message_to_openai(user_id, user_input):
    """Отправляет сообщение в OpenAI и получает ответ"""
    thread_id = create_or_get_thread(user_id)

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # Запускаем ассистента
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)

    # Ожидание ответа
    start_time = time.time()
    while time.time() - start_time < 30:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == "completed":
            break

    # Получение ответа ассистента
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    if messages.data:
        return messages.data[0].content[0].text.value
    return "Ошибка: Нет ответа от ассистента."


# def start(update: Update, context: CallbackContext):
#     """Приветственное сообщение"""
#     update.message.reply_text("🤖 Привет! Я твой AI-ассистент. Просто напиши мне вопрос!")


# def handle_message(update: Update, context: CallbackContext):
#     """Обрабатывает входящие сообщения"""
#     user_id = update.message.chat_id
#     user_input = update.message.text
#
#     update.message.reply_text("⏳ Думаю...")
#
#     try:
#         response = send_message_to_openai(user_id, user_input)
#         update.message.reply_text(response)
#     except Exception as e:
#         update.message.reply_text(f"Ошибка: {e}")


# def main():
#     """Запуск бота"""
#     updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
#     dp = updater.dispatcher
#
#     dp.add_handler(CommandHandler("start", start))
#     dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
#
#     updater.start_polling()
#     updater.idle()
#
#
# if __name__ == "__main__":
#     main()