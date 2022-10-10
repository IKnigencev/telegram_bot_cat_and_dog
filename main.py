import logging
import os
from dotenv import load_dotenv

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
URL_CATS = 'https://api.thecatapi.com/v1/images/search'
URL_DOGS = 'https://api.thedogapi.com/v1/images/search'


def get_cats_image():
    '''Обращение к внешнему API для получения фото кошки.'''
    try:
        response = requests.get(URL_CATS)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        response = requests.get(URL_DOGS)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_dogs_image():
    '''Обращение к внешнему API для получения фото собаки.'''
    try:
        response = requests.get(URL_DOGS).json()
    except Exception as error:
        logging.error(f'Ошибка при запросе к дополнительному API: {error}')
        response = requests.get(URL_CATS).json()

    random_dog = response[0].get('url')
    return random_dog


def new_dog(update, context):
    '''Функция получения новой фотографии собаки.'''
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_dogs_image())


def new_cat(update, context):
    '''Функиция получения новой фотографии кота.'''
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_cats_image())


def wake_up(update, context):
    '''Функция при активации бота.'''
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['/newcat', '/newdog']],
        resize_keyboard=True
    )

    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Посмотри, какого котика я тебе нашёл'.format(name),
        reply_markup=button
    )

    context.bot.send_photo(chat.id, get_cats_image())


def main():
    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))
    updater.dispatcher.add_handler(CommandHandler('newdog', new_dog))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
