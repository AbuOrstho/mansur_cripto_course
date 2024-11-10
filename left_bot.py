from itertools import count
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
import logging

# Установите ваш токен здесь
API_TOKEN = '8101317125:AAHvwVN6izEW52xwrdopJjl8PvornFhGM_0'

# Логирование настроено на уровень DEBUG для подробного вывода
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class FeedbackForm(StatesGroup):
    waiting_for_feedback = State()


# Загрузка черного и белого списка
with open("blacklist.txt", "r", encoding="utf-8") as blacklist:
    blacklist_ids = {line.strip() for line in blacklist}

with open("whitelist.txt", "r", encoding="utf-8") as whitelist:
    whitelist_ids = {line.strip() for line in whitelist}


# Команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')
    user_id = message.from_user.id
    user_info = (
        f"Пользователь {message.from_user.full_name} (@{message.from_user.username}), ID: {user_id} "
        f"вызвал команду /start в {time_str} {date_str}."
    )

    # Создаем инлайн-клавиатуру с кнопками "Принять" и "Отклонить"
    approval_keyboard = InlineKeyboardMarkup(row_width=2)
    approval_keyboard.add(
        InlineKeyboardButton("Принять", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("Отклонить", callback_data=f"reject_{user_id}")
    )

    # Отправляем сообщение с кнопками на ваш ID
    await bot.send_message('789614280', user_info, reply_markup=approval_keyboard)

    # Проверяем, находится ли пользователь в черном списке
    if str(message.from_user.id) not in blacklist_ids:
        await message.reply("""👋Ассаламу 1алайкум, всех приветствую! Добро пожаловать на наш курс обучения!
🔑Здесь ты узнаешь все что нужно для успешного старта в трейдинге и криптовалюте.

📧Данный мини-курс:
➡️научит тебя правильно инвестировать и зарабатывать money💰
➡️научит смотреть на рынок более глобально и находить потенциально прибыльные ситуации
➡️убережет от ошибок в инвестировании, в частности в трейдинге
➡️воспитает в вас проф. трейдера

🧠 Здесь ты узнаешь:
1️⃣ Информацию о работе на рынках (крипто, форекс, индексы)
2️⃣ Основные правила для новичков
3️⃣ Рекомендации по кибербезопасности
4️⃣ Секреты психологии трейдера
5️⃣ Как контролировать риски
6️⃣ Полный комплект инструментов для начала торговли
7️⃣ Логику движения графиков
8️⃣ Как получить деньги в управление

💡 После того как администратор примет твою заявку, ты сможешь приступить к обучению и начать осваивать эти знания.

Ожидай подтверждения от админа и будь готов начать свой путь к успеху!""")
    else:
        await message.reply(
            'К сожалению, вы находитесь в бане у данного бота. Для решения этой проблемы напишите @w03lock'
        )


# Обработчик для кнопок "Принять" и "Отклонить"
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(('approve_', 'reject_')))
async def process_callback(callback_query: types.CallbackQuery):
    action, user_id = callback_query.data.split('_')

    if action == "approve":
        if user_id not in whitelist_ids:
            with open("whitelist.txt", "a", encoding="utf-8") as file:
                file.write(f"{user_id}\n")
            whitelist_ids.add(user_id)

        # Инлайн-клавиатура с кнопками для начала курса
        course_keyboard = InlineKeyboardMarkup(row_width=2)
        course_keyboard.add(
            InlineKeyboardButton("Начать", callback_data="start_course"),
            InlineKeyboardButton("План", callback_data="plan_course")
        )
        await callback_query.answer("Пользователь принят")

        # Отправляем фото пользователю
        photo_url = 'photo/start_photo.jpg'
        caption = (
            "Ваш запрос был принят! 🎓\n"
            "Мы рады приветствовать тебя на Мини-курсе от ComfortZone, на котором ты узнаешь:\n\n"
            "\n➡️Какие знания и навыки нужны для того, чтобы твоя торговля была прибыльной"
            "\n➡️Какие виды рынков существуют помимо крипты"
            "\n➡️Абсолютно разные и прибыльные подходы к анализу графика"
        )
        await bot.send_photo(chat_id=user_id, photo=open(photo_url, "rb"), caption=caption,
                             reply_markup=course_keyboard)

    elif action == "reject":
        if user_id not in blacklist_ids:
            with open("blacklist.txt", "a", encoding="utf-8") as blacklist:
                blacklist.write(f"{user_id}\n")
            blacklist_ids.add(user_id)
        await callback_query.answer("Пользователь отклонен")
        await bot.send_message(user_id, "Ваш запрос был отклонен.")

    await callback_query.message.edit_text(
        callback_query.message.text + f"\n\nПользователь {'принят' if action == 'approve' else 'отклонен'}."
    )


