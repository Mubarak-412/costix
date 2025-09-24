from typing import Annotated
from pydantic import BaseModel,Field
from langchain.tools import StructuredTool
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from costix.db import get_snowflake_connection


class SolutionDataPoint(BaseModel):
    '''
    The data point that should be added to the solution
    '''
    group:str=Field(...,description='The title of the group')
    title:str=Field(...,description='The key of the data point')
    value:str=Field(...,description='The value of the data point')

def execute_sql_query(
        query:str,
    ):

    try:
        conn=get_snowflake_connection()
        cursor=conn.cursor()
        cursor.execute(query)
        
        rows=cursor.fetchall()
        conn.close()
    except Exception as e:
        error_message=f'Error executing query {query}: {e}'
        print(error_message)
        return error_message
    
    response=f"Executed query {query}\nResult: {rows}"
    return response

execute_sql_query_tool=StructuredTool.from_function(
    func=execute_sql_query,
    name='execute_sql_query',
    description='''
    used to execute a sql query
    args:
        query: The sql query to execute
    ''',
)

