# encoding:utf-8

import time

import openai
from chatbot.bot import Bot

from common.log import logger
from config.config import Configure
from openai import AzureOpenAI


# OpenAI对话模型API (可用)
class AzureBot(Bot):
    def __init__(self, config):
        super().__init__()
        # set the default api_key
        api_version = "2024-02-01"
        endpoint = "https://my-resource.openai.azure.com"
        api_key = config["API_KEY"]

        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key
        )

        self.model_name = config["MODEL"]
        self.api_key = config["API_KEY"]
        self.secret_key = config["SECRET_KEY"]
        self.proxy = config["PROXY"]
        if self.proxy:
            openai.proxy = self.proxy

        self.args = {
            "model": config.get("MODEL") or "gpt-3.5-turbo",  # 对话模型的名称
            "temperature": config.get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            # "max_tokens":4096,  # 回复最大的字符数
            "top_p": config.get("top_p", 1),
            "frequency_penalty": config.get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": config.get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": config.get("request_timeout", None),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
            "timeout": config.get("request_timeout", None),  # 重试超时时间，在这个时间内，将会自动重试
        }

    def reply_text(self, message, retry_count=0) -> dict:
        try:
            response = self.client.chat.completions.create(messages=message, **self.args)
            return {
                "total_tokens": response["usage"]["total_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
                "content": response.choices[0]["message"]["content"],
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if need_retry:
                logger.warning("[CHATGPT] 第{}次重试".format(retry_count + 1))
                return self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                return result


if __name__ == "__main__":
    if __name__ == "__main__":
        configure = Configure()
        print(configure.__dict__)
        bot = AzureBot(configure.get("OPENAI", "gpt-4-turbo"))
        print(bot.reply_text("你是谁？"))
