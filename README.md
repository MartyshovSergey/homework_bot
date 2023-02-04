# Бот-ассистент.

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.

### Технологии:

- Python 3.7
- Python-telegram-bot
- SimpleJWT

### Принцип работы API:

Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

- работа принята на проверку 
- работа возвращена для исправления ошибок 
- работа принята 

### Что делает бот:

- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
- логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.


### Запуск проекта:

У API Практикум.Домашка есть лишь один эндпоинт:

https://practicum.yandex.ru/api/user_api/homework_statuses/

и доступ к нему возможен только по токену.

Получить токен можно по [ссылке](https://oauth.yandex.ru/verification_code#access_token=y0_AgAAAAAR_U-IAAYckQAAAADahbMdmXDkOZsnSlC--dBaqVZ_r2J7ui4&token_type=bearer&expires_in=2592000), он нам пригодится позже.

- Клонировать репозиторий и перейти в него в командной строке.
- Установить и активировать виртуальное окружение c Python 3.7 (python не ниже
  версии 3.7):

```
python3 -3.7 -m venv venv
```

```
source venv/bin/activate
```

- Установить зависимости из файла requirements.txt

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
- В консоле импортируем токены для Яндекс.Практикум и для Телеграмм:

```
export PRACT_TOKEN=<PRACTICUM_TOKEN>
export TELEGA_TOKEN=<TELEGRAM_TOKEN>
export TELEGA_ID_TOKEN=<CHAT_ID> 
```
