
# import os
# import json
# import faiss
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# import requests
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import text





# DATABASE_URL = os.getenv("DATABASE_URL_1", "mysql+pymysql://root:devanshjoshi@localhost/garage_management")
# print(f"🔍 Using database: {DATABASE_URL}")

# # ✅ Create database engine
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# # ✅ Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # ✅ Define SQL examples storage file
# EXAMPLES_FILE = "sql_examples.json"

# # ✅ Load SQL examples from file
# def load_sql_examples():
#     if os.path.exists(EXAMPLES_FILE):
#         with open(EXAMPLES_FILE, "r") as f:
#             return json.load(f)
#     return []

# # ✅ Save new SQL query example
# def save_sql_example(question, sql_query):
#     examples = load_sql_examples()
#     examples.append({"question": question, "sql_query": sql_query})

#     with open(EXAMPLES_FILE, "w") as f:
#         json.dump(examples, f, indent=4)

# # ✅ Use a Local Embedding Model
# def get_local_embeddings():
#     return HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

# # ✅ Build FAISS Vector Store using Local LLM
# def build_vector_store():
#     """Converts SQL examples into embeddings and stores them in FAISS."""
#     examples = load_sql_examples()
    
#     if not examples:
#         print("⚠️ No SQL examples found! Please add data to `sql_examples.json`.")
#         return None

#     texts = [ex["question"] + " | " + ex["sql_query"] for ex in examples]
#     embeddings = get_local_embeddings()

#     vector_store = FAISS.from_texts(texts, embeddings)
#     vector_store.save_local("faiss_sql_db")
#     print("✅ FAISS Vector Store built successfully!")

# # ✅ Retrieve Similar SQL Queries
# def retrieve_similar_queries(user_question, top_k=3):
#     """Finds the most relevant SQL queries from FAISS."""
#     embeddings = get_local_embeddings()
#     vector_store = FAISS.load_local("faiss_sql_db", embeddings, allow_dangerous_deserialization=True)
#     retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    
#     docs = retriever.get_relevant_documents(user_question)
#     return [doc.page_content for doc in docs]

# # ✅ Build FAISS DB at Startup (Only if Missing)
# if os.path.exists("faiss_sql_db"):
#     print("✅ FAISS database found, loading it...")
# else:
#     print("⚠️ FAISS database not found, rebuilding it...")
#     build_vector_store()

# # def query_ollama(prompt: str, model: str) -> str:
# #      """Interact with the Ollama API for SQL generation."""
# #      try:
# #          url = "http://127.0.0.1:11434/api/generate"
# #          payload = {"model": model, "prompt": prompt, "stream": False}

# #          response = requests.post(url, json=payload)
# #          response.raise_for_status()
        
# #          response_data = response.json()
# #          return response_data.get("response", "").strip()  # ✅ Extract response safely

# #      except requests.RequestException as e:
# #          return f"Error interacting with Ollama: {str(e)}"
# #      except ValueError as e:
# #          return f"Error parsing Ollama response: {str(e)}"
# #      except json.JSONDecodeError as e:
# #          return f"JSON decode error: {str(e)}"

# def query_ollama(prompt: str, model: str) -> str:
#     """Interact with the Ollama API for SQL generation."""
#     try:
#         url = "http://127.0.0.1:11434/api/generate"
#         payload = {"model": model, "prompt": prompt, "stream": False}

#         response = requests.post(url, json=payload)
#         response.raise_for_status()

#         response_data = response.json()
#         logging.debug(f"🔹 Ollama API Response: {json.dumps(response_data, indent=2)}")

#         response_text = response_data.get("response", "").strip()

#         if not response_text:
#             logging.error("❌ Ollama API returned an empty SQL query!")
#             return "Query not possible with current schema."

#         return response_text

#     except requests.RequestException as e:
#         return f"Error interacting with Ollama: {str(e)}"
#     except ValueError as e:
#         return f"Error parsing Ollama response: {str(e)}"
#     except json.JSONDecodeError as e:
#         return f"JSON decode error: {str(e)}"


