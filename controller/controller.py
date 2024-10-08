# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, Path
from data.data import Query, CacheSignal, Message
from service.general_service import serviceMng
import uvicorn
from common.log import logger
from service.wecom_service import wecomServiceMng
from weworkapi_python.callback.WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import time
from service.wechat_service import wechatService

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/query")
async def process_query(query: Query):
    logger.info("the request is {}".format(query.dict()))
    reply = await serviceMng.process(query)

    # 处理查询逻辑...
    return {
        "reply": reply
    }


@app.post("/cleanCache")
async def process_query(singal: CacheSignal):
    try:
        success = await serviceMng.cleanCache(singal)

        # 处理查询逻辑...
        return {
            "userId": singal.userId,
            "success": success
        }
    except Exception as e:
        logger.error(e)


@app.post("/wecom/{client_url_key:path}")
async def process_query(request: Request,
                        client_url_key: str = Path(..., title="The ID of the item to get"),
                        msg_signature: str = '',
                        timestamp: str = '',
                        nonce: str = '',
                        echostr: str = ''
                        ):
    body = await request.body()  # 获取原始请求体数据
    wecom_client = await wecomServiceMng.prepare_query()

    wxcpt = WXBizMsgCrypt(sToken=wecom_client.client_app_token,
                          sEncodingAESKey=wecom_client.client_aes_key,
                          sReceiveId=wecom_client.company_id
                          )

    ret, xml_content = wxcpt.DecryptMsg(body, msg_signature, timestamp, nonce)
    if ret == 0:
        root = ET.fromstring(xml_content)
        to_user_name = root.find('ToUserName').text
        from_user_name = root.find('FromUserName').text
        content = root.find('Content').text
        msg_id = root.find('MsgId').text
        agent_id = root.find('AgentID').text
        msg_type = root.find('MsgType').text

        query = Query(message=Message(content=content), userId=from_user_name)
        reply = await wecomServiceMng.process(query)

        # 被动回复
        create_time = timestamp = str(int(time.time()))
        reply = reply.replace('?', '!').replace('？', '！')
        sReplyMsg = (f'<xml><ToUserName>{to_user_name}</ToUserName>'
                     f'<FromUserName>{from_user_name}</FromUserName>'
                     f'<CreateTime>{create_time}</CreateTime>'
                     f'<MsgType>text</MsgType>'
                     f'<Content>{reply}</Content>'
                     f'<MsgId>{msg_id}</MsgId>'
                     f'<AgentID>{agent_id}</AgentID></xml>')
        ret, sEncryptMsg = wxcpt.EncryptMsg(sReplyMsg, nonce, timestamp)
        if ret == 0:
            pass
        else:
            return 'ERR: EncryptMsg ret: ' + str(ret)
        return sEncryptMsg
    else:
        return 'ERR: DecryptMsg ret:' + str(ret)


@app.get("/wecom/{client_url_key:path}")
async def verify_url(request: Request,
                     client_url_key: str = Path(..., title="The ID of the item to get"),
                     msg_signature: str = '',
                     timestamp: str = '',
                     nonce: str = '',
                     echostr: str = ''
                     ):
    # 处理查询逻辑...
    logger.info("msg_signature: {}".format(msg_signature))
    logger.info("timestamp: {}".format(timestamp))
    logger.info("nonce: {}".format(nonce))
    logger.info("echostr: {}".format(echostr))

    wecom_client = await wecomServiceMng.prepare_query(client_url_key=client_url_key)

    wxcpt = WXBizMsgCrypt(sToken=wecom_client.client_app_token,
                          sEncodingAESKey=wecom_client.client_aes_key,
                          sReceiveId=wecom_client.company_id
                          )

    ret, reply_echostr = wxcpt.VerifyURL(sMsgSignature=msg_signature, sTimeStamp=timestamp, sNonce=nonce,
                                         sEchoStr=echostr)
    if ret == 0:
        # 转换为普通字符串
        reply_echostr = reply_echostr.decode('utf-8')

        # 去除可能存在的引号和换行符
        # reply_echostr = reply_echostr.replace("'", "").replace('"', '').replace('\n', '')
        logger.info("the response to wcom is {}".format(reply_echostr))
        return int(reply_echostr)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
