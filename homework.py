import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import HTTPStatusError, EndpointError, TelegramIDError
from exceptions import ReponseKeyError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    list_tokens = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    return all(list_tokens)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.debug(f'Бот отправил сообщение {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения. {error}')
        raise TelegramIDError(error)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise HTTPStatusError(homework_statuses)
    except Exception as error:
        raise EndpointError(error, ENDPOINT)
    return homework_statuses.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not response:
        message = 'Ответ от АПИ пришёл пустым словарём'
        logging.error(message)
        raise KeyError(message)

    if not isinstance(response, dict):
        message = 'Ответ от АПИ пришёл не в словаре.'
        logging.error(message)
        raise TypeError(message)

    if 'homeworks' not in response:
        message = 'В ответе от АПИ нет ожидаемого ключа.'
        logging.error(message)
        raise ReponseKeyError(message)

    if not isinstance(response.get('homeworks'), list):
        message = 'В словаре нет Списка.'
        logging.error(message)
        raise TypeError(message)

    return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    if not homework.get('homework_name'):
        homework_name = 'noname'
        message = 'Отсутствует имя домашней работы.'
        logging.warning(message)
        raise KeyError(message)
    else:
        homework_name = homework.get('homework_name')

    homework_status = homework.get('status')
    if 'status' not in homework:
        message = 'Отсутстует ключ homework_status.'
        logging.error(message)
        raise KeyError(message)

    if homework_status not in HOMEWORK_VERDICTS:
        message = 'Такого статуса домашней работы нет'
        logging.error(message)
        raise KeyError(message)
    else:
        verdict = HOMEWORK_VERDICTS.get(homework_status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствует токен')
        sys.exit("Программа  остановлена")

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    prev_error = None

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('Нет проверенных домашний работ.')
            for homework in homeworks:
                message = parse_status(homework)
                if homework:
                    send_message(bot, message)

        except Exception as error:
            if prev_error != error:
                send_message(bot, error)
                prev_error = error
        else:
            prev_error = None
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.FileHandler('log.txt')]
    )
    main()
