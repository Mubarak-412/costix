import os
import os.path
import uuid
import gradio as gr

from costix.graph import CostixGraph
from langgraph.checkpoint.memory import MemorySaver
checkpoint=MemorySaver()

costix_graph=CostixGraph(checkpointer=checkpoint)




from langchain_core.messages import HumanMessage

UPLOAD_DIR='files'


def format_file_names(files_names):

    if(len(files_names)):
        return 'Files Uploaded : \n'+'\n'.join(files_names)
    else:
        return "No Files Uploaded Yet"

def get_random_uuid():
    return str(uuid.uuid4())


def create_new_thread():
    thread_id=get_random_uuid()
    costix_graph.initialize_thread(thread_id)
    return thread_id

with gr.Blocks(fill_height=True) as demo:

    uploaded_file_names=gr.State([])
    collected_data=gr.State([])

    # downloadable_file_names=gr.State([])


    thread_id=gr.State(create_new_thread())

    # code_snipets=gr.State([])
    
    with gr.Sidebar(open=False) as sidebar:
        # gr.TextArea(value=format_file_names,inputs=[uploaded_file_names],label='Uploaded Files')
        
        with gr.Group():
            gr.Text(value=lambda x:x,inputs=[thread_id],label='Thread Id')
            reset_thread=gr.Button(value='Reset Thread',variant='stop')


    with gr.Row():
        with gr.Column(scale=7):
            with gr.Tab(label='Chat'):

                chat_history=gr.Chatbot(type='messages',scale=5)

                chat_input=gr.MultimodalTextbox(
                    file_count='multiple',
                    interactive=True,
                    placeholder='Enter message or upload file',
                    show_label=False,
                    scale=1,
                    sources=['upload'])

                # @gr.render(inputs=[downloadable_file_names])
        # def show_downloadable_files(dl_file_names):
        #     if len(dl_file_names)!=0:

        #         for link in dl_file_names:
        #             download_button=gr.File(value=link,label=f'Download File : {link}')
                    
        #             @download_button.download(inputs=[downloadable_file_names],outputs=[downloadable_file_names])
        #             def onClick(dl_file_names):
        #                 return [x for x in dl_file_names if x!=link]
        #     else:
        #         pass

        with gr.Column(scale=3) as collectedDataCollumn:

            gr.DataFrame(value=lambda x:x,inputs=[collected_data],headers=['title','value','group'],label='Collected Data')
    # with gr.Tab(label='code',scale='100') as codeTab:


        # @gr.render(inputs=[code_snipets])
        # def show_code_snippets(snippets):

        #     if len(snippets) ==0:
        #         gr.Markdown('## No Code Snippets generated ')
        #     else:

        #         for snippet in snippets:

        #             if(snippet['type']=='code'):
        #                 c=gr.Code(value=snippet['content'],language='python',label='code')
        #             else:
        #                 output=gr.Code(value=snippet['content'],label='Output')
    
        @chat_input.submit(
                inputs={
                    chat_history,
                    chat_input,
                    uploaded_file_names,
                    thread_id,
                    collected_data
                    },
                outputs={
                    chat_history,
                    chat_input,
                    uploaded_file_names,
                    collected_data
                    })
        async def handle_input(inputs):

            for file_path in inputs[chat_input]['files']:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(UPLOAD_DIR, filename)
                
                if not os.path.exists(dest_path):
                    os.rename(file_path, dest_path)

                if dest_path not in inputs[uploaded_file_names]:
                    inputs[uploaded_file_names].append(dest_path)
                    yield  {uploaded_file_names:inputs[uploaded_file_names]}
            
            text_input=inputs[chat_input]['text']

            if text_input is not None:
                user_message=gr.ChatMessage(role='user',content=text_input)
                
                inputs[chat_history].append(user_message)
            
                yield {chat_history:inputs[chat_history],chat_input:None}


            config={'configurable':{'thread_id':inputs[thread_id]}}
            messages=[HumanMessage(text_input)]
            
            state={'messages':messages,'uploaded_files':format_file_names(inputs[uploaded_file_names])}


            response=costix_graph.invoke(state,config)


            yield {
                collected_data:response['collected_data'],
                chat_history:inputs[chat_history],
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

   
    @reset_thread.click(outputs={thread_id,uploaded_file_names,chat_history,chat_input})
    def reset_app():

        new_thread_id=create_new_thread()
        return {
            thread_id:new_thread_id,
            uploaded_file_names:[],
            chat_history:[],
            chat_input:None
        }







    
if __name__=='__main__':

    demo.launch(ssr_mode=False)
