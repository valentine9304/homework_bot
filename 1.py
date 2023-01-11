def send_message(bot, message):

    try:

        logger.info('Мы начали отправку сообщения в Telegram')
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
    except TelegramError:
    message = f'Сообщение в чат {TELEGRAM_CHAT_ID} не отправлено!'
    raise TelegramSendError(message)