# # def query_ollama(prompt: str, model: str) -> str:
# #     """Interact with the Together API for SQL generation."""
# #     try:
# #         url = "https://api.together.xyz/v1/chat/completions"
# #         headers = {
# #             "Authorization": f"Bearer d2e6fb732211ac24c7bd473cabe27ae43aab7cbf89c989c8e8c8a9458c49d77c",
# #             "Content-Type": "application/json"
# #         }
# #         payload = {
# #             "model": model,
# #             "messages": [{"role": "user", "content": prompt}],
# #             "max_tokens": None,
# #             "temperature": 0.7,
# #             "top_p": 0.7,
# #             "top_k": 50,
# #             "repetition_penalty": 1,
# #             "stop": ["\n"]
# #         }

# #         response = requests.post(url, headers=headers, json=payload)
# #         response.raise_for_status()
       
# #         response_data = response.json()
# #         print(response_data)
# #         return response_data["choices"][0]["message"]["content"].strip()

# #     except requests.RequestException as e:
# #         return f"Error interacting with Together API: {str(e)}"
# #     except ValueError as e:
# #         return f"Error parsing Together API response: {str(e)}"
# #     except json.JSONDecodeError as e:
# #         return f"JSON decode error: {str(e)}"


# def get_database_schema(session):
#     """Retrieve the database schema dynamically from MySQL."""
#     schema = {}

#     # ✅ Fetch all table names
#     tables_result = session.execute(text("SHOW TABLES")).fetchall()

#     for table in tables_result:
#         table_name = table[0]

#         # ✅ Use text() for MySQL query
#         columns_result = session.execute(text(f"SHOW COLUMNS FROM `{table_name}`")).fetchall()
        
#         schema[table_name] = [column[0] for column in columns_result]

#     return schema

# __all__ = ["SessionLocal"]

# import os
# import json
# import faiss
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# import requests
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import text


# DATABASE_URL = os.getenv("DATABASE_URL_1", "mysql+pymysql://root:devanshjoshi@localhost/garage_management")
# print(f"🔍 Using database: {DATABASE_URL}")

# # ✅ Create database engine
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# # ✅ Create session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # ✅ Define SQL examples storage file
# EXAMPLES_FILE = "sql_examples.json"

# # ✅ Load SQL examples from file
# def load_sql_examples():
#     if os.path.exists(EXAMPLES_FILE):
#         with open(EXAMPLES_FILE, "r") as f:
#             return json.load(f)
#     return []

# # ✅ Save new SQL query example
# def save_sql_example(question, sql_query):
#     examples = load_sql_examples()
#     examples.append({"question": question, "sql_query": sql_query})

#     with open(EXAMPLES_FILE, "w") as f:
#         json.dump(examples, f, indent=4)

# # ✅ Use a Local Embedding Model
# def get_local_embeddings():
#     return HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

# # ✅ Build FAISS Vector Store using Local LLM
# def build_vector_store():
#     """Converts SQL examples into embeddings and stores them in FAISS."""
#     examples = load_sql_examples()
    
#     if not examples:
#         print("⚠️ No SQL examples found! Please add data to `sql_examples.json`.")
#         return None

#     texts = [ex["question"] + " | " + ex["sql_query"] for ex in examples]
#     embeddings = get_local_embeddings()

#     vector_store = FAISS.from_texts(texts, embeddings)
#     vector_store.save_local("faiss_sql_db")
#     print("✅ FAISS Vector Store built successfully!")

# # ✅ Retrieve Similar SQL Queries
# def retrieve_similar_queries(user_question, top_k=3):
#     """Finds the most relevant SQL queries from FAISS."""
#     embeddings = get_local_embeddings()
#     vector_store = FAISS.load_local("faiss_sql_db", embeddings, allow_dangerous_deserialization=True)
#     retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    
#     docs = retriever.get_relevant_documents(user_question)
#     return [doc.page_content for doc in docs]

# # ✅ Build FAISS DB at Startup (Only if Missing)
# if os.path.exists("faiss_sql_db"):
#     print("✅ FAISS database found, loading it...")
# else:
#     print("⚠️ FAISS database not found, rebuilding it...")
#     build_vector_store()
# def query_ollama(prompt: str, model: str) -> str:
#     """Interact with the Ollama API for SQL generation."""
#     try:
#         url = "http://127.0.0.1:11434/api/generate"
#         payload = {"model": model, "prompt": prompt, "stream": False}

