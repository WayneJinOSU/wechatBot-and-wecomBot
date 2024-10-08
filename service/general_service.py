# -*- coding: utf-8 -*-
from chatbot.bot_manager import async_bot_manager
from data.data import Query, Message, Conversation, QA, CacheSignal
import asyncio
from common.log import logger
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from cache.cache_mng import cache_mng
import os
import json


class Service:
    def __init__(self):
        self.__name__ = "service"
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

    async def __get_knowledge_lib__(self, data):
        return "rag"

    async def get_knowledge_lib(self, data: Query):
        """
        :param data:
        :return:
        获取知识库，包括语义处理
        """
        return "rag"

    async def get_history_dialogue(self, data: Query):
        """
        :param data: Query
        :return:

        获取历史对话
        """
        conversation = await self.cache_mng.get_conversation_cache(user_id=data.userId)
        dialogue = ""
        if conversation:
            for index, q2a in enumerate(conversation.Q2A):
                dialogue += "{}\n".format(index + 1, q2a.Q)
                dialogue += "{}\n".format(index + 1, q2a.A)

            return dialogue
        else:
            return None

    async def organize_query(self,
                             message: Message,
                             lib: str,
                             history_dialogue: Conversation
                             ):
        """
        :param message:问题
        :param lib:知识库
        :param app_detail:app设定
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

    async def pre_process(self, data: Query):
        """
        :param data: 请求内容
        :return:
        """
        self.gather = asyncio.gather(self.get_knowledge_lib(data),
                                     self.get_history_dialogue(data))
        tasks = self.gather
        knowledge_lib, history_dialogue = await tasks
        content = await self.organize_query(message=data.message,
                                            lib=knowledge_lib,
                                            history_dialogue=history_dialogue,
                                            )

        return content

    def post_process(self, reply: dict):
        """
        :param reply: 来自于gpt的完整回复
        :return:

        后处理的得到图像id
        """
        reply['img_ids'] = []
        return reply

    async def update_conversation(self, data: Query, dialogue: QA, memory_loop: int):
        """
        :param data: 请求内容
        :param dialogue: 单次对话
        :return:

        在redis中更新历史对话
        """
        conversation = await self.cache_mng.get_conversation_cache(user_id=data.userId)
        if conversation:
            conversation.Q2A.append(dialogue)
            conversation.Q2A = conversation.Q2A[-1 * memory_loop:]
            await self.cache_mng.set_conversation_cache(data.userId, conversation)
        else:
            conversation = Conversation(Q2A=[dialogue])
            await self.cache_mng.set_conversation_cache(data.userId, conversation)

    async def process(self, data: Query):
        message = await self.pre_process(data)
        dialogue, reply = await async_bot_manager.send_message(link_ai=self.link_ai,
                                                         message=message,
                                                         question=data.message,
                                                         system_role=self.prompt_engineer["system_role"]
                                                         )
        await self.update_conversation(data=data, dialogue=dialogue, memory_loop=10)
        return reply

    async def cleanCache(self, data: CacheSignal):
        """
        :param data: 请求内容
        :param dialogue: 单次对话
        :return:

        删除用户对话缓存
        """
        is_success = await self.cache_mng.clean_users_cache(user_id=data.userId)
        return is_success


serviceMng = Service()

