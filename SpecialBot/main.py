import logging
from vkbottle import BaseStateGroup, GroupEventType, VKAPIError, CtxStorage, Keyboard, Text, KeyboardButtonColor, EMPTY_KEYBOARD
from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle.api import API
from db import BotDB
import random
import nest_asyncio
nest_asyncio.apply()
  # Я переделывал чужой готовый код на aiogram'e и с готовой бд в короткий срок, поэтому бд оставил.
  # Для удобства стоит переделать бд и назвать столбцы соответсвующе.


token = ""
group_id = "220697093"
bot = Bot(token)
api = API(bot)
api.groups.get_long_poll_server

ctx = CtxStorage()
logging.getLogger("vkbottle").setLevel(logging.DEBUG)
BotDB = BotDB('/data/database.db')

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_raw_event(event: dict):
    print("Received raw event:", event)
    if "type" in event and event["type"] == "message_new":
        print("Received new message event")
        # Создание объекта Message для обработки
        msg = Message(bot, event)

        # Обработка сообщения
        await bot.dispenser.process_event(msg)

  # Бланки

menu_main_text = '1. Смотреть анкеты по интересам\n2. Смотреть случайные анкеты\n3. Моя анкета\n4. Удалить анкету'
my_anketa_text = '1. Заполнить анкету заново\n2. Изменить любимые фильмы\n3. Изменить текст анкеты\n4. Вернуться назад'


  # Заготовка клавиатуры

keyboard_menu = Keyboard(one_time=False, inline = True)
keyboard_menu.add(Text("1"), color=KeyboardButtonColor.PRIMARY)
keyboard_menu.add(Text("2"), color=KeyboardButtonColor.PRIMARY)
keyboard_menu.add(Text("3"), color=KeyboardButtonColor.PRIMARY)
keyboard_menu.add(Text("4"), color=KeyboardButtonColor.PRIMARY)

def show_anketa(name, age, favorits, text, link):
  return f'Имя: {name}\nВозраст: {age}\nЛюбимые фильмы/сериалы: {favorits}\nО себе: {text}\nСсылка на вк: {link}'

def get_random_anketa(list_of_anketi):
  anketa = list_of_anketi[random.randint(0, len(list_of_anketi) - 1)]
  a = anketa
  return [show_anketa(a[2], a[3], a[7], a[5], a[4]), a[1]]

def is_member(group_id: int, user_id: int) -> bool:
  return api.groups.is_member(access_token=token,
                                 group_id=group_id,
                                 user_id=user_id)

  # Стейты для диалога

class Reg(BaseStateGroup):
  CHOOSING_GENDER = 0
  name = 1
  age = 2
  favorits = 3
  text = 4
  link = 5
  menu_answer = 6
  my_anketa_answer = 7
  change_text = 8
  change_inter = 9
  delete_confirm = 10
  anketa_reaction = 11
  all_anketa_reaction = 12
  end = 13


@bot.on.message(payload={"command": "start"})
@bot.on.message(text=["/start", "Привет", "привет", "Начать", "начать"])
async def anketa_start(message: Message):
    print("Received message:", message.text)

    if not BotDB.user_exists(message.from_id):
        BotDB.add_user(message.from_id)

    if BotDB.anketa_exists(message.from_id):
        anketa = BotDB.get_anketa(message.from_id)
        a = anketa[0]
        caption = show_anketa(a[2], a[3], a[7], a[5], a[4])
        print("Existing anketa found:", caption)

        await message.answer(message=menu_main_text, keyboard=keyboard_menu)
        await bot.state_dispenser.set(message.from_id, Reg.menu_answer)

    else:
        print("No existing anketa found")
        keyboard = Keyboard(one_time=False, inline=True)
        keyboard.add(Text("Заполнить анкету"), color=KeyboardButtonColor.PRIMARY)

        await message.answer(message='Привет! Это КиноТиндер. Хочешь найти собеседника по интересам? Тогда скорее начинай и жми "Заполнить анкету"😁',
                             keyboard=keyboard)

@bot.on.message(text='Заполнить анкету')
async def check_mem(message: Message):
  if not is_member(group_id, message.from_id):
    await message.answer("Кажется, ты не подписан на нашу группу😵Давай скорее это исправим, чтобы начать 👉 (https://vk.com/specialrole)")
    return
  await message.answer(message = "Как тебя зовут?", keyboard=EMPTY_KEYBOARD)
  await bot.state_dispenser.set(message.from_id, Reg.name)