#         response = requests.post(url, json=payload)
#         response.raise_for_status()
        
#         response_data = response.json()
#         return response_data.get("response", "").strip()  # ✅ Extract response safely

#     except requests.RequestException as e:
#         return f"Error interacting with Ollama: {str(e)}"
#     except ValueError as e:
#         return f"Error parsing Ollama response: {str(e)}"
#     except json.JSONDecodeError as e:
#         return f"JSON decode error: {str(e)}"


# def get_database_schema(session):
#     """Retrieve the database schema dynamically from MySQL."""
#     schema = {}

#     # ✅ Fetch all table names
#     tables_result = session.execute(text("SHOW TABLES")).fetchall()

#     for table in tables_result:
#         table_name = table[0]

#         # ✅ Use text() for MySQL query
#         columns_result = session.execute(text(f"SHOW COLUMNS FROM `{table_name}`")).fetchall()
        
#         schema[table_name] = [column[0] for column in columns_result]

#     return schema

# __all__ = ["SessionLocal"]



import os
import json
import faiss
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


DATABASE_URL = os.getenv("DATABASE_URL_1", "mysql+pymysql://root:devanshjoshi@localhost/garage_management")
print(f"🔍 Using database: {DATABASE_URL}")

# ✅ Create database engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ✅ Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ✅ Define SQL examples storage file
EXAMPLES_FILE = "sql_examples.json"

# ✅ Load SQL examples from file
def load_sql_examples():
    if os.path.exists(EXAMPLES_FILE):
        with open(EXAMPLES_FILE, "r") as f:
            return json.load(f)
    return []

# ✅ Save new SQL query example
def save_sql_example(question, sql_query):
    examples = load_sql_examples()
    examples.append({"question": question, "sql_query": sql_query})

    with open(EXAMPLES_FILE, "w") as f:
        json.dump(examples, f, indent=4)

# ✅ Use a Local Embedding Model
def get_local_embeddings():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

# ✅ Build FAISS Vector Store using Local LLM
def build_vector_store():
    """Converts SQL examples into embeddings and stores them in FAISS."""
    examples = load_sql_examples()
    
    if not examples:
        print("⚠️ No SQL examples found! Please add data to `sql_examples.json`.")
        return None

    texts = [ex["question"] + " | " + ex["sql_query"] for ex in examples]
    embeddings = get_local_embeddings()

    vector_store = FAISS.from_texts(texts, embeddings)
    vector_store.save_local("faiss_sql_db")
    print("✅ FAISS Vector Store built successfully!")

# ✅ Retrieve Similar SQL Queries
def retrieve_similar_queries(user_question, top_k=3):
    """Finds the most relevant SQL queries from FAISS."""
    embeddings = get_local_embeddings()
    vector_store = FAISS.load_local("faiss_sql_db", embeddings, allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    
    docs = retriever.get_relevant_documents(user_question)
    return [doc.page_content for doc in docs]

# ✅ Build FAISS DB at Startup (Only if Missing)
if os.path.exists("faiss_sql_db"):
    print("✅ FAISS database found, loading it...")
else:
    print("⚠️ FAISS database not found, rebuilding it...")
    build_vector_store()

def query_ollama_together(prompt: str, model: str) -> str:
    """Interact with the Together API for SQL generation."""
    print(f"🚀 Querying Together API with model: {model}")
    try:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer d2e6fb732211ac24c7bd473cabe27ae43aab7cbf89c989c8e8c8a9458c49d77c",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": None,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["\n"]
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        print(response_data)
        return response_data["choices"][0]["message"]["content"].strip()

    except requests.RequestException as e:
        return f"Error interacting with Together API: {str(e)}"
    except ValueError as e:
        return f"Error parsing Together API response: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON decode error: {str(e)}"




def get_database_schema(session):
    """Retrieve the database schema dynamically from MySQL."""
    schema = {}

    # ✅ Fetch all table names
    tables_result = session.execute(text("SHOW TABLES")).fetchall()

    for table in tables_result:
        table_name = table[0]

        # ✅ Use text() for MySQL query
        columns_result = session.execute(text(f"SHOW COLUMNS FROM `{table_name}`")).fetchall()
        
        schema[table_name] = [column[0] for column in columns_result]

    return schema

__all__ = ["SessionLocal"]
