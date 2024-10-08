import requests
import json

# 目标URL
url = 'http://127.0.0.1:8008/query'

# 要发送的数据
data = {
    'message': {
        'content': '你是谁？'
    },
    "userId": '123'
    # 添加你需要的键值对
}
# 你好，我想买浴帘杆
# 我想买直杆形
# 有那些尺寸的呢？

# 发送POST请求
response = requests.post(url, data=json.dumps(data))

# 检查响应状态码并打印响应内容
if response.status_code == 200:
    print('成功访问！')
    # 假设响应内容是JSON格式
    print(response.json())
else:
    print(f'访问失败，状态码：{response.status_code}')