# Обработчик для нажатия кнопки "Начать"
@dp.callback_query_handler(lambda c: c.data == "start_course")
async def start_course_handler(callback_query: types.CallbackQuery):
    await lesson_1(callback_query)
    await callback_query.answer()


# Обработчик для нажатия кнопки "План"
@dp.callback_query_handler(lambda c: c.data == "plan_course")
async def start_course_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("""План:

- Структура курса 

- Что ты получишь на обучении?

- Словарь

- «Инвестирование - базовая задача в современном обществе»

- Топ 5 плохих способов инвестиций 

- Мои действия, если бы я только сейчас захотел зайти в крипту 

- Главные ошибки новичков в трейдинге

- 5 принципов успешного трейдера 

- Как в себе развить мышление проф. трейдера 

Видео-уроки:
- Кто такой трейдер и почему данная профессия привлекательна?
- Криптовалютный рынок 
- Форекс рынок
- Индексы
- Словарь стрейдера 

- Биржи
- Инструменты 

- Безопасность

- Психология трейдера 
- Риск менеджмент

- Паттерны
- Индикаторы

- Smart Money

- Фазы рынка и структура 
- Ликвидность 

- Вайкофф

- Около крипта""")
    await callback_query.answer()


# Обработчики для каждого занятия
async def lesson_1(callback_query: types.CallbackQuery):
    lesson_1_kb = InlineKeyboardMarkup(row_width=1)
    lesson_1_kb.add(InlineKeyboardButton("Дальше", callback_data="lesson_2"))
    with open("materials/Словарь.docx", "rb") as file:
        await bot.send_document(chat_id=callback_query.from_user.id, document=file)
    await callback_query.message.answer("Это первое занятие. Мы посмотрим словарь терминов ", reply_markup=lesson_1_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_2")
async def lesson_2(callback_query: types.CallbackQuery):
    lesson_2_kb = InlineKeyboardMarkup(row_width=2)
    lesson_2_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_1"),
        InlineKeyboardButton("Дальше", callback_data="lesson_3")
    )
    text = "<a href='https://telegra.ph/INVESTIROVAT---BAZOVAYA-ZADACHA-V-SOVREMENNOM-OBSHCHESTVE-11-03-2'>ИНВЕСТИРОВАТЬ - БАЗОВАЯ ЗАДАЧА В СОВРЕМЕННОМ ОБЩЕСТВЕ</a>"
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=open("photo/lesson2.jpg", "rb"), caption=text,
                         parse_mode="HTML", reply_markup=lesson_2_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_3")
async def lesson_3(callback_query: types.CallbackQuery):
    lesson_3_kb = InlineKeyboardMarkup(row_width=2)
    lesson_3_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_2"),
        InlineKeyboardButton("Дальше", callback_data="lesson_4")
    )
    text = "<a href='https://telegra.ph/TOP-5-PLOHIH-SPOSOBOV-INVESTICIJ-11-03'>ТОП 5 ПЛОХИХ СПОСОБОВ ИНВЕСТИЦИЙ</a>"
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=open("photo/lesson3.jpg", "rb"), caption=text,
                         parse_mode="HTML", reply_markup=lesson_3_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_4")
