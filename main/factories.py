from abc import ABC, abstractmethod
from .models import Chat

class ChatFactory(ABC):
    @abstractmethod
    def create_chat(self, chat_type, **kwargs):
        pass

class TextChatFactory(ChatFactory):
    def create_chat(self, chat_type, **kwargs):
        return Chat(chat_type=chat_type, **kwargs)

class VoiceChatFactory(ChatFactory):
    def create_chat(self, chat_type, **kwargs):
        return Chat(chat_type=chat_type, **kwargs)