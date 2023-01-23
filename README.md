# Бот-ассистент.

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.

### Технологии:

- Python 3.7
- Python-telegram-bot
- SimpleJWT

### Запуск проекта:

У API Практикум.Домашка есть лишь один эндпоинт:

https://practicum.yandex.ru/api/user_api/homework_statuses/

и доступ к нему возможен только по токену.

Получить токен можно по [ссылке](https://oauth.yandex.ru/verification_code#access_token=y0_AgAAAAAR_U-IAAYckQAAAADahbMdmXDkOZsnSlC--dBaqVZ_r2J7ui4&token_type=bearer&expires_in=2592000,)он нам пригодится позже.

### Принцип работы API:

Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

| работа принята на проверку |
| работа возвращена для исправления ошибок |
| работа принята |


