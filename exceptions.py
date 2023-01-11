class HTTPStatusError(Exception):
    def __init__(self, homework_statuses):
        message = (
            f'{homework_statuses.url} недоступен. '
            f'Код ответа API: {homework_statuses.status_code}]'
        )
        super().__init__(message)


class EndpointError(Exception):
    def __init__(self, error, ENDPOINT):
        message = (
            f'{ENDPOINT} недоступен. '
            f'Ошибка: {error}]'
        )
        super().__init__(message)


class TelegramIDError(Exception):
    def __init__(self, error):
        message = (
            f'Нет доступа к Профилю Telegram. '
            f'Ошибка: {error}]'
        )
        super().__init__(message)


class ReponseTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ReponseKeyError(Exception):
    def __init__(self, message):
        super().__init__(message)