async def lesson_4(callback_query: types.CallbackQuery):
    lesson_4_kb = InlineKeyboardMarkup(row_width=2)
    lesson_4_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_3"),
        InlineKeyboardButton("Дальше", callback_data="lesson_5")
    )
    text = (
        "*МОИ ДЕЙСТВИЯ, ЕСЛИ БЫ Я ТОЛЬКО СЕЙЧАС ЗАХОТЕЛ ЗАЙТИ В КРИПТУ? 👆*\n\n"
        "➤ _Посчитал бы, сколько у меня свободных средств сейчас есть в целом\\. И выделил хотя бы 10% на инвестирование в крипту\\. Сначала на небольшой сумме надо «пощупать» и понять, что такое «купить\\-поддержать\\-продать» токен, увидеть первый прирост, пусть даже небольшой\\)\\)\n\n"
        "> *Ваши деньги уже начнут делать деньги\\!* 💰\n\n"
        "➤ _Занялся бы базовой фин\\.грамотностью\\. То есть с каждого дохода 10\\-20% откладывал бы в капитал\\. Или 10% на капитал, 10% на крипту\\.\n\n"
        "➤ _Подписался бы на ComfortZone_\n\n"
        "➤ _Ни за что не стал бы заходить в сделки, где «точно будет рост x500%», это самый лучший проект, его просто недооценили\\)_"
    )
    await callback_query.message.answer(text, parse_mode="MarkdownV2", reply_markup=lesson_4_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_5")
async def lesson_5(callback_query: types.CallbackQuery):
    lesson_5_kb = InlineKeyboardMarkup(row_width=2)
    lesson_5_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_4"),
        InlineKeyboardButton("Дальше", callback_data="lesson_6")
    )
    text = "<a href='https://telegra.ph/Glavnye-oshibki-novichkov-v-trejdinge-11-03'>Главные ошибки новичков в трейдинге:</a>"
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=open("photo/lesson5.jpg", "rb"), caption=text,
                         parse_mode="HTML", reply_markup=lesson_5_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_6")
async def lesson_6(callback_query: types.CallbackQuery):
    lesson_6_kb = InlineKeyboardMarkup(row_width=2)
    lesson_6_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_5"),
        InlineKeyboardButton("Дальше", callback_data="lesson_7")
    )
    text = "<a href='https://telegra.ph/5-principov-uspeshnogo-trejdera-11-03'>5 принципов успешного трейдера:</a>"
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=open("photo/lesson6.jpg", "rb"), caption=text,
                         parse_mode="HTML", reply_markup=lesson_6_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_7")
async def lesson_7(callback_query: types.CallbackQuery):
    lesson_7_kb = InlineKeyboardMarkup(row_width=2)
    lesson_7_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_6"),
        InlineKeyboardButton("Дальше", callback_data="lesson_8")
    )
    text = "<a href='https://telegra.ph/Kak-razvit-v-sebe-myshlenie-professionalnogo-trejdera-11-03'>Как развить в себе мышление профессионального трейдера?</a>"
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=open("photo/lesson7.jpg", "rb"), caption=text,
                         parse_mode="HTML", reply_markup=lesson_7_kb)


@dp.callback_query_handler(lambda c: c.data == "lesson_8")
async def lesson_8(callback_query: types.CallbackQuery):
    lesson_8_kb = InlineKeyboardMarkup(row_width=2)
    lesson_8_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_7"),
        InlineKeyboardButton("Дальше", callback_data="lesson_9")
    )

    await callback_query.message.answer("""—————————

❗️Переходим к видео-урокам ❗️

—————————""")

    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 1</u>
- Кто такой трейдер и почему данная профессия привлекательна?
- Криптовалютный рынок
- Форекс рынок
- Индексы"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANKZyvoeCEUmWsdRALM96UpjzcqRhAAAsxgAAKrsWFJLlvhgK3pakk2BA",
        caption=caption,
        reply_markup=lesson_8_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_9")
async def lesson_9(callback_query: types.CallbackQuery):
    lesson_9_kb = InlineKeyboardMarkup(row_width=2)
    lesson_9_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_8"),
        InlineKeyboardButton("Дальше", callback_data="lesson_10")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Криптовалютный рынок</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANMZyvpVLtzlKdQV-xb21wuZmfGN6IAAtBgAAKrsWFJAAFrqC2fyBSxNgQ",
        caption=caption,
        reply_markup=lesson_9_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_10")
async def lesson_10(callback_query: types.CallbackQuery):
    lesson_10_kb = InlineKeyboardMarkup(row_width=2)
    lesson_10_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_9"),
        InlineKeyboardButton("Дальше", callback_data="lesson_11")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Форекс рынок</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANOZyvpkHlpK6xogeRJNiDGVoQVv5oAAtJgAAKrsWFJc2ro7adoh1g2BA",
        caption=caption,
        reply_markup=lesson_10_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_11")
async def lesson_11(callback_query: types.CallbackQuery):
    lesson_11_kb = InlineKeyboardMarkup(row_width=2)
    lesson_11_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_9"),
        InlineKeyboardButton("Дальше", callback_data="lesson_12")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Индексы</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANQZyvptqW9tYQAAfHtBxvbgrIZUeEEAALTYAACq7FhSa4pcz7R5xddNgQ",
        caption=caption,
        reply_markup=lesson_11_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_12")
