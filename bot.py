import telebot
import pandas as pd
import sys
import os

from telebot import types

bot = telebot.TeleBot('')

admin_login = []
admin_chat_id = set([])

save_path = "daily.xlsx"

msg = [
    "Я вас не понял",
    "Привет! Меня зовут Миньон. Добро пожаловать на проект наставничества. Я в команде кураторов этого проекта и помогу тебе разобраться что тут и как. Ты слышал уже что-то про наставничество?",
    "Держи ссылку на лендинг: [ссылка](https://auth.sberbank.ru/auth/realms/sigma/protocol/openid-connect/auth?scope=openid+extended+cert&state=tHH-3FtsRI2SEsdndan9yAPuAqFzkP5AMd-MPotyXXM.sPdwwMEt2GY.CSk1LdxQQtyv-GYp8RVrYw&response_type=code&client_id=CI01978215_sigma&redirect_uri=https%3A%2F%2Fhr.sberbank.ru%2Fauth%2Frealms%2FPAOSberbank%2Fbroker%2Fngam-otp%2Fendpoint&nonce=EPQOFkrS1lS4IdYSl7pzGg)",
    "Готов принять участие в проекте?",
    "Какая у тебя роль?",
    "Круто! Кем ты хочешь стать?",
    "Если хочешь попасть в проект, то укажи своё ФИО в следующем сообщении",
    "Ты работаешь в Сбере больше 2 лет?",
    "У тебя минимум одна повышенная годовая оценка за результат или ценности в течение 2 лет? Или ты обладаешь уникальной экспертизой?",
    "Если ты не получил памятку наставника, то напиши на почту nastavnik_hr_t@sberbank.ru",
    "Чек-лист наставника:\n1.Инициирует встречу\n2.Проводит установочную встречу\n3. Проводит регулярные встречи\n4. Оценивает результаты и дает развивающую обратную связь\n5. Заполняет чек-лист по итогу и проходит опрос\n6. Дает обратную связь и благодарит за совместную работу",
    "Если ты не получил памятку подопечного, то напиши на почту nastavnik_hr_t@sberbank.ru",
    "Чек-лист подопечного:\n1.Готовится ко встрече, продумывает цели\n2.Реализует договоренности\n3. Рассказывает о результат своей работы\n4. Заполняет чек-лист по итогу и проходит опрос \n5. Корректирует цели развития, согласованные наставником\n6. Обсуждает с наставником планы развития",
    "Отправляй заявку на почту nastavnik_hr_t@sberbank.ru по форме ниже:\n\t• Какие компетенции вы бы хотели развивать?\n\t• Какой запрос к наставнику у вас есть?\n\t• Укажите как минимум двух наставников, с которыми вам хотелось бы поработать. Если ещё ни с кем не знакомы, пропустите этот пункт.\n\t• Коротко расскажите о себе.",
    "Отправляй заявку на почту nastavnik_hr_t@sberbank.ru по форме ниже:\n\t• Расскажите, в развитии каких компетенций готовы помочь.\n\t• С какими запросами вы можете помочь?\n\t• Расскажите немного о себе — эта информация поможет будущим подопечным при выборе наставника.\n\t• Напишите, почему вы решили стать наставником.",
    "Сообщил о тебе HR",
    "Чем тебе помочь?",
    "Тогда жми дальше!",
]

button = [
    "В начало",
    "Да!",
    "Нет, но очень интересно узнать",
    "Я уже в проекте 😁",
    "Да, готов!",
    "Пока не готов, добавьте меня в резерв!",
    "Я - наставник",
    "Я - подопечный",
    "Я хочу стать наставником",
    "Я хочу стать подопечным",
    "Да, работаю больше 2 лет",
    "Нет, ещё набираюсь опыта 😁",
    "Да",
    "Нет",
    "Полезные материалы для наставника",
    "Этапы наставничества",
    "Полезные материалы для подопечного",
    "Этапы подопечного",
    "Я в деле!",
]

today_users = dict()

class User:
    def __init__(self):
        self.full_name = ""
        self.wait_name = False
        self.role = "Нет роли"

