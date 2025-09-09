from langchain_openai import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from dotenv import load_dotenv

load_dotenv()


GPT_4_O='gpt-4o'
GPT_4_1='gpt-4.1'
GPT_5='gpt-5'


OPENAI_MODEL=GPT_4_1
USE_RESPONSE_API=True

def get_model(model_name:str=OPENAI_MODEL)->BaseChatModel:
    '''
    returns the language model to be used by the agent
    '''
    return ChatOpenAI(model_name=model_name,use_responses_api=USE_RESPONSE_API)
