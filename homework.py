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


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Сообщение отправлено.')
    except exceptions.SendMessageFailureException:
        logger.error('Сообщение не отправлено.')


def get_api_answer(current_timestamp):
    """Запрос к ENDPOINT."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except exceptions.ResponseStatusException:
        logger.error('Сбой запроса к ENDPOINT.')
    if response.status_code != HTTPStatus.OK:
        message = 'Сбой запроса к ENDPOINT.'
        logger.error(message)
        raise exceptions.ResponseStatusException(message)
    return response.json()


def check_response(response):
    """Проверка ответа на корректность."""
    try:
        homeworks = response['homeworks']
    except KeyError as error:
        message = f'Ошибка доступа: {error}'
        logger.error(message)
        raise exceptions.CheckResponseException(message)

    if homeworks is None:
        message = 'Ответ не содежит словаря с домашники работами.'
        logger.error(message)
        raise exceptions.CheckResponseException(message)
    if len(homeworks) == 0:
        message = 'За последнее время нет домашних работ.'
        logger.error(message)
        raise exceptions.CheckResponseException(message)
    if not isinstance(homeworks, list):
        message = 'Ответ не представлен списком'
        logger.error(message)
        raise exceptions.CheckResponseException(message)

    return homeworks


def parse_status(homework):
    """Извлечение статуса о домашней работе."""
    try:
        homework_name = homework.get('homework_name')
    except KeyError as error:
        message = f'Ошибка доступа по ключу homework_name: {error}'
        logger.error(message)
    try:
        homework_status = homework.get('status')
    except KeyError as error:
        message = f'Ошибка доступа по ключу status: {error}'
        logger.error(message)

    verdict = HOMEWORK_STATUSES[homework_status]

    if verdict is None:
        message = 'Неизвестный статус домашней работы.'
        logger.error(message)
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
        raise exceptions.NoRequiredTokensException(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ex_status = None
    ex_error = None

    while True:
        try:
            response = get_api_answer(current_timestamp)
        except exceptions.IncorrectResponseException as error:
            if str(error) != ex_error:
                ex_error = str(error)
                send_message(bot, error)
            logger.error(error)
            time.sleep(RETRY_TIME)
            continue

        try:
            homework = check_response(response)
            homework_status = homework[0].get('status')

            if homework_status != ex_status:
                ex_status = homework_status
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logger.debug('Обновлений у статуса домашней работы нет.')

            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if ex_error != str(error):
                ex_error = str(error)
                send_message(bot, message)
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
