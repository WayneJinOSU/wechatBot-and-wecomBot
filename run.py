from controller.controller import app
import uvicorn
from service.wechat_service import wechat_bot

if __name__ == '__main__':
    wechat_bot.start()
    uvicorn.run(app, host="127.0.0.1", port=8008)