async def lesson_12(callback_query: types.CallbackQuery):
    lesson_12_kb = InlineKeyboardMarkup(row_width=2)
    lesson_12_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_11"),
        InlineKeyboardButton("Дальше", callback_data="lesson_13")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 2</u>
- Биржи
- Инструменты"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANSZyvqyyLWRBVk7-Qz41wRdINiSz0AAthgAAKrsWFJ2LzS3wYlBTI2BA",
        caption=caption,
        reply_markup=lesson_12_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_13")
async def lesson_13(callback_query: types.CallbackQuery):
    lesson_13_kb = InlineKeyboardMarkup(row_width=2)
    lesson_13_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_12"),
        InlineKeyboardButton("Дальше", callback_data="lesson_14")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Инструменты</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANUZyvretfofI2uotbZ4zD26PcSb28AAttgAAKrsWFJ6ZXHI-1Zasg2BA",
        caption=caption,
        reply_markup=lesson_13_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_14")
async def lesson_14(callback_query: types.CallbackQuery):
    lesson_14_kb = InlineKeyboardMarkup(row_width=2)
    lesson_14_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_13"),
        InlineKeyboardButton("Дальше", callback_data="lesson_15")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 3</u>
- Безопасность в крипте"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANWZyvsrLZn6SDZozxsQIxdbzwZL7AAAtxgAAKrsWFJSF9oNejqZeo2BA",
        caption=caption,
        reply_markup=lesson_14_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_15")
async def lesson_15(callback_query: types.CallbackQuery):
    lesson_15_kb = InlineKeyboardMarkup(row_width=2)
    lesson_15_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_14"),
        InlineKeyboardButton("Дальше", callback_data="lesson_16")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 4</u>
- Психология трейдера
- Риск менеджмент"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANYZyvs9ikWWEvfVvEhO-xct0FIQd8AAt1gAAKrsWFJXSpNl4rlmTA2BA",
        caption=caption,
        reply_markup=lesson_15_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_16")
async def lesson_16(callback_query: types.CallbackQuery):
    lesson_16_kb = InlineKeyboardMarkup(row_width=2)
    lesson_16_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_15"),
        InlineKeyboardButton("Дальше", callback_data="lesson_17")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Риск менеджмент</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANaZyvtM2YZ2MDUgT4LRZyVbQABUXwPAALgYAACq7FhSaRXvCcQwYI_NgQ",
        caption=caption,
        reply_markup=lesson_16_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_17")
async def lesson_17(callback_query: types.CallbackQuery):
    lesson_17_kb = InlineKeyboardMarkup(row_width=2)
    lesson_17_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_16"),
        InlineKeyboardButton("Дальше", callback_data="lesson_18")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 5</u>
Классический тех. анализ
- Паттерны
- Индикаторы"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANcZyvtYMd_OrV9g1Coyvz-Bwwz7joAAuNgAAKrsWFJwQm6L9elp_82BA",
        caption=caption,
        reply_markup=lesson_17_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_18")
async def lesson_18(callback_query: types.CallbackQuery):
    lesson_18_kb = InlineKeyboardMarkup(row_width=2)
    lesson_18_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_17"),
        InlineKeyboardButton("Дальше", callback_data="lesson_19")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Индикаторы</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANeZyvtuUt5GllFHKNse8ASy7HceXMAAulgAAKrsWFJ5HUXK_JSvoo2BA",
        caption=caption,
        reply_markup=lesson_18_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_19")
async def lesson_19(callback_query: types.CallbackQuery):
    lesson_19_kb = InlineKeyboardMarkup(row_width=2)
    lesson_19_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_18"),
        InlineKeyboardButton("Дальше", callback_data="lesson_20")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 6</u>
- Smart money"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANgZyvt_ndnpO0dxGhmRPh9EHErE3sAAupgAAKrsWFJ2SDfpLkTZ9U2BA",
        caption=caption,
        reply_markup=lesson_19_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_20")
async def lesson_20(callback_query: types.CallbackQuery):
    lesson_20_kb = InlineKeyboardMarkup(row_width=2)
    lesson_20_kb.add(InlineKeyboardButton("Назад", callback_data="lesson_19"),
                     InlineKeyboardButton("Дальше", callback_data="lesson_21"))
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 7</u>
Структура и ликвидность
- Фазы рынка и структура
- Ликвидность"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANiZyvuh6IRSw-KMNqXrOCASfc4MboAAu5gAAKrsWFJibNDhK7OqyE2BA",
        caption=caption,
        reply_markup=lesson_20_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_21")
