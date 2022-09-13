class CheckResponseException(Exception):
    """Неверный формат ответа API."""

    pass


class EmptyHWNameOrStatus(Exception):
    """Значение None имени или статуса домашней работы."""

    pass


class IncorrectResponseException(Exception):
    """Некорректный ответа API."""

    pass


class NoRequiredTokensException(Exception):
    """Отсутствие необходимых переменных среды."""

    pass


class ResponseStatusException(Exception):
    """Сбой запроса к API."""

    pass


class SendMessageFailureException(Exception):
    """Исключение отправки сообщения."""

    pass


class UnknownHWStatusException(Exception):
    """Неизвестный статус домашней работы."""

    pass