def send_with_params(chat_id, text_ids, button_ids):
    l = len(text_ids)
    for i in range(l):
        markup = None
        mode = None

        if text_ids[i] == 2:
            mode = "MarkdownV2"

        if i == l - 1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            for j in button_ids:
                markup.add(types.KeyboardButton(button[j]))
            # items = [types.KeyboardButton(button[j]) for j in button_ids]
            # markup.add(*items)

        bot.send_message(chat_id, msg[text_ids[i]], reply_markup = markup, parse_mode = mode)

def send_users():
    global today_users

    result = {
        "username": [],
        "role": [],
        "full_name": [],
    }

    for user in today_users:
        if today_users[user].full_name != "":
            result["username"].append(user)
            result["role"].append(today_users[user].role)
            result["full_name"].append(today_users[user].full_name)

    today_users = dict()

    pd.DataFrame(result).to_excel(save_path)

    for chat_id in admin_chat_id:
        bot.send_document(chat_id, open(save_path, 'rb'))

    os.remove(save_path)

@bot.message_handler(commands = ["start", "help"])
def start(message):
    send_with_params(message.chat.id, [1], [1, 2])

@bot.message_handler(commands = ["results"])
def get_results(message):
    if message.from_user.username in admin_login:
        print("{} take results, chat id {}".format(message.from_user.username, message.chat.id))

        admin_chat_id.add(message.chat.id)
        send_users()

@bot.message_handler(content_types = ["text"])
def handle_text(message):
    text = message.text
    user = today_users.get(message.from_user.username, User())
    
    if text == button[0]:
        user.wait_name = False
        send_with_params(message.chat.id, [1], [1, 2])
    elif text == button[1]:
        user.wait_name = False
        send_with_params(message.chat.id, [3], [3, 4, 5])
    elif text == button[2]:
        user.wait_name = False
        send_with_params(message.chat.id, [2], [0])
    elif text == button[3]:
        user.wait_name = False
        send_with_params(message.chat.id, [4], [6, 7])
    elif text == button[4]:
        user.wait_name = False
        send_with_params(message.chat.id, [5], [8, 9])
    elif text == button[5]:
        user.wait_name = True
        user.role = "Резерв без роли"
        send_with_params(message.chat.id, [6], [0])
    elif text == button[6]:
        send_with_params(message.chat.id, [16], [14, 15])
    elif text == button[7]:
        user.wait_name = False
        send_with_params(message.chat.id, [16], [16, 17])
    elif text == button[8]:
        user.wait_name = False
        send_with_params(message.chat.id, [7], [10, 11])
    elif text == button[9]:
        user.wait_name = False
        send_with_params(message.chat.id, [13], [0])
    elif text == button[10]:
        user.wait_name = False
        send_with_params(message.chat.id, [8], [12, 13])
    elif text == button[11]:
        user.wait_name = True
        user.role = "Резерв наставник"
        send_with_params(message.chat.id, [6], [0])
    elif text == button[12]:
        user.wait_name = False
        send_with_params(message.chat.id, [17], [18])
    elif text == button[13]:
        user.wait_name = True
        user.role = "Резерв наставник"
        send_with_params(message.chat.id, [6], [0])
    elif text == button[14]:
        user.wait_name = False
        send_with_params(message.chat.id, [9], [0])
    elif text == button[15]:
        user.wait_name = False
        send_with_params(message.chat.id, [10], [0])
    elif text == button[16]:
        user.wait_name = False
        send_with_params(message.chat.id, [11], [0])
    elif text == button[17]:
        user.wait_name = False
        send_with_params(message.chat.id, [12], [0])
    elif text == button[18]:
        user.wait_name = False
        send_with_params(message.chat.id, [14], [0])
    else:
        if user.wait_name:
            user.wait_name = False
            user.full_name = text

            send_with_params(message.chat.id, [15], [0])

        else:
            send_with_params(message.chat.id, [0], [0])

    today_users[message.from_user.username] = user

bot.polling(none_stop = True, interval = 0)

send_users()