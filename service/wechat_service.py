import os
from enum import Enum
from threading import Thread
from qrcode.main import QRCode
from service.dependencies.itchat.content import INCOME_MSG
from common.log import logger
from service.dependencies import itchat
from data.data import Conversation, QA
from service.models.wechat import MessageModel, MessageTypeEnum
from service.wechat.base import filter_message
from cache.cache_mng import cache_mng
import json
from chatbot.bot_manager import bot_manager
from cache.cache_mng import wechatConversationManager


@filter_message(model=MessageModel)
def handle_single(message: MessageModel):
    """
    监听私聊消息
    :param message:
    :return:
    """
    if message.type == MessageTypeEnum.TEXT:
        reply = wechatService.process(data=message)
        itchat.send(reply, toUserName=message.from_user_id)


class WeChatBot(Thread):
    class ContextType(Enum):
        TEXT = 1  # 文本消息
        VOICE = 2  # 音频消息
        IMAGE = 3  # 图片消息
        FILE = 4  # 文件信息
        VIDEO = 5  # 视频信息
        SHARING = 6  # 分享信息
        IMAGE_CREATE = 10  # 创建图片命令
        ACCEPT_FRIEND = 19  # 同意好友请求
        JOIN_GROUP = 20  # 加入群聊
        PATPAT = 21  # 拍了拍
        FUNCTION = 22  # 函数调用
        EXIT_GROUP = 23  # 退出

    def __init__(self):
        super().__init__()
        self.current_dir = os.path.dirname(__file__)
        self.parent_dir = os.path.abspath(os.path.join(self.current_dir, os.pardir))
        self.grandparent_dir = os.path.abspath(os.path.join(self.parent_dir, os.pardir))

        # 将 ContextType 枚举封装为类的属性
        self.context_type = self.ContextType

        self.status_path = "itchat.pkl"

    def qrcode_callback(self, uuid, status, qr_code):
        url = f"https://login.weixin.qq.com/l/{uuid}"
        if status == "0":
            logger.info("QR code scanned")
            qr = QRCode(border=1)
            qr.add_data(url)
            qr.make(fit=True)
            qr.print_ascii(invert=True)
        elif status == "200":
            logger.info("QR code confirmed")
        elif status == "201":
            logger.info("QR code scanned, waiting for confirmation")
        else:
            logger.info(f"QR code status: {status}")

    def login_callback(self, *args, **kwargs):
        user_id = itchat.instance.storageClass.userName
        name = itchat.instance.storageClass.nickName
        logger.info(f"Wechat login success, user_id: {user_id}, nickname: {name}")

    def logout_callback(self, *args, **kwargs):
        user_id = itchat.instance.storageClass.userName
        name = itchat.instance.storageClass.nickName
        logger.info(f"Wechat logout success, user_id: {user_id}, nickname: {name}")

    def run(self):
        # 修改断线超时时间
        itchat.msg_register(INCOME_MSG)(handle_single)
        itchat.instance.receivingRetryCount = 600
        itchat.auto_login(
            enableCmdQR=2,
            hotReload=False,
            statusStorageDir=self.status_path,
            qrCallback=self.qrcode_callback,
            exitCallback=self.logout_callback,
            loginCallback=self.login_callback,
        )
        # 启动消息监听
        itchat.run()


class WechatService:
    def __init__(self):
        self.cache_mng = cache_mng
        dir_path = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
        self.path = os.path.join(dir_path, "config/prompt.json")
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.prompt_engineer = data

        dir_path = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
        self.path = os.path.join(dir_path, "config/work.json")
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.link_ai = data["work"]

        self.wechat_conversation_mng = wechatConversationManager

    def __get_knowledge_lib__(self, data):
        return "rag"

    def get_knowledge_lib(self, data: MessageModel):
        """
        :param data:
        :return:
        获取知识库，包括语义处理
        """
        return "rag"

    def get_conversation_cache(self, user_id: str):

        return ""

    def get_history_dialogue(self, data: MessageModel):
        """
        :param data: Query
        :return:

        获取历史对话
        """
        conversation = self.wechat_conversation_mng.get_conversation(user_id=data.from_user_id)
        dialogue = ""
        if conversation:
            for index, q2a in enumerate(conversation.Q2A):
                dialogue += "{}\n".format(index + 1, q2a.Q)
                dialogue += "{}\n".format(index + 1, q2a.A)

            return dialogue
        else:
            return None

    def organize_query(self,
                       message: MessageModel,
                       lib: str,
                       history_dialogue: str
                       ):
        """
        :param message:问题
        :param lib:知识库
        :param history_dialogue:历史对话
        :return:

        组织询问内容
        """
        content = ""
        if lib:
            content += "[知识库]： {{{}}}。\n".format(lib)
        if history_dialogue:
            content += "[历史对话]: {{{}}} \n。".format(history_dialogue)

        if message:
            content += "请你根据以上设定,要求和历史对话完成我接下来的询问. \n" \
                       "我的问题是：{}。".format(message.content)
        return content

    def pre_process(self, data: MessageModel):
        """
        :param data: 请求内容
        :return:
        """
        knowledge_lib, history_dialogue = self.get_knowledge_lib(data), self.get_history_dialogue(data)
        content = self.organize_query(message=data,
                                      lib=knowledge_lib,
                                      history_dialogue=history_dialogue
                                      )
        return content

    def process(self, data: MessageModel):
        content = self.pre_process(data=data)
        dialogue, reply = bot_manager.send_message(link_ai=self.link_ai,
                                                   message=content,
                                                   question=data,
                                                   system_role=self.prompt_engineer["system_role"]
                                                   )
        self.wechat_conversation_mng.update_conversation(user_id=data.from_user_id, dialogue=dialogue)
        return reply['content']


wechatService = WechatService()
wechat_bot = WeChatBot()
