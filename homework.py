import exceptions
import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        logger.info('Отправка сообщения.')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Сообщение отправлено.')
    except exceptions.SendMessageFailureException:
        message = 'Сообщение не отправлено.'
        raise exceptions.SendMessageFailureException(message)


def get_api_answer(current_timestamp):
    """Запрос к ENDPOINT."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except exceptions.ResponseStatusException:
        message = 'Сбой запроса к ENDPOINT.'
        raise exceptions.ResponseStatusException(message)
    if response.status_code != HTTPStatus.OK:
        raise SystemError(f'Ошибка: {response.reason}; '
                          f'Код: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверка ответа на корректность."""
    keys = ['current_date', 'homeworks']

    if not isinstance(response, dict):
        message = (f'Ответ является {type(response)}, а не словарем')
        raise TypeError(message)

    try:
        homeworks = response.get('homeworks')
    except KeyError as error:
        message = f'Ошибка доступа: {error}'
        raise exceptions.CheckResponseException(message)

    if keys[0] not in response.keys() and keys[1] not in response.keys():
        empty_key_list = []
        for key in keys:
            if key not in response.keys():
                empty_key_list.append(key)
        message = (f'Отсутствует: {",".join(empty_key_list)}')
        raise exceptions.CheckResponseException(message)

    if homeworks is None:
        message = 'Ответ не содежит словаря с домашники работами.'
        raise exceptions.CheckResponseException(message)

    if not isinstance(homeworks, list):
        message = 'Ответ не представлен списком'
        logger.error(message)
        raise exceptions.CheckResponseException(message)

    if len(homeworks) == 0:
        message = 'За последнее время нет домашних работ.'
        raise exceptions.CheckResponseException(message)

    return homeworks


def parse_status(homework):
    """Извлечение статуса о домашней работе."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_name is None:
        message = 'Ошибка доступа по ключу homework_name'
        raise KeyError(message)

    if homework_status is None:
        message = 'Ошибка доступа по ключу status'
        raise KeyError(message)

    verdict = HOMEWORK_STATUSES.get(homework_status)

    if verdict is None:
        message = 'Неизвестный статус домашней работы.'
        raise exceptions.UnknownHWStatusException(message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка переменных окружения."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        message = 'Переменная среды не найдена.'
        logger.critical(message)
        raise sys.exit(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    homework_old_data = {
        'homework_name': '',
        'message': ''
    }

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if message != homework_old_data['message']:
                send_message(bot, message)
                homework_old_data = {
                    'homework_name': homework[0]['homework_name'],
                    'message': message
                }
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            message = f'Сбой в работе программы: {error}'
            if message != homework_old_data['message']:
                homework_old_data['message'] = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format=('%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - '
                '%(message)s'),
        level=logging.INFO,
        filename="program.log",
        filemode="w",
    )
    main()
