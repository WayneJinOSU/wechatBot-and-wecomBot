# encoding:utf-8

import requests, json
from common.log import logger
from chatbot.bot import Bot
import httpx


class BaiduWenxinBot(Bot):

    def __init__(self, config):
        super().__init__()
        self.model_name = config["MODEL"]
        self.api_key = config["API_KEY"]
        self.secret_key = config["SECRET_KEY"]

        if self.model_name == "wenxin-4":
            self.model = "completions_pro"

    async def reply_text(self, message, system_role="", retry_count=0) -> dict:
        try:
            logger.info("[BAIDU] model={}".format(self.model_name))
            access_token = self.get_access_token()
            if access_token == 'None':
                logger.warn("[BAIDU] access token 获取失败")
                return {
                    "total_tokens": 0,
                    "completion_tokens": 0,
                    "content": 0,
                }
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/" + self.model + "?access_token=" + access_token
            headers = {
                'Content-Type': 'application/json'
            }
            payload = {"messages": [{"content": message, "role": "user"}]
            }

            client = httpx.AsyncClient()
            response = await client.post(url, headers=headers, data=json.dumps(payload).encode('utf-8'))
            # response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            response_text = json.loads(response.text)
            logger.info(f"[BAIDU] response text={response_text}")
            res_content = response_text["result"]
            total_tokens = response_text["usage"]["total_tokens"]
            completion_tokens = response_text["usage"]["completion_tokens"]
            logger.info("[BAIDU] reply={}".format(res_content))
            return {
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "content": res_content,
                "status": 1
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"total_tokens": 0, "completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}

            if need_retry:
                logger.warn("[BAIDU] 第{}次重试".format(retry_count + 1))
                return await self.reply_text(message=message, retry_count=retry_count + 1)
            else:
                logger.warn("[BAIDU] Exception: {}".format(e))
                result['status'] = 0
                return result
            return result

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        return str(requests.post(url, params=params).json().get("access_token"))