@bot.on.message(state = Reg.name)
async def name(message: Message):
  if len(message.text) > 30:
    await message.answer("Слишком длинное имя")
    return
  ctx.set(f'name{message.from_id}', message.text)
  ctx.set(f'gender{message.from_id}', '0')
  await message.answer("Сколько тебе лет?")
  await bot.state_dispenser.set(message.from_id, Reg.age)

@bot.on.message(state = Reg.age)
async def age(message: Message):
  try:
    if 10 > int(message.text) or int(message.text) > 100:
      await message.answer("Какой-то странный возраст, попробуй еще раз")
      return
  except(TypeError, ValueError):
    await message.answer("Какой-то странный возраст, попробуй еще раз")
    return
  ctx.set(f'age{message.from_id}', message.text)

  await message.answer("Напиши через запятую несколько своих любимых фильмов/сериалов. Поиск происходит в основном по ним, так что чем больше укажешь, тем больше шанс найти кого-то)")
  await bot.state_dispenser.set(message.from_id, Reg.favorits)

@bot.on.message(state = Reg.favorits)
async def favorits(message: Message):
  ctx.set(f'favorits{message.from_id}', message.text)

  await message.answer("Расскажи что-нибудь о себе: например, какие жанры тебе нравятся? Как давно и почему начал смотреть кино/сериалы? Здесь может быть все, что, на твой взгляд, поможет тебе найти собеседника по душе.")
  await bot.state_dispenser.set(message.from_id, Reg.text)

@bot.on.message(state = Reg.text)
async def text(message: Message):
  if len(message.text) > 500:
    await message.answer("Слишком длинное описание, постарайся его сократить")
    return
  ctx.set(f'text{message.from_id}', message.text)

  await message.answer(message = "Укажи ссылку на свою страницу в вк для связи (начиная с https://vk.com/...)")
  await bot.state_dispenser.set(message.from_id, Reg.link)

@bot.on.message(state = Reg.link)
async def link(message: Message):
  if 'https://vk.com/' not in message.text:
    await message.answer("Обрати внимание на формат ссылки и отправь еще раз")
    return
  ctx.set(f'link{message.from_id}', message.text)
  keyboard = Keyboard(one_time=False, inline=True)
  keyboard.add(Text("Проверить"), color=KeyboardButtonColor.POSITIVE)

  await message.answer("Отлично, анкета готова! Давай проверим, что все на месте", keyboard=keyboard)
  await bot.state_dispenser.set(message.from_id, Reg.end)

@bot.on.message(state = Reg.end)
async def end(message: Message):

  data=[]
  data.append(ctx.get(f'name{message.from_id}'))
  data.append(ctx.get(f'gender{message.from_id}'))
  data.append(ctx.get(f'age{message.from_id}'))
  data.append(ctx.get(f'favorits{message.from_id}'))
  data.append(ctx.get(f'text{message.from_id}'))
  data.append(ctx.get(f'link{message.from_id}'))
  d = list(data)
  print(d)

  BotDB.add_anketa(message.from_id, d[0], d[1], d[2], d[3], d[4], d[5])

  caption = show_anketa(d[0], d[2], d[3], d[4], d[5])
  await message.answer("Вот ваша анкета: ")
  await message.answer(caption)

  await message.answer(menu_main_text, keyboard = keyboard_menu)
  await bot.state_dispenser.set(message.from_id, Reg.menu_answer)


