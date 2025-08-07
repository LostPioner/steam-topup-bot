import logging
from aiogram import Bot, Dispatcher, types, executor
import os

# === НАСТРОЙКИ ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "8358944672:AAGwXvk3lVOtgFZIuAX9hO33WA7k44PYuJA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1850622948"))
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "22222222222222")
COMMISSION_PERCENT = 10

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# === Хэндлер /start ===
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("\U0001F4B8 Пополнение баланса Steam\n\nВведите сумму, на которую хотите пополнить (в рублях):")

# === Хэндлер суммы ===
@dp.message_handler(lambda message: message.text.isdigit())
async def process_amount(message: types.Message):
    try:
        amount = int(message.text)
        final_amount = round(amount * (1 + COMMISSION_PERCENT / 100))

        text = (
            f"Вы хотите пополнить Steam на: {amount} ₽\n"
            f"С учётом комиссии {COMMISSION_PERCENT}%: {final_amount} ₽\n\n"
            f"\U0001F4B3 Оплатите на ЮMoney: `{YOOMONEY_WALLET}`\n"
            f"После оплаты нажмите кнопку ниже."
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("\u2709\ufe0f Я оплатил", callback_data=f"paid:{amount}:{final_amount}"))

        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as e:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        logging.exception(e)

# === Подтверждение оплаты ===
@dp.callback_query_handler(lambda c: c.data.startswith("paid:"))
async def confirm_payment(callback_query: types.CallbackQuery):
    _, amount, final_amount = callback_query.data.split(":")
    user = callback_query.from_user

    text = (
        f"\u2709️ Новый заказ!\n"
        f"Пользователь: @{user.username} (ID: {user.id})\n"
        f"Хочет пополнить: {amount} ₽\n"
        f"Оплатил: {final_amount} ₽\n"
        f"ЮMoney: {YOOMONEY_WALLET}"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await bot.answer_callback_query(callback_query.id, text="Спасибо! Заявка отправлена оператору.")
    await bot.send_message(chat_id=user.id, text="\u2705 Спасибо! Ваша заявка отправлена. Ожидайте подтверждения.")

# === Запуск ===
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
