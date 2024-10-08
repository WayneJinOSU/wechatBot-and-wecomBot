# chatbot

## 安装依赖环境

pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/

# 微信/企业微信智能客服接入指南

## 个人微信接入

### 修改 prompt.json

在 `system_role` 中添加您定义的提示词，例如：

```json
{
  "system_role": "【角色定义】：你是酷猫医美的客服专家\n【重要】你最重要的事情是需要获取到用户的联系方式\n【重要】当你向用户推荐医美项目时，你可以参考你了解的价格告知一个大约的市场价，并告诉用户具体的价格需要根据你的面诊情况来定\n"
}
```

### 修改 work.json
```json
{
  "work": "qwen-plus"
}
```
## 企业微信接入

### 修改 wecom.json
```json
{
  "company_id": "企业id",
  "client_app_token": "Token",
  "client_aes_key": "EncodingAESKey"
}
```
### 如何获取
请参考操作手册: https://uoeahwutd2.feishu.cn/docx/XPx7dajWXo6gRSx9SK9cGqd2nNf#A6XUdrn9MoWaT6xiXEoc2ZK1nXf

直接查看3.4节中的“获取企业id” 和 “获取Token和EncodingAESKey”的部分。

注意：企业微信需要在服务器上部署，并且对外开放接口
## 运行
python3 run.py


