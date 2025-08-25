import jupyter_client
import queue
import atexit
from typing import Dict

# Using modern Pydantic import
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool, BaseTool

# --- Core REPL Class (Jupyter Kernel) ---
# This class manages a persistent Jupyter kernel and communicates with it.
class JupyterKernelREPL:
    """
    Manages a persistent, interactive Jupyter kernel subprocess.
    The kernel is started automatically on initialization and shut down
    when the program exits.
    """
    def __init__(self):
        self.kernel_manager = None
        self.kernel_client = None
        self.startup_error = None  # To store any error during initialization
        self._start_session()
        # Ensure cleanup happens when the script exits
        atexit.register(self._end_session)

    def _start_session(self):
        """Starts a Jupyter kernel subprocess automatically."""
        if self.kernel_manager and self.kernel_manager.is_alive():
            return

        try:
            self.kernel_manager = jupyter_client.KernelManager()
            self.kernel_manager.start_kernel()
            self.kernel_client = self.kernel_manager.client()
            self.kernel_client.start_channels()
            # Wait for the client to be ready
            self.kernel_client.wait_for_ready(timeout=10)
            print("Jupyter kernel session started automatically.")
        except Exception as e:
            # Store the specific error and print it for debugging in logs
            self.startup_error = f"Error auto-starting Jupyter kernel: {e}"
            print(self.startup_error)
            self.kernel_manager = None
            self.kernel_client = None
        
    def _end_session(self):
        """Shuts down the Jupyter kernel automatically."""
        if not self.kernel_manager or not self.kernel_manager.is_alive():
            return

        print("Jupyter kernel session shutting down automatically.")
        try:
            # Check if channels are still running before trying to stop them
            if self.kernel_client.channels_running:
                self.kernel_client.stop_channels()
            if self.kernel_manager.is_alive():
                self.kernel_manager.shutdown_kernel(now=True)
        except Exception as e:
            print(f"Error during auto-shutdown of Jupyter kernel: {e}")

    def run_command(self, command: str) -> str:
        """
        Executes a command in the persistent Jupyter kernel.
        """
        # Return the specific startup error if the kernel failed to initialize
        if self.startup_error:
            return self.startup_error
        if not self.kernel_client or not self.kernel_manager.is_alive():
            return "Error: Jupyter kernel session is not running or failed to start."

        # Execute the code
        msg_id = self.kernel_client.execute(command, store_history=False)

        # Wait for the final reply message on the shell channel
        try:
            execute_reply = self.kernel_client.get_shell_msg(timeout=10)
            if execute_reply['content']['status'] == 'error':
                error_content = execute_reply['content']
                error_message = f"--- STDERR ---\n"
                error_message += f"{error_content.get('ename', 'Error')}: {error_content.get('evalue', '')}\n"
                traceback = "\n".join(error_content.get('traceback', []))
                error_message += traceback
                return error_message
        except queue.Empty:
             # Fallback to iopub if shell is silent
             pass


        # Poll the iopub channel for execution status and output
        output = ""
        error_output = ""
        while True:
            try:
                msg = self.kernel_client.get_iopub_msg(timeout=5)
                
                # Check if the message is from our execution request
                if msg.get('parent_header', {}).get('msg_id') != msg_id:
                    continue

                msg_type = msg['header']['msg_type']
                
                if msg_type == 'stream':
                    if msg['content']['name'] == 'stdout':
                        output += msg['content']['text']
                elif msg_type == 'error':
                    error_content = msg['content']
                    error_output += f"{error_content.get('ename', 'Error')}: {error_content.get('evalue', '')}\n"
                    error_output += "\n".join(error_content.get('traceback', []))
                elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                    # Kernel is done executing, break the loop
                    break
            except queue.Empty:
                # No more messages, break the loop
                break
        
        if error_output:
            return f"--- STDERR ---\n{error_output.strip()}\n"
        if output:
            return f"--- STDOUT ---\n{output.strip()}\n"

        return "Command executed with no output."


# --- Tool Factory Function ---

class PythonREPLInput(BaseModel):
    command: str = Field(description="The Python code to execute in the persistent session.")

def get_jupyter_repl_tool() -> BaseTool:
    """
    Factory function that creates and returns a single, stateful Jupyter REPL tool.
    The JupyterKernelREPL instance is managed within the closure of this function,
    and its session is handled automatically.
    """
    repl_session = JupyterKernelREPL()

    # The run function is now simpler, just passing the command.
    def _run_jupyter_repl(command: str) -> str:
        return repl_session.run_command(command)

    tool = StructuredTool.from_function(
        func=_run_jupyter_repl,
        name="Python_REPL",
        description="A persistent Python REPL powered by a Jupyter Kernel. The session starts and stops automatically. Just provide the Python code to run., print the variables to see the values",
        args_schema=PythonREPLInput
    )
    return tool


# # --- Example Usage ---
# if __name__ == '__main__':
    # print("--- Persistent Python REPL: Auto-Session Jupyter Kernel ---")
    
    # # Kernel starts automatically when the tool is created
    # python_tool = get_jupyter_repl_tool()
    
    # print("-" * 20)
    
    # # print(f"TOOL: {python_tool.name}\nOPERATION: Create a file")
    # # print(f"RESULT: {python_tool.invoke({'command': 'with open(\"test_jupyter.txt\", \"w\") as f: f.write(\"hello from jupyter\")'})}")
    # print("-" * 20)

    # print(f"TOOL: {python_tool.name}\nOPERATION: x = 250")
    # print(f"RESULT: {python_tool.invoke({'command': 'x = 250'})}")
    # print("-" * 20)
    
    # print(f"TOOL: {python_tool.name}\nOPERATION: print(x)")
    # print(f"RESULT: {python_tool.invoke({'command': 'print(f\"The value of x is {x}\")'})}")
    # print("-" * 20)
    
    # print(f"TOOL: {python_tool.name} (demonstrating an error)")
    # print(f"OPERATION: print(z)")
    # print(f"RESULT: {python_tool.invoke({'command': 'print(z)'})}")
    # print("-" * 20)

    # print("--- End of script. Kernel will be shut down automatically by atexit. ---")
