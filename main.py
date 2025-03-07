# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from sql_agent import SessionLocal
# from models import User, Garage
# from workflow_engine import workflow
# import logging
# import time

# logging.basicConfig(level=logging.DEBUG)
# app = FastAPI()

# class QueryRequest(BaseModel):
#     user_id: int
#     role: str
#     question: str

# class QueryResponse(BaseModel):
#     query_result: dict
#     sql_error: bool
#     execution_time: float

# def get_user_garage(session: Session, user_id: int):
#     """Fetch garage_id if the user is an owner."""
#     garage = session.query(Garage).filter(Garage.owner_id == user_id).first()
#     return garage.id if garage else None

# @app.post("/ask_question", response_model=QueryResponse)
# def ask_question(request: QueryRequest):
#     session = SessionLocal()
#     start_time = time.time()

#     user_role = request.role.lower()
#     user_id = request.user_id
#     garage_id = get_user_garage(session, user_id) if user_role == "owner" else None

#     state = {
#         "question": request.question,
#         "sql_query": "",
#         "query_result": {"raw_answer": "No data", "human_readable": "No response generated."},
#         "sql_error": False,
#         "garage_id": garage_id,
#         "role": user_role  # ✅ Include role
#     }
#     config = {"configurable": {"session": session}}

#     try:
#         logging.debug(f"Query from user {user_id} ({user_role}): {request.question}")

#         app_workflow = workflow.compile()
#         result = app_workflow.invoke(input=state, config=config)

#         sql_query = result.get("sql_query", "").lower()

#         # ✅ Define allowed tables per role
#         ROLE_TABLE_ACCESS = {
#             "admin": ["users", "garages", "services", "garage_services", "vehicle_service_summary", "customer_vehicle_info"],
#             "owner": ["garages", "services", "garage_services", "vehicle_service_summary"],
#             "customer": ["services", "garage_services", "garages"]
#         }

#         allowed_tables = ROLE_TABLE_ACCESS.get(user_role, [])
#         if not any(table in sql_query for table in allowed_tables):
#             return QueryResponse(query_result={"raw_answer": "", "human_readable": "Query out of domain"}, sql_error=True, execution_time=round(time.time() - start_time, 3))

#         execution_time = round(time.time() - start_time, 3)
#         return QueryResponse(query_result=result.get("query_result", {}), sql_error=result["sql_error"], execution_time=execution_time)

#     except Exception as e:
#         logging.error(f"❌ ERROR: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

#     finally:
#         session.close()



from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sql_agent import SessionLocal
from models import Garage
from workflow_engine import workflow
import logging
import time  # ✅ Import time module

# ✅ Configure Logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# ✅ Request & Response Models
class QueryRequest(BaseModel):
    user_id: int  # 🔹 User selects their ID manually in UI
    role: str
    question: str

class QueryResponse(BaseModel):
    query_result: dict
    sql_error: bool
    execution_time: float  # ✅ Include execution time

# ✅ Get All Garage IDs for Owners
def get_user_garages(session: Session, user_id: int):
    """Fetch all garage IDs owned by the user."""
    return [g.id for g in session.query(Garage.id).filter(Garage.owner_id == user_id).all()]

@app.post("/ask_question", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """Process user query with role-based access control."""
    start_time = time.time()  # ✅ Start Timer

    user_role = request.role.lower()  # ✅ Ensure role comparison is case-insensitive
    user_id = request.user_id

    with SessionLocal() as session:
        garage_ids = get_user_garages(session, user_id) if user_role == "owner" else []
        garage_condition = f"g.owner_id IN ({', '.join(map(str, garage_ids))})" if garage_ids else ""

        # ✅ Initial Query State
        state = {
            "question": request.question,
            "sql_query": "",
            "query_result": {"raw_answer": "No data", "human_readable": "No response generated."},
            "sql_error": False,
            "garage_ids": garage_ids  # ✅ Always pass a list
        }
        config = {"configurable": {"session": session, "role": user_role}}  # ✅ Pass role to workflow

        try:
            logging.debug(f"Received query: {request.question} from user {request.user_id} with role {request.role}")

            # ✅ Compile and invoke workflow
            app_workflow = workflow.compile()
            result = app_workflow.invoke(input=state, config=config)

            execution_time = round(time.time() - start_time, 3)

            return QueryResponse(
                query_result=result.get("query_result", {}),
                sql_error=result["sql_error"],
                execution_time=execution_time  # ✅ Include execution time in response
            )

        except Exception as e:
            logging.error(f"❌ ERROR: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
