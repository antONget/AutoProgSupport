import openai
import os
import time
from config_data.config import load_config, Config
config: Config = load_config()
# 🔑 Вставь сюда свой API-ключ
API_KEY = config.tg_bot.api_key_openai
# 🆔 Вставь ID твоего ассистента
ASSISTANT_ID = "asst_Td9iMeRH6MwhAKLgRGAt1PPs"
if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Ошибка: API-ключ или ID ассистента не указаны!")

# Глобальная переменная для хранения ID нити
thread_id = None


def create_or_get_thread(client):
    """Создает новую нить или использует существующую"""
    global thread_id
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id  # Сохраняем ID
    return thread_id


def send_message(client, user_input):
    """Отправляет сообщение ассистенту в существующую нить"""
    thread_id = create_or_get_thread(client)
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )


def wait_for_response(client, thread_id, run_id, timeout=30):
    """Ожидает ответа от ассистента"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            return run
    raise TimeoutError("Ошибка: Ассистент не ответил вовремя!")


def get_assistant_response(client, thread_id):
    """Получает последние сообщения ассистента"""
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    if messages.data:
        # Берем последние несколько сообщений для контекста
        return "\n".join([msg.content[0].text.value for msg in reversed(messages.data[:5])])

    return "Ошибка: Нет ответа от ассистента."


def chat_with_assistant():
    """Основная функция диалога"""
    client = openai.OpenAI(api_key=API_KEY)

    print("🤖 GPT-ассистент активирован! Введите 'exit' для выхода.")

    while True:
        user_input = input("Вы: ")
        if user_input.lower() == "exit":
            print("🚪 Выход из чата...")
            break

        thread_id = create_or_get_thread(client)
        send_message(client, user_input)

        # Запускаем выполнение запроса
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)

        try:
            wait_for_response(client, thread_id, run.id)
            response = get_assistant_response(client, thread_id)
            print("GPT:", response)
        except TimeoutError as e:
            print(e)


if __name__ == "__main__":
    chat_with_assistant()