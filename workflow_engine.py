from langgraph.graph import StateGraph, END
from sql_agent import retrieve_similar_queries, save_sql_example
from sql_agent import query_ollama_together, get_database_schema
from sqlalchemy import text, exc
import logging
import json
from typing import List, Union, TypedDict

# ✅ Define the Workflow State Schema
class AgentState(TypedDict):
    question: str
    sql_query: str
    query_result: Union[str, List[dict]]
    sql_error: bool

# ✅ Define workflow
workflow = StateGraph(state_schema=AgentState)

def execute_sql(state, config):
    """Execute the SQL query and return results using SQLAlchemy."""
    session = config.get("configurable", {}).get("session")
    user_role = config.get("configurable", {}).get("role", "").lower()

    if not session:
        raise ValueError("Session is not available in config.")
    
    query = state["sql_query"].strip()
    logging.debug(f"⚡ Running query: {query}")

    # ✅ Define allowed tables per role
    ROLE_TABLE_ACCESS = {
        "admin": ["users", "garages", "services", "garage_services", "vehicle_service_summary", "customer_vehicle_info"],
        "owner": ["garages", "services", "garage_services", "vehicle_service_summary"],
        "customer": ["services", "garage_services", "garages"]
    }

    # ✅ Extract tables used in the query
    used_tables = [table for table in ROLE_TABLE_ACCESS["admin"] if table in query.lower()]

    # ✅ Check if query is out of domain
    allowed_tables = set(ROLE_TABLE_ACCESS.get(user_role, []))
    if not set(used_tables).issubset(allowed_tables):
        logging.error(f"❌ Query out of domain for role '{user_role}'. Query: {query}")
        state["query_result"] = {"raw_answer": "", "human_readable": "Query out of domain"}
        state["sql_error"] = True
        return state

    try:
        # ✅ Ensure it's a valid SELECT query
        if not query.lower().startswith("select"):
            raise ValueError("Invalid SQL query. Only SELECT statements are allowed.")

        # ✅ Execute the query
        result = session.execute(text(query))
        rows = result.fetchall()
        keys = result.keys()

        state["query_result"] = {"data": [dict(zip(keys, row)) for row in rows]}
        state["sql_error"] = False

    except exc.SQLAlchemyError as e:
        logging.error(f"❌ SQLAlchemy Error: {str(e)}")
        state["query_result"] = {"error": f"Database error: {str(e)}"}
        state["sql_error"] = True

    except Exception as e:
        logging.error(f"❌ General Error: {str(e)}")
        state["query_result"] = {"error": f"An error occurred: {str(e)}"}
        state["sql_error"] = True

    return generate_human_readable_response_with_llama(state)

def clean_sql_query(query: str) -> str:
    """Cleans the generated SQL query by removing unwanted formatting."""
    if not query:
        return ""

    query = query.strip().replace("ILIKE", "LIKE")

    # ✅ Remove unwanted markdown code block markers
    if query.startswith("```sql"):
        query = query[len("```sql"):].strip()
    if query.endswith("```"):
        query = query[:-3].strip()

    # ✅ Remove AI response artifacts
    if query.startswith("<s>"):
        query = query[len("<s>"):].strip()

    return query

