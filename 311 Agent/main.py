import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import Query, parse_question
from predictor import predict_resolution_hours

app = FastAPI(
    title="NYC 311 Complaint Assistant AI",
    description="Parses natural language questions about NYC 311 complaints",
    version="1.0.0",
)

logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5000,
        description="The user's question",
    )

class PredictionResponse(BaseModel):
    hours: float

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

    try:
        result = parse_question(question)
        return result

    except Exception:
        logger.exception("Failed to parse NYC 311 question")

        raise HTTPException(
            status_code=502,
            detail='The AI service failed to process your question',
        )

@app.post("/api/predict", response_model=PredictionResponse)
def predict_complaint(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        query = parse_question(question)
    except Exception:
        logger.exception("Failed to parse NYC 311 question")
        raise HTTPException(
            status_code=502,
            detail='The AI service failed to process your question',
        )

    try:
        hours = predict_resolution_hours(query)
    except Exception:
        logger.exception("Failed to predict resolution time")
        raise HTTPException(
            status_code=502,
            detail='Failed to generate a prediction',
        )

    return PredictionResponse(hours=hours)