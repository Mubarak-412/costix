import os
import os.path
import uuid
import gradio as gr
import json
import pandas as pd
from costix.graph import CostixGraph
from langgraph.checkpoint.memory import MemorySaver

from gradio_ui.gradioComponents import create_question_component



checkpoint=MemorySaver()

costix_graph=CostixGraph(checkpointer=checkpoint)




from langchain_core.messages import AIMessage, HumanMessage


def format_file_names(files_names):

    if(len(files_names)):
        return 'Files Uploaded : \n'+'\n'.join(files_names)
    else:
        return "No Files Uploaded Yet"

def get_random_uuid():
    return str(uuid.uuid4())

starting_ai_message=AIMessage(
    content=json.dumps({
        'type':'single_select',
        'title':'What are you here for?',
        'subtitle':'I can help you with the following usecases, or create a new usecase.',
        'options':['Infrastructure Migration','Pre-Project Budgeting','Other','new usecase']
    })
)

def create_new_thread():
    thread_id=get_random_uuid()
    costix_graph.initialize_thread(thread_id,{'messages':[starting_ai_message],'messages_history':[starting_ai_message]})
    return thread_id



css='''
#messages-container {
  height: 75vh;              /* tweak as you like */
  border: 1px solid var(--background-fill-secondary);
  padding: 5px;
  border-radius: 12px;
  background-color: var(--background-fill-secondary); 
#   252424
}

#messages-container > .styler {
    overflow-y: scroll !important;
    scrollbar-width: none;
    display: flex;
    background-color: var(--background-fill-secondary);
}



#messages-container .message {
    background-color: var(--block-background-fill) !important;
    border-radius: 12px;
    margin-bottom: 12px;
    flex-shrink: 0;
}

#messages-container .message.user-message {
    width:80%;
    margin-right: auto;
}


#messages-container .message.assistant-message {
    width:80%;
    margin-left: auto;
}

'''







chat_input=gr.MultimodalTextbox(
                    file_count='multiple',
                    interactive=True,
                    placeholder='Enter message or upload file',
                    show_label=False,
                    scale=1,
                    sources=['upload'])





