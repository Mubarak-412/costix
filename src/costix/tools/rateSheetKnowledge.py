
from pathlib import Path
import os

from langchain.tools import StructuredTool

from costix.data import rateTableMetadata
from costix.data.rateTableMetadata import RATE_TABLE_META_DATA

PROJECT_ROOT=Path(__file__).parent.parent.parent.parent
VECTOR_STORE_DB_PATH= os.path.abspath(os.path.join(PROJECT_ROOT,'vectorDB'))

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma



EMBEDDING_MODEL='text-embedding-3-large'

EMBEDDING=OpenAIEmbeddings(model=EMBEDDING_MODEL)


VECTOR_STORE_COLLECTION_NAME='rate_sheets_collection'

def get_vector_store():
    try:
        vector_store=Chroma(
            collection_name=VECTOR_STORE_COLLECTION_NAME,
            embedding_function=EMBEDDING,
            persist_directory=VECTOR_STORE_DB_PATH
        )
        return vector_store
    except Exception as e:
        raise ValueError(f"Error initializing vector store: {e}")





def initialize_vector_store():
    try:
        vector_store=get_vector_store()
        vector_store.reset_collection()
        # vector_store.add_texts(RATE_TABLE_META_DATA)
        return True
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        return False



def get_rate_sheet_vector_store_tool():

    vector_store=get_vector_store()
    vector_store.as_retriever(k=2)

    def sementic_search(query:str):
        return vector_store.similarity_search(query)

    tool=StructuredTool.from_function(
        func=sementic_search,
        name='rate_sheet_knowledge_tool',
        description='''
        Use this tool to perform search on the rate sheet knowledge base.
        args:
            query: The search query string.
        returns:
            detailed information about tables that match the query.
        '''
    )
    return tool
    



if not os.path.exists(VECTOR_STORE_DB_PATH):
    initialize_vector_store()