@bot.on.message(state = Reg.menu_answer)
async def menu_answer(message: Message):
  if message.text == "1":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])

    u_list_of_anketi = BotDB.find_anketi(message.from_id, a[7], a[3])
    list_of_anketi = []
    seen=[]

    for i in u_list_of_anketi:
      if i[1] not in seen:
        list_of_anketi.append(i)

    try:
      get_random_anketa(list_of_anketi)
    except ValueError:
      await message.answer('Мне не удалось тебе никого подобрать ;(\nПроверить корректность введенных данных.\nЕсли все хорошо, то, скорее всего, твой возраст или твои интересы не очень популярные.\n\nТы можешь попробовать дополнить любимые фильмы или вернуться назад и выбрать пункт "2", чтобы смотреть случайные анкеты')
      await message.answer(caption)
      await message.answer(my_anketa_text, keyboard = keyboard_menu)
      await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)

    keyboard = Keyboard(one_time=True, inline = False)
    keyboard.add(Text("Дальше"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Вернуться назад"))

    anketa = get_random_anketa(list_of_anketi)
    caption = anketa[0]
    seen.append(anketa[1])
    ctx.set(f'seen{message.from_id}', seen)

    await message.answer(message = caption, keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.anketa_reaction)

  elif message.text == "2":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])

    u_list_of_anketi = BotDB.get_all_anketi(message.from_id)
    list_of_anketi = []
    all_seen=[]

    for i in u_list_of_anketi:
      if i[1] not in all_seen:
        list_of_anketi.append(i)

    try:
      get_random_anketa(list_of_anketi)
    except ValueError:
      await message.answer("Ты просмотрел все анкеты на данный момент. Наша база пока что небольшая, но она постоянно пополняется, поэтому попробуй вернуться позже")
      await message.answer(caption)
      await message.answer(my_anketa_text, keyboard = keyboard_menu)
      await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)

    keyboard = Keyboard(one_time=True, inline = False)
    keyboard.add(Text("Дальше"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Вернуться назад"))

    anketa = get_random_anketa(list_of_anketi)
    caption = anketa[0]
    all_seen.append(anketa[1])
    ctx.set(f'all_seen{message.from_id}', all_seen)

    await message.answer(message = caption, keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.all_anketa_reaction)    

  elif message.text == "3":
# Show form (anketa) in 4 strings

    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])

    await message.answer(caption)

    keyboard = Keyboard(one_time=False, inline = True)
    keyboard.add(Text("1"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("2"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("3"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("4"), color=KeyboardButtonColor.PRIMARY)

    await message.answer(my_anketa_text, keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)

  elif message.text == "4":
    keyboard = Keyboard(one_time=False, inline = True)
    keyboard.add(Text("Да"), color=KeyboardButtonColor.NEGATIVE)
    keyboard.add(Text("Нет"), color=KeyboardButtonColor.PRIMARY)

    await message.answer("Вы точно хотите удалить свою анкету?", keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.delete_confirm)

  else:
    await message.answer("Выберите вариант из кнопок")
    return

@bot.on.message(state = Reg.anketa_reaction)
async def anketa_reaction(message: Message):
  if message.text == "Дальше":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])

    u_list_of_anketi = BotDB.find_anketi(message.from_id, a[7], a[3])
    list_of_anketi = []

    for i in u_list_of_anketi:
      if i[1] not in ctx.get(f'seen{message.from_id}'):
        list_of_anketi.append(i)

    try:
      get_random_anketa(list_of_anketi)
    except ValueError:
      await message.answer("Мне больше не удалось никого найти ;(\nВозможно, твой возраст или твои интересы не очень популярные.\nЕсли хочешь увидеть еще анкеты, можешь попробовать дополнить список любимых фильмов или вернуться назад и просмотреть случайные анкеты")
      await message.answer(caption)
      await message.answer(my_anketa_text, keyboard = keyboard_menu)
      await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)

    keyboard = Keyboard(one_time=True, inline = False)
    keyboard.add(Text("Дальше"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Вернуться назад"))
    anketa = get_random_anketa(list_of_anketi)

    caption = anketa[0]
    seen=ctx.get(f'seen{message.from_id}')
    seen.append(anketa[1])
    ctx.set(f'seen{message.from_id}', seen)

    await message.answer(message = caption, keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.anketa_reaction)

  elif message.text == "Вернуться назад":

    await message.answer(menu_main_text, keyboard = keyboard_menu)
    await bot.state_dispenser.set(message.from_id, Reg.menu_answer)
  else:
    await message.answer("Выберите вариант из кнопок")
    return

@bot.on.message(state = Reg.all_anketa_reaction)
async def anketa_reaction(message: Message):
  if message.text == "Дальше":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])

    u_list_of_anketi = BotDB.get_all_anketi(message.from_id)
    list_of_anketi = []

    for i in u_list_of_anketi:
      if i[1] not in ctx.get(f'all_seen{message.from_id}'):
        list_of_anketi.append(i)

    try:
      get_random_anketa(list_of_anketi)
    except ValueError:
      await message.answer("Ты просмотрел все анкеты на данный момент. Наша база пока что небольшая, но она постоянно пополняется, поэтому попробуй вернуться позже")
      await message.answer(caption)
      await message.answer(my_anketa_text, keyboard = keyboard_menu)
      await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)

    keyboard = Keyboard(one_time=True, inline = False)
    keyboard.add(Text("Дальше"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Вернуться назад"))
    anketa = get_random_anketa(list_of_anketi)

    caption = anketa[0]
    all_seen=ctx.get(f'all_seen{message.from_id}')
    all_seen.append(anketa[1])
    ctx.set(f'all_seen{message.from_id}', all_seen)

    await message.answer(message = caption, keyboard = keyboard)
    await bot.state_dispenser.set(message.from_id, Reg.all_anketa_reaction)

  elif message.text == "Вернуться назад":

    await message.answer(menu_main_text, keyboard = keyboard_menu)
    await bot.state_dispenser.set(message.from_id, Reg.menu_answer)
  else:
    await message.answer("Выберите вариант из кнопок")
    return

@bot.on.message(state = Reg.delete_confirm)
async def delete_confirm(message: Message):
  if message.text == "Да":
    BotDB.delete_anketa(message.from_id)
    BotDB.delete_user(message.from_id)
    await message.answer("Ваша анкета удалена!\nВы можете вернуться сюда в любое время по команде /start", keyboard = EMPTY_KEYBOARD)
  elif message.text == "Нет":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])
    await message.answer(caption)
    await message.answer(my_anketa_text, keyboard = keyboard_menu)
    await bot.state_dispenser.set(message.from_id, Reg.my_anketa_answer)
  else:
    await message.answer("Выберите вариант из кнопок")
    return

