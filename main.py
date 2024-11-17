import os
from telebot import TeleBot, types
from dotenv import load_dotenv, find_dotenv
import logging
from logging import config
from logging_config import dict_config
import time


# В файле .env
# BOT_KEY = 'Bot key'                   -- Ключ бота
# ADMIN_CHAT = '000000000/000000000'    -- Введите ID чатов админов через символ '/'

config.dictConfig(dict_config)
logger = logging.getLogger(__name__)


if not find_dotenv():
    logger.error('Файл .env не найден')
else:
    load_dotenv()


API_TOKEN = os.getenv('BOT_KEY')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT')
COMMANDS = ['start', 'admin', 'info']

try:
    bot = TeleBot(token=API_TOKEN)
except:
    logger.error('Нет токена для бота')



@bot.message_handler(commands=['start'])
def start_command(message):
    logger.info(f'Пользователь {message.from_user.first_name} (id:{message.from_user.id}) выполнил команду <start>')
    commands = ''
    for command in COMMANDS:
        commands += f'\n/{command}'
    if str(message.from_user.id) in ADMIN_CHAT_ID:
        welcome_text = ("Вы являетесь АДМИНИСТРАТОРОМ!")
    else:
        welcome_text = ("Вы являетесь ПОЛЬЗОВАТЕЛЕМ!")
    bot.send_message(message.chat.id, f'"Привет! Это коммуникационный бот !\n{welcome_text}{commands}')


@bot.message_handler(commands=['info'])
def start_command(message):
    # print(message.from_user.__get_attr__)
    # print(str(message.from_user))
    logger.info(f'Пользователь {message.from_user.first_name} (id:{message.from_user.id}) выполнил команду <info>')
    if str(message.from_user.id) in ADMIN_CHAT_ID:
        welcome_text = ("Вы являетесь АДМИНИСТРАТОРОМ!")
    else:
        welcome_text = ("Вы являетесь ПОЛЬЗОВАТЕЛЕМ!")
    # info = ''
    # for i_item, i_result in json.loads(str(message.from_user)).items():
    #     if i_result:
    #         info += f'\n{i_item}: {i_result}'

    info = welcome_text + (f'\nid: {message.from_user.id}'
                           f'\nname: {message.from_user.first_name}'
                           f'\nlast_name: {message.from_user.last_name}'
                           f'\nuser_name: {message.from_user.username}'
                           f'\nbot: {message.from_user.is_bot}'
                           f'\nlanguage_code: {message.from_user.language_code}')
    bot.send_message(message.chat.id, info)


@bot.message_handler(commands=['admin'])
def admin_command(message):
    logger.info(f'Пользователь {message.from_user.first_name} (id:{message.from_user.id}) выполнил команду <admin>')
    if str(message.from_user.id) in ADMIN_CHAT_ID:
        rep = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton('Добавить', callback_data='add_ad')
        button2 = types.InlineKeyboardButton('Удалить', callback_data='dell_ad')
        rep.add(button1, button2)
        admins = ''
        for ad in ADMIN_CHAT_ID.split('/'):
            if ad:
                admins += f'\nid: {ad}'
        welcome_text = (f'Список админов:{admins}')
        bot.send_message(message.chat.id, welcome_text, reply_markup=rep)
    else:
        welcome_text = ("Напишите сообщение админу:")
        bot.register_next_step_handler(message, send_admin_message)
        bot.send_message(message.chat.id, welcome_text)


@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(call):
    if call.message:

        if call.data == "dell":
            bot.delete_message(call.message.chat.id, call.message.id)
        elif call.data == 'add_ad':
            msg = bot.send_message(call.message.chat.id, f'Введите id:')
            bot.register_next_step_handler(msg, admin_add)
        elif call.data == 'dell_ad':
            msg = bot.send_message(call.message.chat.id, f'Введите id:')
            bot.register_next_step_handler(msg, admin_dell)
        else:
            msg = bot.send_message(call.message.chat.id, f'Введите ответ для {call.message.from_user.first_name}:')
            bot.register_next_step_handler(msg, answer, call.data, call.from_user.username)
            bot.delete_message(call.message.chat.id, call.message.id)


def answer(message, data, name):
    bot.delete_message(message.chat.id, message.id)
    logger.info(f'Ответ от администратора отправлен пользователю {name}')
    bot.send_message(data, f"Ответ от админа:\n***********\n{message.text}")
    bot.send_message(message.chat.id, f'Ответ отправлен пользователю {name}')


def admin_add(message):
    if message.text.isdigit():
        global ADMIN_CHAT_ID
        logger.info(f'Пользователь {message.text} добавлен к администраторам')
        ADMIN_CHAT_ID += f'{message.text}/'
        bot.send_message(message.chat.id, f'Пользователь {message.text} добавлен к администраторам')
    else:
        bot.send_message(message.chat.id, f'Ошибка ввода id')


def admin_dell(message):
    if message.text.isdigit():
        global ADMIN_CHAT_ID
        if message.text in ADMIN_CHAT_ID:
            new_admin = ADMIN_CHAT_ID.replace(f'{message.text}/', '')
            logger.info(f'Пользователь {message.text} удален из администраторов')
            bot.send_message(message.chat.id, f'Пользователь {message.text} удален из администраторов')
            ADMIN_CHAT_ID = new_admin
        else:
            bot.send_message(message.chat.id, f'Такого админа нет!')
    else:
        bot.send_message(message.chat.id, f'Ошибка ввода id')
    # new_admin = ''
    # for ad in ADMIN_CHAT_ID.split('/'):
    #     if ad != message.text and ad:
    #         new_admin += f'{ad}/'
    #     else:
    #         logger.info(f'Пользователь {message.text} удален из администраторов')
    #         bot.send_message(message.chat.id, f'Пользователь {message.text} удален из администраторов')
    # ADMIN_CHAT_ID = new_admin


# @bot.message_handler()
def send_admin_message(message):

    if not str(message.from_user.id) in ADMIN_CHAT_ID:
        bot.reply_to(message, "Сообщение отправлено администратору")
        logger.info(
            f'Пользователь {message.from_user.first_name} (id:{message.from_user.id}) отправил сообщение админу')
        for admin in ADMIN_CHAT_ID.split('/'):
            if admin:
                rep = types.InlineKeyboardMarkup(row_width=2)
                button1 = types.InlineKeyboardButton('Ответить', callback_data=str(message.chat.id))
                button2 = types.InlineKeyboardButton('Удалить', callback_data='dell')
                rep.add(button1, button2)
                bot.send_message(admin, f'Сообщение: \n*********** \n{message.text}\n*********** \n'
                                        f'Пользователь: @{message.from_user.first_name} ('
                                        f'id:{message.from_user.id})',
                                 reply_markup=rep)


def main():
    while True:
        try:
            logger.info(f'== Бот запущен ==')
            bot.polling(none_stop=True)
        except Exception as ex:
            time.sleep(2)


if __name__ == "__main__":
   main()
