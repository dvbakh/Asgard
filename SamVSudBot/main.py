import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import nest_asyncio
nest_asyncio.apply()

bot = Bot(token='')
logging.basicConfig(level=logging.DEBUG)
dp = Dispatcher(bot, storage=MemoryStorage())

# States
class Wait(StatesGroup):
    start = State()
    choosing_answer = State()
    answer = State()
    end = State()

@dp.message_handler(commands="start", state = "*")
async def start(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Начать!"]
        keyboard.add(*buttons)
        photo = open('5 ошибок.png', 'rb')
        await bot.send_photo(message.from_user.id, photo, caption='Приветствую, коллега! Меня зовут Любава Трофимова, я основатель школы для юристов "Сам в Суд". За свои 18 лет практики я поняла, что каждый юрист совершает 5 ошибок в своей работе. По каждой из них я подготовила отдельное видео до 5 минут, в котором точно и емко описываю проблему и её решение. Выберите ту, которая сейчас ближе к тебе.', reply_markup = keyboard)
        await Wait.start.set()

@dp.message_handler(state = Wait.start, text=["Начать!"])
async def start(message: types.Message):
        user_channel_status = await bot.get_chat_member(chat_id='-1001914388640', user_id=message.chat.id)
        if user_channel_status["status"] != 'left':
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            buttons = ["На мне все пытаются сэкономить, и я рабою за полцены", 
                      "Я не умею делегировать и боюсь потерять из-за этого деньги",
                      "Не знаю, как удерживать клиентов, чтобы они возвращались",
                      "Не могу найти клиентов онлайн и определиться с площадкой",
                      "Хочу выйти из найма, но боюсь остаться без стабильного дохода"]
            keyboard.add(*buttons)
            await message.answer("О какой проблеме Вы хотели бы узнать?",  reply_markup = keyboard)
        else:
            # Check if member before sending a video
            await message.answer("Вы не подписаны на [канал](https://t.me/samvsud)\. Подпишитесь, чтобы получить подробный разбор ошибок юристов\.",  parse_mode='MarkdownV2')
            return
        await Wait.choosing_answer.set()

@dp.message_handler(state = Wait.choosing_answer)
async def choosing_answer(message: types.Message, state: FSMContext):
    user_channel_status = await bot.get_chat_member(chat_id='-1001914388640', user_id=message.chat.id)
    if user_channel_status["status"] != 'left':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Вернуться к проблемам", "Завершить общение"]
        keyboard.add(*buttons)
        if message.text not in ["На мне все пытаются сэкономить, и я рабою за полцены", 
                      "Я не умею делегировать и боюсь потерять из-за этого деньги",
                      "Не знаю, как удерживать клиентов, чтобы они возвращались",
                      "Не могу найти клиентов онлайн и определиться с площадкой",
                      "Хочу выйти из найма, но боюсь остаться без стабильного дохода"]:
            await message.answer("Выберите вариант из кнопок ниже")
            return
        else:
            if message.text == "На мне все пытаются сэкономить, и я рабою за полцены":
                await message.answer('''Что делать, если на мне все пытаются сэкономить\?  
                  
    Все мы сталкивается с клиентами, которые пытаются сэкономить, выпросить скидку или вообще договориться за бартер\. Как сделать из такого клиента своего фаната, но при этом не снижать стоимость ни на копейку\?  
      
    В [видео](https://youtu.be/LhX8KzpIjU8) я подробно рассказываю, как определить свою настоящую цену и что делать, если клиенты пытаются вас использовать:  
      
    А также в своём телеграм\-канале эту тему я уже поднимала в одном из [постов](https://t.me/samvsud/107)\.''', parse_mode='MarkdownV2', reply_markup = keyboard)
            elif message.text == "Я не умею делегировать и боюсь потерять из-за этого деньги":
                await message.answer('''Я не умею делегировать и боюсь потерять из\-за этого деньги  

    Все хотя бы раз слышали фразу\: «Если хочешь сделать что\-то хорошо — сделай сам»\. А как же разделение обязанностей\? Что, когда и в каких случаях можно делегировать\? Как правильно это делать, чтобы не растратить деньги на зарплаты\?  

    В [видео](https://youtu.be/x5ZfDyrTJBI) я подробно отвечаю на все эти вопросы\.  

    А также в своем телеграм\-канале эту тему я уже поднимала в одном из [постов](https://t.me/samvsud/148)\.''', parse_mode='MarkdownV2', reply_markup = keyboard)
            elif message.text == "Не знаю, как удерживать клиентов, чтобы они возвращались":
                await message.answer('''Не знаю, как удерживать клиентов, чтобы они возвращались  

    У всех юристов есть клиенты, которые пришли к ним от своих знакомых и коллег\. Но как сделать так, чтобы вас рекомендовали\? Для этого есть 5 способов\.  

    О них я подробно рассказала в [видео](https://youtu.be/EEaom3Usd8M)\.  

    А также в своем телеграм\-канале эту тему я уже поднимала в одном из [постов](https://t.me/samvsud/155)\.''', parse_mode='MarkdownV2', reply_markup = keyboard)
            elif message.text == "Не могу найти клиентов онлайн и определиться с площадкой":
                await message.answer('''Не могу найти клиентов онлайн и определиться с площадкой  

    Существует 5 рабочих площадок, где вы сможете найти 10 новых клиентов в месяц, которые заплатят вам от 100 000 рублей\.  

    О них я подробно рассказала в [видео](https://youtu.be/2EWla8W6obk)\. И эта информация доступна только в моём боте\.''', parse_mode='MarkdownV2', reply_markup = keyboard)
            elif message.text == "Хочу выйти из найма, но боюсь остаться без стабильного дохода":
                await message.answer('''Хочу выйти из найма, но боюсь остаться без стабильного дохода  

    Сразу скажу, что я _против резкого ухода из найма_\. Этот вариант подходит немногим\. Вы рискуете остаться без денег вообще, поэтому делать всë нужно постепенно\. Только тогда ваша мечта о работе на самого себя станет реальностью\.  

    Как это сделать, я подробно рассказываю в [видео](https://youtu.be/r-5jR0mk6OE)\.

    А также в своем телеграм\-канале эту тему я уже поднимала в одном из [постов](https://t.me/samvsud/150)\.''', parse_mode='MarkdownV2', reply_markup = keyboard)
    else:
        await message.answer("Вы не подписаны на [канал](https://t.me/samvsud)\. Подпишитесь, чтобы получить подробный разбор ошибок юристов\.",  parse_mode='MarkdownV2')
        return
    await Wait.end.set()

@dp.message_handler(state = Wait.end)
async def end(message: types.Message, state: FSMContext):
    if message.text not in ["Вернуться к проблемам", "Завершить общение"]:
        await message.answer("Выберите вариант из кнопок ниже")
        return
    elif message.text == "Вернуться к проблемам":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttons = ["На мне все пытаются сэкономить, и я рабою за полцены", 
                   "Я не умею делегировать и боюсь потерять из-за этого деньги",
                   "Не знаю, как удерживать клиентов, чтобы они возвращались",
                   "Не могу найти клиентов онлайн и определиться с площадкой",
                   "Хочу выйти из найма, но боюсь остаться без стабильного дохода"]
        keyboard.add(*buttons)
        await message.answer("О какой проблеме Вы хотели бы узнать?",  reply_markup = keyboard)
        await Wait.choosing_answer.set()
    elif message.text == "Завершить общение":
        await message.answer("Спасибо, что воспользовались функциями нашего бота! Вы всегда можете вернуться к началу по команде /start", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