@bot.on.message(state = Reg.my_anketa_answer)
async def my_anketa_answer(message: Message):

  if message.text == "1":
    BotDB.delete_anketa(message.from_id)
    await message.answer("Как тебя зовут?", keyboard=EMPTY_KEYBOARD)
    await bot.state_dispenser.set(message.from_id, Reg.name)

  elif message.text == "2":
    await message.answer("Введите новый список любимых фильмов/сериалов через запятую", keyboard=EMPTY_KEYBOARD)
    ctx.set(f'favorits{message.from_id}', message.text)
    await bot.state_dispenser.set(message.from_id, Reg.change_inter)

  elif message.text == "3":
    await message.answer("Введите новую информацию о себе", keyboard=EMPTY_KEYBOARD)
    ctx.set(f'text{message.from_id}', message.text)
    await bot.state_dispenser.set(message.from_id, Reg.change_text)

  elif message.text == "4":
    anketa = BotDB.get_anketa(message.from_id)
    a = anketa[0]
    caption = show_anketa(a[2], a[3], a[7], a[5], a[4])
    await message.answer(caption)
    await message.answer(menu_main_text, keyboard = keyboard_menu)
    await bot.state_dispenser.set(message.from_id, Reg.menu_answer)

  else:
    await message.answer("Выберите вариант из кнопок")
    return

@bot.on.message(state = Reg.change_text)
async def change_text(message: Message):
  BotDB.update_text(message.from_id, message.text)
  anketa = BotDB.get_anketa(message.from_id)
  a = anketa[0]
  caption = show_anketa(a[2], a[3], a[7], a[5], a[4])
  await message.answer(caption)
  await message.answer(menu_main_text, keyboard = keyboard_menu)
  await bot.state_dispenser.set(message.from_id, Reg.menu_answer)

@bot.on.message(state = Reg.change_inter)
async def change_text(message: Message):
  BotDB.update_inter(message.from_id, message.text)
  anketa = BotDB.get_anketa(message.from_id)
  a = anketa[0]
  caption = show_anketa(a[2], a[3], a[7], a[5], a[4])
  await message.answer(caption)
  await message.answer(menu_main_text, keyboard = keyboard_menu)
  await bot.state_dispenser.set(message.from_id, Reg.menu_answer)

if __name__ == "__main__":
    bot.run_forever()