async def lesson_21(callback_query: types.CallbackQuery):
    lesson_21_kb = InlineKeyboardMarkup(row_width=2)
    lesson_21_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_20"),
        InlineKeyboardButton("Дальше", callback_data="lesson_22")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Ликвидность</u>"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANkZyvuqpmC0u2qlIzV_7OqUx3527wAAu9gAAKrsWFJd3fuRR50EZs2BA",
        caption=caption,
        reply_markup=lesson_21_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_22")
async def lesson_22(callback_query: types.CallbackQuery):
    lesson_22_kb = InlineKeyboardMarkup(row_width=2)
    lesson_22_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_21"),
        InlineKeyboardButton("Дальше", callback_data="lesson_23")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """<u>Урок 8</u>
- Вайкофф"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANmZyvvNSSWX7h1mziqwTWr3MlxuAQAAvFgAAKrsWFJ499JcFh5V7Q2BA",
        caption=caption,
        reply_markup=lesson_22_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_23")
async def lesson_23(callback_query: types.CallbackQuery):
    lesson_23_kb = InlineKeyboardMarkup(row_width=2)
    lesson_23_kb.add(
        InlineKeyboardButton("Назад", callback_data="lesson_22"),
        InlineKeyboardButton("Дальше", callback_data="lesson_24")
    )
    # Text with description and link (escape special symbols for MarkdownV2 if necessary)
    caption = """Урок 9
- около крипта
( на чем еще можно заработать )"""

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video="BAACAgIAAyEFAASJgBueAANoZyvvkZhV6AqZRXEpNzMwejyTfRcAAvJgAAKrsWFJteEml5io_-g2BA",
        caption=caption,
        reply_markup=lesson_23_kb,
        parse_mode="HTML"
    )


@dp.callback_query_handler(lambda c: c.data == "lesson_24")
async def lesson_24(callback_query: types.CallbackQuery):
    lesson_24_kb = InlineKeyboardMarkup(row_width=2)
    lesson_24_kb.add(
        InlineKeyboardButton("Оставить отзыв", callback_data="feedback"),
        InlineKeyboardButton("Поддержать проект ❤️", callback_data="donat")
    )

    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="""Поздравляю, вы успешно прошли наш мини-курс от ComfortZone!

Надеюсь, что вся информация, которую Вы получили, оказалась для вас полезной. Всегда помните о важности дисциплины, холодной головы при подходе к трейду, соблюдении риск-менеджмента!

И не забывайте - на фьючерсы не лезем ❌. Онли СПОТ
Всем удачи и хорошего урожая !


📘 Составитель курса: @w03lock
👨‍💻 Разработчик бота: @vay_ahi
""",
                           reply_markup=lesson_24_kb)


@dp.callback_query_handler(lambda c: c.data == "feedback")
async def lesson_24(callback_query: types.CallbackQuery):
    await callback_query.message.answer("""Мы будем рады узнать ваше мнение. Пожалуйста, оставьте отзыв о курсе — это поможет нам улучшить обучение и сделать его еще полезнее для будущих участников.

✍️ Напишите, что вам понравилось и что, по вашему мнению, можно улучшить.

Ваш отзыв очень важен для нас! Благодарим за обратную связь и удачи на вашем пути в мире криптовалют! 🚀""")
    await FeedbackForm.waiting_for_feedback.set()


@dp.message_handler(state=FeedbackForm.waiting_for_feedback, content_types=types.ContentType.TEXT)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_info = f"Отзыв от @{message.from_user.username} (ID: {message.from_user.id}):\n\n{feedback_text}"

    # Отправляем отзыв администратору
    await bot.send_message('789614280', user_info)

    # Подтверждение пользователю
    await message.answer("Спасибо за ваш отзыв! Он был отправлен администратору.")

    # Сбрасываем состояние
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "donat")
async def lesson_24(callback_query: types.CallbackQuery):
    await callback_query.message.answer("""
Вот текст для сообщения после нажатия кнопки доната:

Спасибо за поддержку! 🙏

Ваш вклад помогает нам развивать бота, добавлять новые функции и улучшать сервис для вас. Если хотите внести донат. 
Мы благодарны каждому, кто поддерживает наш проект!

Сбербанк
2202 2068 3313 3031
Мансур Т.""")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
