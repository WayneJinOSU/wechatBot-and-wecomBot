from config.config import Configure
from chatbot.claude.claude_ai_bot import ClaudeBot, AsyncClaudeBot
from chatbot.openAI.chatgpt_bot import ChatGPTBot, AsyncChatGPTBot
from chatbot.moonshot.moonshot_bot import MoonshotBot, AsyncMoonshotBot
from chatbot.ali.qianwen_bot import QianWenBot, AsyncQianWenBot
from data.data import QA, Message
import time


class AsyncBotManager:
    def __init__(self):
        self.config = Configure()
        self.claude_bot = AsyncClaudeBot(self.config.get("CLAUDE", "claude-3-opus"))
        self.gpt_turbo_bot = AsyncChatGPTBot(self.config.get("OPENAI", "gpt-4-turbo"))
        self.gpt_o_bot = AsyncChatGPTBot(self.config.get("OPENAI", "gpt-4o"))
        self.gpt_bot = AsyncChatGPTBot(self.config.get("OPENAI", "gpt-4"))
        self.moonshot_8k_bot = AsyncMoonshotBot(self.config.get("MOONSHOT", "moonshot-v1-8k"))
        self.moonshot_32k_bot = AsyncMoonshotBot(self.config.get("MOONSHOT", "moonshot-v1-32k"))
        self.qwen_bot = AsyncQianWenBot(self.config.get("ALI", "qwen-plus"))

    async def send_message(self,
                           link_ai: str,
                           message: str,
                           question: Message,
                           system_role=""
                           ):
        reply = {"content": ""}
        if link_ai == "claude-3-opus":
            time.sleep(10)
            reply = await self.claude_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "gpt-4-turbo":
            reply = await self.gpt_turbo_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "gpt-4o":
            reply = await self.gpt_o_bot.reply(message=message, system_role=system_role)
        elif link_ai == "gpt-4":
            reply = await self.gpt_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "moonshot-8k":
            reply = await self.moonshot_8k_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "moonshot-32k":
            reply = await self.moonshot_32k_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "qwen-plus":
            reply = await self.qwen_bot.reply_text(message=message, system_role=system_role)
        else:
            reply = await self.qwen_bot.reply_text(message=message, system_role=system_role)

        return QA(**{"Q": question.content, "A": reply["content"]}), reply


class BotManager:
    def __init__(self):
        self.config = Configure()
        self.claude_bot = ClaudeBot(self.config.get("CLAUDE", "claude-3-opus"))
        self.gpt_turbo_bot = ChatGPTBot(self.config.get("OPENAI", "gpt-4-turbo"))
        self.gpt_o_bot = ChatGPTBot(self.config.get("OPENAI", "gpt-4o"))
        self.gpt_bot = ChatGPTBot(self.config.get("OPENAI", "gpt-4"))
        self.moonshot_8k_bot = MoonshotBot(self.config.get("MOONSHOT", "moonshot-v1-8k"))
        self.moonshot_32k_bot = MoonshotBot(self.config.get("MOONSHOT", "moonshot-v1-32k"))
        self.qwen_bot = QianWenBot(self.config.get("ALI", "qwen-plus"))

    def send_message(self,
                           link_ai: str,
                           message: str,
                           question: str,
                           system_role=""
                           ):
        reply = {"content": ""}
        if link_ai == "claude-3-opus":
            time.sleep(10)
            reply = self.claude_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "gpt-4-turbo":
            reply = self.gpt_turbo_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "gpt-4o":
            reply = self.gpt_o_bot.reply(message=message, system_role=system_role)
        elif link_ai == "gpt-4":
            reply = self.gpt_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "moonshot-8k":
            reply = self.moonshot_8k_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "moonshot-32k":
            reply = self.moonshot_32k_bot.reply_text(message=message, system_role=system_role)
        elif link_ai == "qwen-plus":
            reply = self.qwen_bot.reply_text(message=message, system_role=system_role)
        else:
            reply = self.qwen_bot.reply_text(message=message, system_role=system_role)

        return QA(**{"Q": question.content, "A": reply["content"]}), reply


async_bot_manager = AsyncBotManager()
bot_manager = BotManager()
