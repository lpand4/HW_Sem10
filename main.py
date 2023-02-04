import logging
import requests
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.dispatcher.webhook import SendMessage
from datetime import datetime
from dataclasses import dataclass
from urllib.request import urlopen
import json

API_TOKEN = "6164207847:AAGkhKgLMDVy_vAbsDU-hYiwacBc7tIcxXw"
WEATHER_API_TOKEN = '2a24b8368fceb5855699a102d09044d6'
CURRENT_WEATHER_API_CALL = ('https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid='
                            + WEATHER_API_TOKEN + '&units=metric')


# Координаты пользователя
@dataclass(slots=True, frozen=True)
class Coordinates:
    latitude: float
    longitude: float
    city: str


# Погода
@dataclass(slots=True, frozen=True)
class Weather:
    city: str
    temperature: float
    temperature_feeling: float
    weather: str
    wind_speed: float


# Перемещаем нужные значения в класс координат
def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Share Position", request_location=True)
    keyboard.add(button)
    return keyboard


def get_data_weather(latitude, longitude):
    url = CURRENT_WEATHER_API_CALL.format(latitude=latitude, longitude=longitude)
    data = urlopen(url)
    return json.load(data)


# Перемещаем значения погоды в класс погоды
def get_weather(latitude, longitude) -> Weather:
    data_weather_dict = get_data_weather(latitude, longitude)
    city1 = data_weather_dict['name']
    temperatue1 = data_weather_dict['main']['temp']
    temperatue_feeling1 = data_weather_dict['main']['feels_like']
    weather1 = str(data_weather_dict['weather'][0]['description']).capitalize()
    wind_speed1 = data_weather_dict['wind']['speed']
    return Weather(city=city1, temperature=temperatue1, temperature_feeling=temperatue_feeling1, weather=weather1,
                   wind_speed=wind_speed1)


# Bot
logging.basicConfig(level=logging.INFO, filename="log.csv")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)


# /Bot


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_lastname = message.from_user.last_name
    user_bot = message.from_user.is_bot
    user_message = message.text
    logging.info(f'{datetime.now()} - {user_id}|{user_name} {user_lastname} - {user_message}|{user_bot}')
    await message.reply(f'Hi, {user_name}!')
    btns = types.ReplyKeyboardMarkup(row_width=3)
    btn_weather = types.KeyboardButton('/weather', request_location=True)
    btn_film = types.KeyboardButton('/film')
    btn_out = types.KeyboardButton('/quit')

    btns.add(btn_weather, btn_film, btn_out)
    await bot.send_message(user_id, 'Выберите что Вас интересует:', reply_markup=btns)


@dp.message_handler(content_types=['location'])
async def weather_handler(message: types.Message):
    lat = message.location.latitude
    long = message.location.longitude
    # noinspection PyTypeChecker
    weather = get_weather(latitude=lat, longitude=long)
    message_text = f'Город: {weather.city}\nТемпература воздуха: {weather.temperature}\n' \
                   f'Ощущается как: {weather.temperature_feeling}\nПогода: {weather.weather}\n' \
                   f'Скорость ветра: {weather.wind_speed}\n'
    logging.info(f'{datetime.now()} - Пользователь {message.from_user.full_name}\n {message_text}')

    return SendMessage(message.chat.id, message_text)


@dp.message_handler(commands=['film'])
async def film_handler(message: types.Message):
    return SendMessage(message.chat.id, 'Данная функция находится в процессе разработки')


@dp.message_handler(commands=['quit'])
async def quit_handler(message: types.Message):
    await bot.send_message(message.from_user.id, 'See u later! Goodbye', reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
