import pandas as pd
from typing import List, Optional
from fastapi import FastAPI, Query, Request
from starlette.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI(
    title="Student API",
    description="API to fetch student details with optional class filtering",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_pna_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# Load the student data from CSV (safe load with fillna)
try:
    students_df = pd.read_csv("q-fastapi(1).csv").fillna("")
except FileNotFoundError:
    # fallback empty dataframe if CSV missing
    students_df = pd.DataFrame(columns=["studentId", "class"])

@app.get("/api")
def get_students(class_filter: Optional[List[str]] = Query(None, alias="class")):
    """
    Serves student data.

    - No `class` query param → returns all students.
    - With one or more `class` params → returns students
      belonging to those classes.
    Example: /api?class=1A&class=2B
    """
    if not class_filter:
        filtered_df = students_df
    else:
        filtered_df = students_df[students_df["class"].isin(class_filter)]

    return {"students": filtered_df.to_dict("records")}
