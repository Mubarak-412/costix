from langchain_core.messages import RemoveMessage, ToolMessage
from langgraph.prebuilt import tools_condition
from langmem.short_term.summarization import DEFAULT_FINAL_SUMMARY_PROMPT
from costix.schemas import CostixAgentState, CostixState



DEFAULT_MESSAGES_KEY='messages'
DEFAULT_SUMMARY_KEY='summary'
DEFAULT_MESSAGES_TO_RETAIN=10
DEFAULT_SUMMARY_CHUNK_SIZE=5



def summary_condition(state:CostixAgentState)->bool:
    messages=state[DEFAULT_MESSAGES_KEY]
    return len(messages) > DEFAULT_MESSAGES_TO_RETAIN+DEFAULT_SUMMARY_CHUNK_SIZE


class SummaryNode:

    def __init__(self,
    model,
    messages_key=DEFAULT_MESSAGES_KEY,
    summary_key=DEFAULT_SUMMARY_KEY,
    summary_chunk_size=DEFAULT_SUMMARY_CHUNK_SIZE,
    messages_to_retain=DEFAULT_MESSAGES_TO_RETAIN,
    ):
        self.model=model
        self.messages_key=messages_key
        self.summary_key=summary_key
        self.summary_chunk_size=summary_chunk_size
        self.messages_to_retain=messages_to_retain
        
    
    def get_messages_to_summarize(self,messages):
        """
        Get the messages to be summarized from the messages list.

        """
        messages_to_summarize=messages[::self.summary_chunk_size]

        # if last message contains Toolcalls then include the tool messages as well in to be summarized
        # to avoid breaking the format for messages
        if(tools_condition(messages_to_summarize)=='tools'):
            while len(messages):
                message=messages.pop(0)
                if isinstance(message,ToolMessage):
                    messages_to_summarize.append(message)                
                else:
                    break

        # remove the last message if it is a toolcalls still exist   ( for safety )
        if(tools_condition(messages_to_summarize)=='tools'):
            messages_to_summarize=messages_to_summarize[:-1]
        
        return messages_to_summarize


    def summarize_messages(self,messages_to_summarize):
        """
        Summarize the messages.

        """
        summary_chain=DEFAULT_FINAL_SUMMARY_PROMPT | self.model
        summary_response=summary_chain.invoke(messages_to_summarize)
        
        return summary_response


    def __call__(self, state:CostixState):
        
        messages=state[self.messages_key]
        print(f'entering summary node with {len(messages)} messages')
        all_summarised_message_ids=set()
        summary=[]

        while len(messages)>self.messages_to_retain+self.summary_chunk_size:
            print(f'looping start with {len(messages)} messages')
            messages_to_summarize=self.get_messages_to_summarize(messages)

            print(f'messages to be summarised {len(messages_to_summarize)} messages')
            for m in messages_to_summarize:
                m.pretty_print()
            
            summary_message=self.summarize_messages(messages_to_summarize)
            current_summarised_message_id_set=set()
            if summary_message:
                summary.append(summary_message)
                current_summarised_message_id_set.update([message.id for message in messages_to_summarize])
                all_summarised_message_ids.update(current_summarised_message_id_set)
                print(f'summarised {len(current_summarised_message_id_set)} messages',current_summarised_message_id_set)
            else:
                print('summarization attempt Failed  could not generate the summary, Exiting loop')
                break
            
            if( current_summarised_message_id_set):
                print(f'messages length before summarizaion {len(messages)}')

                messages=list(
                    filter(lambda m:m.id not in current_summarised_message_id_set,messages)
                )
                print(f'messages length after summarization {len(messages)}')
            else:
                print('summarization attempt Failed , Exiting loop')
                break


        updates={
            self.summary_key:summary,
            self.messages_key:[RemoveMessage(id=message_id) for message_id in list(all_summarised_message_ids)]
        }

        print(f'looping end with {len(messages)} messages')
        print(f'updates \n {updates}')
        
        return updates
       
