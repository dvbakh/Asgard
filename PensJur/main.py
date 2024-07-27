from python_whatsapp_bot import Whatsapp
import re
import requests
import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep

# Параметры для WhatsApp
TOKEN = ''
PHONE_ID = "" 
INSTANCE_ID = ""

# Создание случайного сообщения для избежания блокировки
greets = ['Добрый день!', 'Здравствуйте!']
problem = ['Пожалуйста, опишите вашу проблему, чтобы мы смогли Вам помочь. Вы можете написать её текстом или отправить голосовое сообщение.', 'Вы можете описать свою проблему в сообщении текстом или голосом.']
thanks = ['Спасибо за Ваше доверие!', 'Спасибо, что доверяете нам!']



# Настройки авторизации
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('pensionny-jurist-397d684b267d.json', scope)
client = gspread.authorize(creds)

# ID Google Таблицы
spreadsheet_id = ''

# Функция для получения данных из таблицы
def get_data_from_sheet():
    sheet = client.open_by_key(spreadsheet_id).sheet1
    data = sheet.get_all_values()
    return data, sheet

while True:
    # Получаем данные из таблицы
    data, sheet = get_data_from_sheet()

    for idx, row in enumerate(data[1:], start=2):  # Начинаем со второй строки, индекс с 2
        if row[6] != 'T':  # Проверяем, что G колонка пустая
            NUMBER = str(row[1])
            NUMBER = re.sub('\D', '', NUMBER)
            MESSAGE = f'{random.choice(greets)} Вы обратились в юридическую компанию "Сам в Суд" Любавы Трофимовой. {random.choice(problem)} {random.choice(thanks)}'
            URL = f"https://biz.wapico.ru/api/send.php"
            headers = {
                "Authorization": "Bearer " + TOKEN,
            }

            data = {
                "number": NUMBER,
                "type": "text",
                "instance_id": INSTANCE_ID,
                "access_token": TOKEN,
                "message": MESSAGE,
            }

            response = requests.post(URL, headers=headers, data=data)
            response_json = response.json()
            print(response_json)

            if response_json.get("status") == "success":
                # Обновляем ячейку G в строке после успешной отправки сообщения
                sheet.update_cell(idx, 7, "T")

    # Приостанавливаем выполнение программы на 1 минуту
    sleep(60)
