from langchain_openai import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from dotenv import load_dotenv

load_dotenv()


GPT_4_O='gpt-4o'
GPT_4_1='gpt-4.1'
GPT_5='gpt-5'
GPT_5_MINI='gpt-5-mini'
GPT_5_NANO='gpt-5-nano'


DEFAULT_MODEL=GPT_4_1
DEFAULT_RESSONING_MODEL=GPT_5_MINI
USE_RESPONSE_API=True

DEFAULT_TEMPERATURE=0.7

def get_model(model_name:str=DEFAULT_MODEL,*args,**kwargs)->BaseChatModel:
    '''
    returns the language model to be used by the agent
    '''
    
    
    if not 'temperature' in kwargs:
        kwargs['temperature']=DEFAULT_TEMPERATURE
    
    
    return ChatOpenAI(model_name=model_name,use_responses_api=USE_RESPONSE_API,*args,**kwargs)



def get_resoning_model(model_name:str=DEFAULT_RESSONING_MODEL,*args,**kwargs)->BaseChatModel:
    '''
    returns the language model to be used by the agent
    '''
    reasoning = {
    "effort": "high",  # 'low', 'medium', or 'high'
    "summary": None,  # 'detailed', 'auto', or None
}
    
    if not 'temperature' in kwargs:
        kwargs['temperature']=DEFAULT_TEMPERATURE
    
    
    return ChatOpenAI(model_name=model_name,use_responses_api=USE_RESPONSE_API,reasoning=reasoning,*args,**kwargs)
