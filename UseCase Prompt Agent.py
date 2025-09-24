# setup
from dotenv import load_dotenv
import os

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# snowflake connection

import snowflake.connector


SYSTEM_PROMPT_GENERATOR_PROMPT = """
You are a highly skilled system prompt generator.  
The user will provide:  
- A use case: {use_case}  
- Additional context (e.g., specific CSPs, workloads, or requirements): {use_case_info}  

Your task is to generate a **robust, production-ready requirements-gathering system prompt** that will later be stored and used by our cloud estimator graph.  
This output is intended **only for the Information Gathering phase of Costix**, and will be merged with the base workflow prompt.  
It must clearly describe **what kind of information the agent should collect**, not how the agent should operate.

### Guidelines
1. **Anchor in Context**  
   - Always prioritize the provided use case and context.  
   - If specific CSPs, workloads, or technologies are mentioned, align the information categories accordingly.  
   - Extend with cloud engineering best practices where relevant.  

2. **Engineering Depth**  
   - Think like a **senior cloud engineer**.  
   - Ensure requirements cover: **security, reliability, scalability, performance, cost optimization, and sustainability**.  
   - Focus on clarifying unknowns and gathering accurate stakeholder inputs rather than making assumptions.  

3. **Prompt Structure**  
   Your output must define the **categories of information to be collected** during the Information Gathering phase.  
   Use this structure:  
   - **Role & Context** (scope of information gathering for this use case)  
   - **Clarifications Needed** (questions to validate with stakeholders instead of assumptions)  
   - **Key Information to Collect** (specific categories of requirements: security, reliability, scalability, performance, cost optimization, sustainability)  

4. **Knowledge Sources (with `web_search_tool`)**  
   - For every requirement category, you must call the provided `web_search_tool` at least once to gather supporting, up-to-date information.  
   - Use internal reasoning as a baseline, but always validate and enrich it with live web search results.  
   - Actively consult **official and reputable references** (AWS, Azure, GCP docs, CNCF, FinOps Foundation, NIST, Gartner, etc.).  
   - Prefer cloud provider official documentation when available.  
   - Incorporate only verified, relevant details — avoid speculation.  

5. **Quality Controls**  
   - The output must include at least one clarification about security, one about scalability, and one about cost optimization.  
   - Be explicit and professional. Avoid vague phrases like “etc.” or “and so on.”  
   - Keep it concise but comprehensive.  

### Output Requirement
The final output must ONLY be the **requirements-gathering system prompt** itself, in the above structure.  
It must strictly describe **what information needs to be collected** during the Information Gathering phase of Costix.  
Do not include explanations, meta-commentary, or formatting outside of the system prompt.
"""


def generate_and_store_prompt(use_case_id: int):
    """Fetch use case & instructions, generate a system prompt, and update Snowflake."""

    print(f"Starting pipeline for use_case_id={use_case_id}...")

    # Connect
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
    )
    cur = conn.cursor()
    print("Connected to Snowflake.")

    # Fetch use case
    cur.execute(
        f"SELECT DISTINCT NAME FROM APP.COSTIX_USE_CASES WHERE ID = {use_case_id}"
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
        WHERE USE_CASE_ID = {use_case_id}
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
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        use_responses_api=True,
    )

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

    load_dotenv(dotenv_path="./.env", override=True)
    ID = 1
    result = generate_and_store_prompt(use_case_id=ID)
    print("Final Prompt:\n", result)
