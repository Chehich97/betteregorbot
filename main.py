import logging
import random
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiohttp import web

TOKEN = '7864799152:AAFlvHkSkK2Sap5_9B0G_ITltfvm2MbNVZY'  # Ваш токен сосал

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

# ID пользователя, на сообщения которого будет реагировать бот
TARGET_EGOR_ID = 484494756
RESPONSE_PROBABILITY_INSULT = 0.05
TARGET_KLIM_ID = 648321861
GIF_URL = "https://media1.tenor.com/m/Ws2SCL9HpZUAAAAd/ah-here-you-are-phoebe-dynevor.gif"
RESPONSE_PROBABILITY_GIF = 0.99

EGOR_PROMPT = (
    "Ответь на это сообщение в грубой манере, попытаясь унизить автора сообщения. Учти, что автора этого сообщения зовут Егор. Длинна текста твоего ответа должны быть не больше 30 слов"
)

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # Реагируем на сообщения для отправки оскорблений (для INSULT_USER_ID)
    if user_id == TARGET_EGOR_ID:
        if random.random() < RESPONSE_PROBABILITY_INSULT:
            # Генерируем ответ на основе промпта
            url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImE4YzY1ODRhLTdjOWQtNDFmYS1iMzFlLTE5ZTU5MjM3YmUyNSIsImV4cCI6NDkwMDY0MTkwNH0.ERimLEnY9FJ8Mve61g5a3KBnVD2oURz9Yt8bgSEf-A89oWem6kbCYTDPPP3IOHIrVClt5tcT5jm0GkHZD0NeRA",
            }
            data = {
                "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                "messages": [
                    {"role": "system", "content": EGOR_PROMPT},
                    {"role": "user", "content": message.text},
                ],
            }

            try:
                response = requests.post(url, headers=headers, json=data, timeout=50)
                response.raise_for_status()
                response_data = response.json()
                if "choices" in response_data and response_data["choices"]:
                    bot_text = response_data["choices"][0]["message"]["content"].strip()
                    await message.reply(bot_text, parse_mode="Markdown")
                    return  # Завершаем обработку, если оскорбление отправлено
            except Exception as e:
                await message.reply(f"Ошибка при генерации оскорбления: {e}")

    # Реагируем на сообщения для отправки гифок (для GIF_USER_ID)
    if user_id == TARGET_KLIM_ID:
        if random.random() < RESPONSE_PROBABILITY_GIF:
            # Отправляем гифку как ответ на сообщение
            await message.reply_animation(GIF_URL)  # Отправка гифки в ответ
            return  # Завершаем обработку, если гифка отправлена

    # Проверяем, упомянут ли бот
    bot_username = (await bot.get_me()).username
    if message.chat.type in ["group", "supergroup"] and f"@{bot_username}" not in message.text:
        return  # Игнорируем, если бот не был упомянут

    # Убираем упоминание бота из текста
    user_message = message.text.replace(f"@{bot_username}", "").strip()

    # Генерируем основное сообщение
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImE4YzY1ODRhLTdjOWQtNDFmYS1iMzFlLTE5ZTU5MjM3YmUyNSIsImV4cCI6NDkwMDY0MTkwNH0.ERimLEnY9FJ8Mve61g5a3KBnVD2oURz9Yt8bgSEf-A89oWem6kbCYTDPPP3IOHIrVClt5tcT5jm0GkHZD0NeRA",
    }
    data = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [
            {"role": "system", "content": "Отвечай не большим сообщение, длинной не более чем в 70 слов. Общайся как с другом. Если ты понимаешь, что над тобой хотят пошутить то ответь на это сообщение в грубой манере, попытаясь унизить автора сообщения. Если к тебе обращаются с серьерзным вопросом, отвечай серьезно"},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=50)
        response.raise_for_status()

        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            bot_text = response_data["choices"][0]["message"]["content"].strip()
            await message.answer(bot_text, parse_mode="Markdown")
        else:
            await message.answer("Ответ от API пустой или в неверном формате.")

    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка подключения к API: {e}")
    except (IndexError, KeyError, ValueError) as e:
        await message.answer("Ошибка при обработке ответа от API. Проверьте правильность модели или токена.")
    except Exception as e:
        await message.answer(f"Произошла неожиданная ошибка: {e}")


async def on_start(request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return web.Response()

app = web.Application()
app.router.add_post(f'/{TOKEN}', on_start)
