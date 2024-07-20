import pickle
from langchain.memory import ChatMessageHistory

class ChatHistory():

    def __init__(self, chat_history):
        self.messaging_history = chat_history

    def add_new_message(self, request, user_message, ai_message):

        self.messaging_history.add_user_message(question)
        self.messaging_history.add_ai_message(response)
