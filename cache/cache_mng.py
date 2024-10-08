from fastapi_cache import FastAPICache
from data.data import Conversation, QA
import aioredis
from fastapi_cache.backends.redis import RedisBackend
import json
from common.log import logger
from typing import Optional, Literal, List, Dict


class CacheManager:
    def __init__(self):
        self.conversation_cache_prefix = "conversation-detail"
        try:
            redis = aioredis.from_url("redis://127.0.0.1:6379", encoding="utf8", decode_responses=True)
            redis_backend = RedisBackend(redis)
            FastAPICache.init(backend=redis_backend, prefix="fastapi-cache")
            self.redis = redis
            logger.info("init redis successfully")
        except Exception as e:
            logger.error("failed init redis")

    async def get_conversation_cache(self, user_id: int) -> Conversation:
        cache_key = "{}_{}".format(self.conversation_cache_prefix, user_id)

        try:
            cached_data = await FastAPICache.get_backend().get(cache_key)
        except ConnectionError:
            logger.error("[get_conversation_cache]: {}".format("failed to connect redis"))
            return None
        except TimeoutError:
            logger.error("[get_conversation_cache]: {}".format("timeout with Redis server"))
            return None

        if cached_data:
            cached_data = json.loads(cached_data)
            return Conversation(**cached_data)
        return None

    async def set_conversation_cache(self, user_id: int, conversation: Conversation, expire: int = 300):
        cache_key = "{}_{}".format(self.conversation_cache_prefix, user_id)

        # 将模型转换为字典以存储在缓存中
        try:
            await FastAPICache.get_backend().set(cache_key, json.dumps(conversation.dict()), expire)
        except ConnectionError:
            logger.error("[set_conversation_cache]: {}".format("failed to connect redis"))
            return None
        except TimeoutError:
            logger.error("[set_conversation_cache]: {}".format("timeout with Redis server"))
            return None
        logger.info("[set_conversation_cache]: : {}".format(cache_key, json.dumps(conversation.dict())))

    async def clean_users_cache(self, user_id: int):
        """
        清除特定用户的缓存数据
        """
        try:

            # 删除对话详情缓存
            conversation_cache_key = "{}_{}".format(self.conversation_cache_prefix, user_id)
            await self.redis.delete(conversation_cache_key)
            logger.info("[clean_users_cache]: Deleted conversation cache for user {}: {}".format(user_id,
                                                                                                 conversation_cache_key))
        except ConnectionError:
            logger.error("[clean_users_cache]: Failed to connect to Redis")
            return False
        except TimeoutError:
            logger.error("[clean_users_cache]: Timeout with Redis server")
            return False

        return True


class WeChatConversationManager:
    def __init__(self, default_limit: int = 10):
        self.default_limit = default_limit
        self.users: Dict[str, Conversation] = {}

    def _get_or_create_conversation(self, user_id: str) -> Conversation:
        if user_id not in self.users:
            self.users[user_id] = Conversation(limit=self.default_limit)
        return self.users[user_id]

    def update_conversation(self, user_id: str, dialogue: QA):
        """为指定用户添加一个新的问答对到对话历史"""
        conversation = self._get_or_create_conversation(user_id)
        conversation.Q2A.append(dialogue)

        # 如果超出限制，删除最旧的对话
        if len(conversation.Q2A) > conversation.limit:
            conversation.Q2A.pop(0)

    def get_conversation(self, user_id: str) -> Conversation:
        """获取指定用户的全部对话历史"""
        conversation = self._get_or_create_conversation(user_id)
        return conversation

    def clear_conversation(self, user_id: str):
        """清空指定用户的对话历史"""
        conversation = self._get_or_create_conversation(user_id)
        conversation.Q2A = []

    def get_last_qa(self, user_id: str) -> Optional[QA]:
        """获取指定用户最近的一个问答对"""
        conversation = self._get_or_create_conversation(user_id)
        if conversation.Q2A:
            return conversation.Q2A[-1]
        return None

    def update_limit(self, user_id: str, new_limit: int):
        """更新指定用户对话历史的长度限制"""
        conversation = self._get_or_create_conversation(user_id)
        conversation.limit = new_limit
        # 如果当前历史超出新限制，裁剪历史
        while len(conversation.Q2A) > new_limit:
            conversation.Q2A.pop(0)

    def to_dict(self) -> dict:
        """将所有用户的对话转换为字典形式"""
        return {
            "app_code": self.app_code,
            "default_limit": self.default_limit,
            "users": {user_id: conv.dict() for user_id, conv in self.users.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeChatConversationManager':
        """从字典创建多用户对话管理器实例"""
        manager = cls(app_code=data['app_code'], default_limit=data['default_limit'])
        for user_id, conv_data in data['users'].items():
            manager.users[user_id] = Conversation(**conv_data)
        return manager

    def remove_user(self, user_id: str):
        """移除指定用户的对话历史"""
        if user_id in self.users:
            del self.users[user_id]

    def get_all_users(self) -> List[str]:
        """获取所有用户ID列表"""
        return list(self.users.keys())


cache_mng = CacheManager()
wechatConversationManager = WeChatConversationManager()
