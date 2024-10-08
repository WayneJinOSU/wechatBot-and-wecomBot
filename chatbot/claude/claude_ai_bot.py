from chatbot.bot import Bot
from common.log import logger
from openai import *
import requests
import json
import httpx


class AsyncClaudeBot(Bot):
    def __init__(self, config):
        super().__init__()
        self.api_key = config['API_KEY']
        self.args = {
            "model": config.get("MODEL") or "claude-3-opus-20240229",  # 对话模型的名称
            "temperature": config.get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "max_tokens": config.get("max_tokens", 4096),  # 回复最大的字符数
            "top_p": config.get("top_p", 1),
            "frequency_penalty": config.get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": config.get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": config.get("request_timeout", 120),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
        }

    async def reply_text(self, message, system_role="", retry_count=0) -> dict:
        """
        call openai's ChatCompletion to get the answer
        :param session: a conversation session
        :param session_id: session id
        :param retry_count: retry count
        :return: {}
        """
        try:
            url = "https://api.openai-hk.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "{}".format(self.api_key)
            }
            data = {
                "max_tokens": self.args['max_tokens'],
                "model": "{}".format(self.args['model']),
                "temperature": self.args['temperature'],
                "top_p": 1,
                "frequency_penalty": self.args['frequency_penalty'],
                "presence_penalty": self.args['presence_penalty'],
                "messages": [
                    {
                        "role": "system",
                        "content": "{}".format(system_role)
                    },
                    {"role": "user", "content": "{}".format(message)}
                ]
            }

            # data = copy.deepcopy(self.args)
            client = httpx.AsyncClient()
            response = await client.post(url, headers=headers, data=json.dumps(data).encode('utf-8'), timeout=300)
            # response = openai.ChatCompletion.create(api_key=self.api_key, messages=message, **self.args)
            response = json.loads(response.content.decode("utf-8"))
            logger.info("[CHATGPT]: the request is {}".format(data))
            logger.info("[CHATGPT]: the response is {}".format(response))
            print(response)
            if isinstance(response, dict):
                return {
                    "total_tokens": response["usage"]["total_tokens"],
                    "completion_tokens": response["usage"]["completion_tokens"],
                    "content": response['choices'][0]["message"]["content"],
                    "status": 1
                }

        except Exception as e:
            need_retry = retry_count < 2
            result = {"total_tokens": 0, "completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if isinstance(e, RateLimitError):
                logger.warn("[CHATGPT] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"

            elif isinstance(e, Timeout):
                logger.warn("[CHATGPT] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"

            elif isinstance(e, APIError):
                logger.warn("[CHATGPT] Bad Gateway: {}".format(e))
                result["content"] = "请再问我一次"

            elif isinstance(e, APIConnectionError):
                logger.warn("[CHATGPT] APIConnectionError: {}".format(e))
            else:
                logger.exception("[CHATGPT] Exception: {}".format(e))
                need_retry = False

            if need_retry:
                logger.warn("[CHATGPT] 第{}次重试".format(retry_count + 1))
                return await self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                result['status'] = 0
                return result


class ClaudeBot(Bot):
    def __init__(self, config):
        super().__init__()
        self.api_key = config['API_KEY']
        self.args = {
            "model": config.get("MODEL") or "claude-3-opus-20240229",  # 对话模型的名称
            "temperature": config.get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "max_tokens": config.get("max_tokens", 4096),  # 回复最大的字符数
            "top_p": config.get("top_p", 1),
            "frequency_penalty": config.get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": config.get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": config.get("request_timeout", 120),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
        }

    def reply_text(self, message, system_role="", retry_count=0) -> dict:
        """
        call openai's ChatCompletion to get the answer
        :param session: a conversation session
        :param session_id: session id
        :param retry_count: retry count
        :return: {}
        """
        try:
            url = "https://api.openai-hk.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "{}".format(self.api_key)
            }
            data = {
                "max_tokens": self.args['max_tokens'],
                "model": "{}".format(self.args['model']),
                "temperature": self.args['temperature'],
                "top_p": 1,
                "frequency_penalty": self.args['frequency_penalty'],
                "presence_penalty": self.args['presence_penalty'],
                "messages": [
                    {
                        "role": "system",
                        "content": "{}".format(system_role)
                    },
                    {"role": "user", "content": "{}".format(message)}
                ]
            }

            response = requests.post(url, headers=headers, data=json.dumps(data).encode('utf-8'), timeout=300)
            response = json.loads(response.content.decode("utf-8"))
            logger.info("[CHATGPT]: the request is {}".format(data))
            logger.info("[CHATGPT]: the response is {}".format(response))
            print(response)
            if isinstance(response, dict):
                return {
                    "total_tokens": response["usage"]["total_tokens"],
                    "completion_tokens": response["usage"]["completion_tokens"],
                    "content": response['choices'][0]["message"]["content"],
                    "status": 1
                }

        except Exception as e:
            need_retry = retry_count < 2
            result = {"total_tokens": 0, "completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if isinstance(e, RateLimitError):
                logger.warn("[CHATGPT] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"

            elif isinstance(e, Timeout):
                logger.warn("[CHATGPT] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"

            elif isinstance(e, APIError):
                logger.warn("[CHATGPT] Bad Gateway: {}".format(e))
                result["content"] = "请再问我一次"

            elif isinstance(e, APIConnectionError):
                logger.warn("[CHATGPT] APIConnectionError: {}".format(e))
            else:
                logger.exception("[CHATGPT] Exception: {}".format(e))
                need_retry = False

            if need_retry:
                logger.warn("[CHATGPT] 第{}次重试".format(retry_count + 1))
                return self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                result['status'] = 0
                return result
