import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import re

from agent import Query, parse_question

KEYWORDS = {
    "complaint", "311", "nyc", "nyc 311",
    "noise", "loud", "parking", "driveway",
    "street", "sidewalk", "pothole", "streetlight",
    "light", "heat", "hot water", "water",
    "trash", "garbage", "sanitation", "building",
    "construction", "blocked", "hydrant", "rat",
    "mice", "rodent", "sewer", "leak", "plumbing",
    "traffic", "tree", "graffiti", "electric",
    "elevator", "apartment", "landlord", "heat",
    "resolve", "resolution", "repair", "broken",
    "take", "long", "status", "report", "service",
}

def is_question(question: str) -> bool:
    words = set(re.findall(r"[a-z0-9]+", question.lower()))
    return bool(words & KEYWORDS)

app = FastAPI(
    title="NYC 311 Complaint Assistant AI",
    description="Parses natural language questions about NYC 311 complaints",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5000,
        description="The user's question",
    )

@app.get("/")
def home():
    return {"message": "NYC 311 Complaint Assistant API is running"}

@app.post("/api/parse", response_model=Query)
def parse_complaint(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if not is_question(question):
        raise HTTPException(
            status_code=400,
            detail="Please ask a question about an NYC 311 complaint."
        )

    try:
        result = parse_question(question)
        return result

    except Exception:
        logger.exception("Failed to parse NYC 311 question")

        raise HTTPException(
            status_code=502,
            detail='The AI service failed to process your question',
        )