def convert_nl_to_sql(state, config):
    """Convert a natural language query into an SQL query with RAG-based retrieval."""
    session = config.get("configurable", {}).get("session")
    if not session:
        raise ValueError("Session is not available in config.")

    question = state["question"]
    schema = get_database_schema(session)
    retrieved_queries = retrieve_similar_queries(question)
    retrieved_examples = "\n".join(retrieved_queries) if retrieved_queries else "No relevant examples found."

    user_role = config.get("configurable", {}).get("role", "").lower()
    garage_ids = state.get("garage_ids", [])

    # ✅ Ensure garage owners only see their own garages
    if garage_ids:
        if len(garage_ids) == 1:
            garage_filter = f"g.owner_id = {garage_ids[0]}"
        else:
            garage_filter = f"g.owner_id IN ({', '.join(map(str, garage_ids))})"
    else:
        garage_filter = "1=0"  # Prevents unauthorized access if no garages are found

    # ✅ Fixing SQL generation issues for customers
    if user_role == "customer":
        required_tables = """
        FROM garage_services gs 
        JOIN services s ON gs.service_id = s.id 
        JOIN garages g ON gs.garage_id = g.id
        """
    else:
        required_tables = ""

    # ✅ Updated SQL generation prompt with stricter constraints
    prompt = f"""
### Instructions:
You are a MySQL SQL query generator. Follow these rules:
- **Only output a valid `SELECT` statement, without explanations or comments.**
- **Use table aliases (Example: `FROM garages g`)**
- **Define aliases in `FROM` or `JOIN` before using them.**
- **Ensure correct `JOIN ON` conditions for table relationships.**
- **For customers:** The query must include only `services`, `garage_services`, and `garages`.
- **For owners:** The query must include only `garages`, `services`, `garage_services`, and `vehicle_service_summary`.
- **For owners, strictly **prohibit** queries accessing the `users` table.**
- **For owners:** The query must filter using: `{garage_filter}`.
- **Ensure correct JOINs between `garage_services`, `garages`, and `services`.**
- **Never return data for garages the owner does not own.**
- **If an owner's revenue is needed, use:**
   SELECT g.garage_name, SUM(vs.total_amount) AS revenue FROM garages g JOIN vehicle_service_summary vs ON g.id = vs.garage_id WHERE {garage_filter} GROUP BY g.garage_name;
- **Do not include explanations, markdown, or placeholders like `<your_owner_id>`.**
- **Do not output queries that require write permissions (`INSERT`, `UPDATE`, `DELETE`).**
- **Ensure `g` is correctly aliased in `FROM` or `JOIN` before using it.**

#### Database Schema:
{schema}

#### Example Queries:
{retrieved_examples}

#### User's Question:
"{question}"

#### Correct SQL Query:
"""

    try:
        sql_query = query_ollama_together(prompt, "Qwen/Qwen2.5-Coder-32B-Instruct").strip()
        logging.debug(f"🟢 Generated SQL Query: {sql_query}")

        # ✅ Ensure the query is valid
        if not sql_query.lower().startswith("select"):
            logging.error(f"❌ Invalid SQL Query Generated: {sql_query}")
            state["sql_error"] = True
            state["query_result"] = {"error": "Query could not be generated correctly."}
            return state
        
        # ✅ Block Unauthorized Table Access
        

        # ✅ Fix Empty Owner Queries
        if user_role == "owner" and "WHERE g.owner_id IN ()" in sql_query:
            sql_query = sql_query.replace("WHERE g.owner_id IN ()", f"WHERE {garage_filter}").strip()

        state["sql_query"] = sql_query

    except Exception as e:
        logging.error(f"❌ SQL Generation Error: {str(e)}")
        state["sql_query"] = ""
        state["sql_error"] = True
        state["query_result"] = {"error": f"SQL Generation Error: {str(e)}"}

    return state

def generate_human_readable_response_with_llama(state):
    """Generate both a raw SQL query result and a human-readable response."""
    
    question = state["question"]
    query_result = state["query_result"]
    sql_query = state["sql_query"]

    # ✅ If there was an SQL error, return the raw error message
    if state["sql_error"]:
        state["query_result"] = {
            "raw_answer": query_result,  # Preserve raw query result
            "human_readable": f"An error occurred while executing the query: {query_result}"
        }
        return state

    # ✅ If query results are empty, provide a better response
    if not query_result or "data" not in query_result or not query_result["data"]:
        state["query_result"] = {
            "raw_answer": query_result,
            "human_readable": "No relevant data found for your query."
        }
        return state

    results = query_result["data"]

    # ✅ Convert query results into a structured format for AI processing
    formatted_results = "\n".join(
        [" | ".join(f"{key}: {value}" for key, value in row.items()) for row in results]
    )

    # ✅ Improved prompt for concise human-readable response
    prompt = f"""
    You are an AI assistant that explains SQL query results in a **concise and direct** way.

    **User's Question:** "{question}"
    **SQL Query:** {sql_query}

    **Database Results:** 
    {formatted_results}

    **Instructions:**
    - Provide a **one-sentence answer** summarizing the key information.
    - Do NOT assume missing details or add extra information.
    - If multiple records exist, summarize them concisely.
    - If there is no relevant data, respond with: "No relevant data found."

    **Final Answer:**
    """

    try:
        # ✅ Query a local LLM (replace "deepseek-llm:7b-chat" with your preferred model)
        response = query_ollama_together(prompt,"meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K" )
        response = response.strip() if response else "No human-readable answer available."

        state["query_result"] = {
            "raw_answer": results,  # ✅ Store raw SQL results
            "human_readable": response  # ✅ AI-generated explanation
        }

    except Exception as e:
        state["query_result"] = {
            "raw_answer": results,
            "human_readable": f"Error generating explanation: {str(e)}"
        }

    return state



# ✅ Define workflow nodes
workflow.add_node("convert_nl_to_sql", convert_nl_to_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_edge("convert_nl_to_sql", "execute_sql")
workflow.add_edge("execute_sql", END)
workflow.set_entry_point("convert_nl_to_sql")




#  You are an SQL query generator for MySQL. Follow these rules:
#     - **find [desired data] from [tables], where [conditions].**
#     - **retrieve [desired data] by joining [table1] and [table2] on [relationship], with conditions [conditions].**
#     - **calculate [aggregation function] for [desired data] from [table], where [conditions].**
#     - **find records in [table] where [column_name] LIKE '[value]'.**
#     - **find [desired data] from [table] where [conditions], ordered by [column_name] [ASC/DESC].**
#     - **find [desired data] from [table] where [conditions], ordered by (column_name IS NULL), column_name DESC.**
#     - **find [desired data] from [table] where [condition1] AND [condition2].**
#     - **find [desired data] by joining [table1], [table2], and [table3] on appropriate columns, where [conditions].**
#     - **All queries will use LIKE instead of ILIKE to handle case-insensitive searches.**
#     - **The query structure will be correct with proper JOIN ON clauses.**"meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"