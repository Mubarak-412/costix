# setup
from dotenv import load_dotenv
import os

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from costix.db import get_snowflake_connection
from costix.model import get_model

# snowflake connection

import snowflake.connector


SYSTEM_PROMPT_GENERATOR_PROMPT = """
You are a highly skilled system prompt generator.  
The user will provide:  
- A use case: {use_case}  
- Additional context (e.g., specific CSPs, workloads, or requirements): {use_case_info}  

Your task is to gernerate a section of the system prompt for the Information Gathering Agent.

you will generate a **robust, production-ready requirements-gathering system prompt** that will be added to the Information Gathering Agent.  
It must clearly describe **what kind of information the agent should collect** for the provided use case. do not focus on how it is collected.

### Guidelines
1. **Anchor in Context**  
   - Always prioritize the provided use case and context.  
   - If specific CSPs, workloads, or technologies are mentioned, align the information categories accordingly. 

2. **Engineering Depth**  
   - Think like a **senior cloud engineer**.  
   - Add all aspects of the use case that must be considered: ex: reliability, scalability, performance, cost optimization,etc. 
   - Focus on clarifying unknowns and gathering accurate stakeholder inputs rather than making assumptions.  

3. **Prompt Structure**  
   Your output must define the **categories of information to be collected** during the Information Gathering phase.  
   Use this structure:  
   - **Role & Context** (scope of information gathering for this use case)  
   - **Clarifications Needed** ( additional key aspects of the projects that must be clarified  )  
   - **Key Information to Collect** (categories of information to be collected, ex:security, scalability,etc.)

4. **Knowledge Sources (with `web_search_tool`)**  
   - For every requirement category, the agent must call the provided `web_search_tool` at least once to gather supporting, up-to-date information.  
   - Use internal reasoning as a baseline, but always validate and enrich it with live web search results.  
   - Actively consult **official and reputable references** (AWS, Azure, GCP docs, CNCF, FinOps Foundation, NIST, Gartner, etc.).  
   - Prefer cloud provider official documentation when available.  
   - Incorporate only verified, relevant details — avoid speculation.  

5. **Quality Controls**  
   - The output must include at least one clarification about security, one about scalability, and one about cost optimization.  
   - Be explicit and professional,Keep it concise but comprehensive.  

### Output Requirement
your final output must be the key focus areas of the project  to be considered in order to capture the requirement for the usecase.  
It must strictly describe the things to consider during the Information Gathering phase of Costix.  
Do not include explanations, meta-commentary, or formatting outside of the system prompt.
"""


def fetch_use_case_prompt(use_case_id: str):
    try:
        conn=get_snowflake_connection()
        cur=conn.cursor()
        cur.execute(
            f"SELECT DISTINCT USE_CASE_PROMPT FROM APP.COSTIX_USE_CASES WHERE ID = '{use_case_id}'"
        )
        row=cur.fetchone()
        if not row:
            raise ValueError(f"No use case prompt found for ID={use_case_id}")
        use_case_prompt=row[0]
        return use_case_prompt
    except Exception as e:
        return None


def generate_and_store_prompt(use_case_id: str):
    """Fetch use case & instructions, generate a system prompt, and update Snowflake."""

    print(f"Starting pipeline for use_case_id={use_case_id}...")

    # Connect
    conn = get_snowflake_connection()
    cur = conn.cursor()
    print("Connected to Snowflake.")

    # Fetch use case
    cur.execute(
        f"SELECT DISTINCT NAME FROM APP.COSTIX_USE_CASES WHERE ID = '{use_case_id}' "
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(f"No use case found for ID={use_case_id}")
    use_case = row[0]
    print(f"Use case: {use_case}")

    # Fetch instructions
    cur.execute(
        f"""
        SELECT DISTINCT USE_CASE_CONTENT 
        FROM APP.COSTIX_USE_CASE_INSTRUCTIONS
        WHERE USE_CASE_ID = '{use_case_id}'
        AND ACTIVE = TRUE
        """
    )
    rows = cur.fetchall()
    use_case_info = ", ".join(r[0] for r in rows)
    print(f"Instructions: {use_case_info}")

    # Build prompt
    prompt_template = ChatPromptTemplate.from_messages(
        messages=[
            (
                "system",
                SYSTEM_PROMPT_GENERATOR_PROMPT.format(
                    use_case=use_case, use_case_info=use_case_info
                ),
            )
        ]
    )

    # LLM
    llm = get_model()

    web_search_tool = {"type": "web_search_preview"}
    llm_with_tools = llm.bind_tools(tools=[web_search_tool])

    response = llm_with_tools.invoke(input=prompt_template.format_messages())
    use_case_prompt_final = response.text()
    print("LLM output received.")

    # Update DB
    cur.execute(
        """
        UPDATE APP.COSTIX_USE_CASES
        SET USE_CASE_PROMPT = %s
        WHERE ID = %s
        """,
        params=(use_case_prompt_final, use_case_id),
    )
    print(f"Updated use case {use_case_id}.")

    cur.close()
    conn.close()
    print("Connection closed.")

    return use_case_prompt_final


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ID = 'db845027-b985-42d0-8498-62f61f0a7f78'
    result = generate_and_store_prompt(use_case_id=ID)
    print("Final Prompt:\n", result)
    # prompt = fetch_use_case_prompt(use_case_id=ID)
    # print("Prompt:\n", prompt)
