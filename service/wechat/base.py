import time
from functools import partial, wraps

from common.log import logger
from redis import Redis

from service.models.wechat import MessageModel


# 过滤过期消息
def filter_expired(message: MessageModel, expire_seconds=60):
    """
    过滤过期消息
    :param message:
    :param expire_seconds:
    :return:
    """
    if message.create_time:
        return int(message.create_time) < int(time.time() - expire_seconds)
    else:
        return 0


def filter_message(func=None, *, model=None, expire=True, repeat=True, expire_seconds=60):
    """
    过滤消息
    :param model:
    :param func:
    :param expire:
    :param repeat:
    :param expire_seconds:
    :return:
    """
    if func is None:
        return partial(filter_message, model=model, expire=expire, repeat=repeat, expire_seconds=expire_seconds)

    @wraps(func)
    def wrapper(msg):
        logger.info(f"Receive message: {msg}")
        message = model(**msg) if model else msg
        if expire and filter_expired(message, expire_seconds):
            return
        return func(message)

    return wrapper