with gr.Blocks(fill_height=True,css=css) as demo:
    uploaded_file_names=gr.State([])
    collected_data=gr.State([])
    thoughts=gr.State([])
    solution=gr.State([])

    # downloadable_file_names=gr.State([])


    thread_id=gr.State(value=(create_new_thread()))

    # code_snipets=gr.State([])
    
    with gr.Sidebar(open=False) as sidebar:
        # gr.TextArea(value=format_file_names,inputs=[uploaded_file_names],label='Uploaded Files')
        
        with gr.Group():
            gr.Text(value=lambda x:x,inputs=[thread_id],label='Thread Id')
            reset_thread=gr.Button(value='Reset Thread',variant='stop')


    with gr.Row():
        with gr.Column(scale=6):
            with gr.Tab(label='Chat'):
                

                chat_history=gr.State([starting_ai_message])
                @gr.render(inputs={chat_history})
                def render_chat_history(inputs):
                    with gr.Group(elem_id='messages-container',preserved_by_key='messages-container') as messages_window:
                        for message in inputs[chat_history]:
                            # gr.Markdown(message.content)
                    
                            content=None
                            try:
                                content=json.loads(message.content)
                            except Exception as ex:
                                pass
                                # gr.Text(value=ex,label='Json parse error')
                            
                            if isinstance(message, HumanMessage):
                                with gr.Group(elem_classes=['message','user-message'],preserved_by_key=message.id) as user_block:
                                    gr.Text(value=message.content,label='user')
                            elif isinstance(message,AIMessage):
                                with gr.Blocks(preserved_by_key=message.id) as assistant_block:
                                    if(content):
                                        # gr.Text('assistant message')
                                        q_type=content.get('type','text')
                                        title=content.get('title','No title')
                                        subtitle=content.get('subtitle','No subtitle')
                                        options=content.get('options',[])
                                        is_last_message=inputs[chat_history].index(message)==len(inputs[chat_history])
                                        response=content.get('response',None)
                                        

                                        with gr.Group(elem_classes=['message','assistant-message']) as question_block:
                                            if response:
                                                gr.Text(value=response,label='AI Response',text_align='right')
                                            gr.Text(value=title,label='AI Response',text_align='right',autoscroll=is_last_message,autofocus=is_last_message)
                                            # gr.Markdown(f'# {title}')
                                            gr.Text(value=subtitle,show_label=False,text_align='right',container=False)
                                            

                                            
                                            
                                            def submit_options(options):
                                                options_str=''
                                                if isinstance(options,list):
                                                    options_str=','.join(options)
                                                else:
                                                    options_str=options
                                                return {chat_input:{'text':options_str}}

                                                
                                            
                                            if q_type=='single_select':
                                                single_select=gr.Radio(options,label='Select One')  
                                                single_select.change(
                                                    fn=submit_options,
                                                    inputs=[single_select],
                                                    outputs={chat_input}
                                                )

                                            elif q_type=='multi_select':
                                                checkbox_group=gr.CheckboxGroup(options,label='options')    
                                                checkbox_group.change(
                                                    fn=submit_options,
                                                    inputs=[checkbox_group],
                                                    outputs={chat_input}
                                                )
                                            
                                           
                                    else:
                                        gr.Text(value=message.content,label='Json parse error')
                            else:
                                pass
                   
                    
                chat_input.render()
               


        with gr.Column(scale=4) as rightSideBar:

            with gr.Tab('Thought Process') as thoughts_tab:
                
                @gr.render(inputs=[thoughts])
                def render_thoughts(thoughts):
                    if not thoughts:
                        return 
                    with gr.Group():
                        for thought in thoughts:
                            gr.Radio([thought],value=thought,show_label=False)

            with gr.Tab('Collected Data') as collected_data_tab:
                @gr.render(inputs=[collected_data])
                def format_collected_data(collected_data):

                    if not collected_data:
                        return gr.Markdown('No data collected')

                    # Convert list[dict] → DataFrame
                    df = pd.DataFrame(collected_data)

                    # Ensure required columns exist
                    if not {"group", "title", "value"}.issubset(df.columns):
                        return gr.Markdown('No data collected')

                    # Group by 'group'
                    markdown_parts = []
                    for group, gdf in df.groupby("group", sort=False):   # sort=False = keep input order
                        markdown_parts.append(f"## {group}")
                        for _, row in gdf.iterrows():
                            markdown_parts.append(f"\n&emsp;{row['title']}: {row['value']}")
                        markdown_parts.append("")  # spacing between groups

                    return gr.Markdown("\n".join(markdown_parts))

            with gr.Tab('Solution') as solution_tab:
                @gr.render(inputs=[solution])
                def render_solution(solution):

                    if not solution:
                        return gr.Markdown('Solution yet to be generated')
                    df=pd.DataFrame(solution)
                    markdown_parts=[]
                    for group,gdf in df.groupby('group'):
                        markdown_parts.append(f'## {group}')
                        for _,row in gdf.iterrows():
                            markdown_parts.append(f'\n&emsp;{row["title"]}: {row["value"]}')
                        markdown_parts.append("")  # spacing between groups
                    return gr.Markdown('\n'.join(markdown_parts))


        def handle_input(inputs):

            # for file_path in inputs[chat_input]['files']:
            #     filename = os.path.basename(file_path)
            #     dest_path = os.path.join(UPLOAD_DIR, filename)
                
                # if not os.path.exists(dest_path):
                #     os.rename(file_path, dest_path)

                # if dest_path not in inputs[uploaded_file_names]:
                #     inputs[uploaded_file_names].append(dest_path)
                #     yield  {uploaded_file_names:inputs[uploaded_file_names]}
            
            text_input=inputs[chat_input]['text']

            if text_input is not None:
                user_message=gr.ChatMessage(role='user',content=text_input)
                
                inputs[chat_history].append(user_message)
            
                yield {chat_history:inputs[chat_history],chat_input:None}                # return 


            config={'configurable':{'thread_id':inputs[thread_id]}}
            messages=[HumanMessage(text_input)]
            
            state={
                'messages':messages,
                'messages_history':messages,
                'uploaded_files':format_file_names(inputs[uploaded_file_names])}


            response=costix_graph.invoke(state,config)
            print(response)

            


            yield {
                collected_data:response['collected_data'],
                thoughts:response['thoughts'],
                solution:response['solution'],
                chat_history:response['messages_history']
            }


            # def getLastMessage():
            #     return inputs[chat_history][-1]

            # async for chunk in stream:
                
            #     event=chunk['event']
            #     eventData=chunk['data']
            #     # print(event)


            #     if(event=='on_chat_model_start'):
            #         new_message=gr.ChatMessage(role='assistant',content='',metadata={'status':'pending'})
            #         inputs[chat_history].append(new_message)

            #     elif(event=='on_chat_model_stream'):
            #         partialMessage=eventData['chunk'].content
            #         getLastMessage().content+=partialMessage
            #     elif(event=='on_chat_model_end'):
            #         outputMessage=eventData['output'].content
            #         lastMessage=getLastMessage
            #         lastMessage.content=outputMessage
            #         lastMessage.metadata={'status','done'}

            #     elif(event=='on_tool_start'):
            #         tool_name=chunk['name']
            #         tool_input=eventData['input']


            #         title=f'Using Tool 🛠️ {tool_name}'
            #         # if tool_name=='Python_REPL':
            #         #     code=tool_input['command']
            #         #     new_snippet={'type':'code','content':code}
            #         #     inputs[code_snipets].append(new_snippet)
            #         #     yield {code_snipets:inputs[code_snipets]}
                    
            #         # if tool_name=='download_file':
            #         #     file_name=tool_input['file_name']

            #         #     if os.path.exists(file_name):
            #         #         inputs[downloadable_file_names].append(file_name)
            #         #         yield {downloadable_file_names:inputs[downloadable_file_names]}

                        
            #         metadata={'title':title}
            #         getLastMessage().metadata=metadata
            
            #     elif(event=='on_tool_end'):
            #         tool_name=chunk['name']
            #         tool_output=eventData['output']
            #         print('tool outptu   skdjskfjksjdkfjs ',tool_output)




                
                
            #     yield {chat_history:inputs[chat_history]}

        
        chat_input.submit(
            fn=handle_input,
            inputs={
                    chat_history,
                    chat_input,
                    uploaded_file_names,
                    thread_id,
                    thoughts,
                    collected_data,
                    solution,
                    },
                outputs={
                    chat_history,
                    chat_input,
                    uploaded_file_names,
                    thoughts,
                    collected_data,
                    solution,
                    }
        )
        
        
        
        gr.on(
            triggers=[
                chat_history.change,
                chat_input.submit,
                thoughts.change,
                collected_data.change,
                solution.change,
                ],
            fn=None,
            js='''
                function scrollMessagesContainer() {
                    function scrollToBottom(container_selector) {

                        const container=document.querySelector(container_selector);
                        if(container) {
                            container.scrollTop = container.scrollHeight;
                            console.log('scrolled to bottom')
                        }
                    }
                    setTimeout(() => {
                        scrollToBottom('#messages-container .styler');
                    }, 2000);
                }
            ''',
            inputs=[],
            outputs=[]
)
        
        

    @reset_thread.click(outputs={thread_id,uploaded_file_names,chat_history,thoughts,solution,collected_data,chat_input})
    def reset_app():

        new_thread_id=create_new_thread()
        return {
            thread_id:new_thread_id,
            uploaded_file_names:[],
            chat_history:[starting_ai_message],
            thoughts:[],
            solution:[],
            collected_data:[],
            chat_input:None
        }







    
if __name__=='__main__':

    demo.launch(ssr_mode=False)
