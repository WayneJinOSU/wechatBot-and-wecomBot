# -*- coding: utf-8 -*-
import copy
from chatbot.bot_manager import bot_manager
from data.data import Query, QA, WecomAppClient
import asyncio
from common.log import logger
import sys
import json
from service.general_service import Service

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from cache.cache_mng import cache_mng, wechatConversationManager
import os


class WecomService(Service):
    def __init__(self):
        super().__init__()
        self.__name__ = "wecom_service"
        self.cache_mng = cache_mng
        self.wecom_conversation_mng = wechatConversationManager
        dir_path = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))
        self.path = os.path.join(dir_path, "config/wecom.json")
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.wecom_config = WecomAppClient(
                company_id=data["company_id"],
                client_app_token=data["client_app_token"],
                client_aes_key=data["client_aes_key"]
            )

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

    async def prepare_query(self) -> WecomAppClient:
        return self.wecom_config

    async def process(self, data: Query):
        message = await self.pre_process(data)
        dialogue, reply = await bot_manager.send_message(link_ai=self.link_ai,
                                                         message=message,
                                                         question=data.message,
                                                         system_role=self.prompt_engineer["system_role"]
                                                         )

        self.wechat_conversation_mng.update_conversation(user_id=data.from_user_id, dialogue=dialogue)
        return reply


wecomServiceMng = WecomService()
