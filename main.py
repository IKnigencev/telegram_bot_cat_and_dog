import logging
import os
from dotenv import load_dotenv

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from googletrans import Translator


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
NASA_TOKEN = os.getenv('NASA_TOKEN')
URL_CATS = 'https://api.thecatapi.com/v1/images/search'
URL_DOGS = 'https://api.thedogapi.com/v1/images/search'
URL_COMPLIMENT = 'https://complimentr.com/api'
URL_NASA = 'https://api.nasa.gov/planetary/apod?{NASA_TOKEN}'

translator = Translator()


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


def get_compliment():
    '''Обращение к API для получения фото собачки.'''
    try:
        response = requests.get(URL_COMPLIMENT).json()
        rendom_compliment = response.get('compliment')
        result = translator.translate(rendom_compliment, src='en', dest='ru')
        return result
    except Exception as error:
        logging.error(f'Ошибка при запросе к API комплиментов: {error}')
        response = requests.get(URL_CATS).json()
        random_compliment = response[0].get('url')
        return random_compliment


def get_nasa_api():
    '''Обращение к API для получения фото и описания космоса.'''
    try:
        response = requests.get(URL_NASA, headers=NASA_TOKEN).json()
        title = response.get('title')
        image = response.get('url')
        return title, image
    except Exception as error:
        logging.error(f'Ошибка при запросе к API NASA: {error}')
        response = requests.get(URL_CATS).json()
        title = 'Не нашли картинку космоса, но есть котики!'
        random_cats = response[0].get('url')
        return title, random_cats


def new_dog(update, context):
    '''Функция получения новой фотографии собаки.'''
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_dogs_image())


def new_cat(update, context):
    '''Функция получения новой фотографии кота.'''
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_cats_image())


def new_compliment(update, context):
    '''Функция получения нового комплимента.'''
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_compliment())


def new_space(update, context):
    '''Функция получения данных о космосе.'''
    chat = update.effective_chat
    title, image = get_nasa_api()
    context.bot.send_message(chat.id, title)
    context.bot.send_photo(chat.id, image)


def wake_up(update, context):
    '''Функция при активации бота.'''
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['/newcat', '/newdog'], ['/newcompliment'], ['/newnasaimage']],
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
    updater.dispatcher.add_handler(
        CommandHandler('newcompliment', new_compliment)
    )
    updater.dispatcher.add_handler(CommandHandler('newnasaimage', new_space))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
