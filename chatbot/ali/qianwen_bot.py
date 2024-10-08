# encoding:utf-8

from chatbot.bot import Bot
from common.log import logger
from config.config import Configure
from openai import *
import asyncio


# OpenAI对话模型API (可用)
class AsyncQianWenBot(Bot):
    def __init__(self, config):
        super().__init__()
        # set the default api_key
        self.api_key = config['API_KEY']
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.args = {
            "model": config.get("MODEL") or "qwen-plus",  # 对话模型的名称
            "temperature": config.get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "top_p": config.get("top_p", 1),
            "max_tokens": config.get("max_tokens", 2000),
            "request_timeout": config.get("request_timeout", 120),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
        }

    async def reply_text(self, message, system_role="", retry_count=0) -> dict:
        """
        call openai's ChatCompletion to get the answer
        :param system_role:
        :param session: a conversation session
        :param session_id: session id
        :param retry_count: retry count
        :return: {}
        """
        try:
            completion = await self.client.chat.completions.create(
                model=self.args['model'],  # "moonshot-v1-8k",
                messages=[
                    {
                        "role": "system",
                        "content": system_role,
                    },
                    {"role": "user", "content": "{}".format(message)}
                ],
                temperature=self.args['temperature'],
                top_p=self.args['top_p'],
                timeout=300,
                max_tokens=self.args['max_tokens']
            )
            logger.info("[QWEN]: the response is {}".format(completion))
            return {
                "total_tokens": completion.usage.total_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "content": completion.choices[0].message.content,
                "status": 1
            }

        except Exception as e:
            logger.warn(e)
            need_retry = retry_count < 2
            result = {"total_tokens": 0, "completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if isinstance(e, RateLimitError):
                logger.warn("[QWEN] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"

            elif isinstance(e, Timeout):
                logger.warn("[QWEN] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"

            elif isinstance(e, APIError):
                logger.warn("[QWEN] Bad Gateway: {}".format(e))
                result["content"] = "请再问我一次"

            elif isinstance(e, APIConnectionError):
                logger.warn("[QWEN] APIConnectionError: {}".format(e))
            else:
                logger.exception("[QWEN] Exception: {}".format(e))
                need_retry = False

            if need_retry:
                logger.warn("[QWEN] 第{}次重试".format(retry_count + 1))
                return await self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                result['status'] = 0
                return result


class QianWenBot(Bot):
    def __init__(self, config):
        super().__init__()
        # set the default api_key
        self.api_key = config['API_KEY']
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.args = {
            "model": config.get("MODEL") or "qwen-plus",  # 对话模型的名称
            "temperature": config.get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "top_p": config.get("top_p", 1),
            "max_tokens": config.get("max_tokens", 2000),
            "request_timeout": config.get("request_timeout", 120),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
        }

    def reply_text(self, message, system_role="", retry_count=0) -> dict:
        """
        call openai's ChatCompletion to get the answer
        :param system_role:
        :param session: a conversation session
        :param session_id: session id
        :param retry_count: retry count
        :return: {}
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.args['model'],  # "moonshot-v1-8k",
                messages=[
                    {
                        "role": "system",
                        "content": system_role,
                    },
                    {"role": "user", "content": "{}".format(message)}
                ],
                temperature=self.args['temperature'],
                top_p=self.args['top_p'],
                timeout=300,
                max_tokens=self.args['max_tokens']
            )
            logger.info("[QWEN]: the response is {}".format(completion))
            return {
                "total_tokens": completion.usage.total_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "content": completion.choices[0].message.content,
                "status": 1
            }

        except Exception as e:
            logger.warn(e)
            need_retry = retry_count < 2
            result = {"total_tokens": 0, "completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if isinstance(e, RateLimitError):
                logger.warn("[QWEN] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"

            elif isinstance(e, Timeout):
                logger.warn("[QWEN] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"

            elif isinstance(e, APIError):
                logger.warn("[QWEN] Bad Gateway: {}".format(e))
                result["content"] = "请再问我一次"

            elif isinstance(e, APIConnectionError):
                logger.warn("[QWEN] APIConnectionError: {}".format(e))
            else:
                logger.exception("[QWEN] Exception: {}".format(e))
                need_retry = False

            if need_retry:
                logger.warn("[QWEN] 第{}次重试".format(retry_count + 1))
                return self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                result['status'] = 0
                return result
