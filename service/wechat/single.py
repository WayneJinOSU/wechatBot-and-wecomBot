from common.log import logger

from service.dependencies import itchat
from service.models.wechat import MessageModel, MessageTypeEnum
from service.wechat.base import filter_message
from chatbot.bot_manager import bot_manager

# @itchat.msg_register(INCOME_MSG)



@filter_message(model=MessageModel)
def handle_single(message: MessageModel):
    """
    监听私聊消息
    :param message:
    :return:
    """
    logger.info(f"Message content: {message.content}")
    if message.type == MessageTypeEnum.TEXT:
        bot_manager.send_message()
        logger.info(res)
        logger.info(f"Text message: {message.content}")
        itchat.send(res, toUserName=message.from_user_id)
