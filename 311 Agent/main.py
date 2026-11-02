import logging
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import Query, parse_question
from predictor import predict_resolution_hours, get_parser_categories

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

class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    query: Query | None = None
    pending_field: str | None = None

class ChatResponse(BaseModel):
    status: str
    query: Query
    missing_fields: list[str]
    pending_field: str | None = None
    message: str
    options: list[str] | None = None

def get_channel_options() -> list[str]:
    return [
        c for c in get_parser_categories()["open_data_channel_type"]
        if c.upper() != "UNKNOWN"
    ]

def get_followup_message(field: str) -> str:
    return {
        "complaint_type": "What type of 311 issue are you reporting?",
        "location_type": "Where did the issue occur?",
        "open_data_channel_type": "How was the 311 complaint submitted? Was it through, phone, mobile, email, or other?",
    }[field]

REQUIRED_FIELDS = [
    "complaint_type",
    "location_type",
    "open_data_channel_type",
]

def get_missing_fields(query: Query) -> list[str]:
    return [
        field
        for field in REQUIRED_FIELDS
        if not (getattr(query, field) or "").strip()
    ]

def debug_print(label: str, **data):
    print(f"\n===== {label} =====")
    for key, value in data.items():
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        print(f"{key}: {json.dumps(value, indent=2, default=str)}")
    print("=" * (len(label) + 12))

class PredictionResponse(BaseModel):
    hours: float

class PredictionRequest(BaseModel):
    query: Query

@app.get("/")
def home():
    return {"message": "NYC 311 Complaint Assistant API is running"}

@app.post("/api/parse", response_model=ChatResponse)
def parse_complaint(request: ChatRequest):
    debug_print(
        "INCOMING",
        question=request.question,
        pending_field=request.pending_field,
        query=request.query,
    )

    response = handle_parse(request)

    debug_print(
        "OUTGOING",
        status=response.status,
        query=response.query,
        missing_fields=response.missing_fields,
        pending_field=response.pending_field,
        options=response.options,
        message=response.message,
    )
    return response

def handle_parse(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # First message
    if request.query is None:
        try:
            query = parse_question(question)
        except Exception:
            logger.exception("Failed to parse NYC 311 question")
            raise HTTPException(status_code=502, detail="The AI service failed to process your question.")

    # Follow-up messages
    else:
        field = request.pending_field
        if field not in REQUIRED_FIELDS:
            raise HTTPException(status_code=400, detail="Invalid or missing pending_field.")

        if field == "open_data_channel_type":
            lookup = {c.lower(): c for c in get_channel_options()}
            value = lookup.get(question.lower())

            if value is not None:
                query = request.query.model_copy(update={field: value})
            else:
                try:
                    query = parse_question(question, current_query=request.query)
                except Exception:
                    logger.exception("Failed to parse follow-up")
                    raise HTTPException(
                        status_code=502,
                        detail="The AI service failed to process your answer.",
                    )

                if not query.open_data_channel_type:
                    return ChatResponse(
                        status="needs_clarification",
                        query=query,
                        missing_fields=get_missing_fields(query),
                        pending_field=field,
                        message="Please choose one of the options below.",
                        options=get_channel_options(),
                    )
        else:
            try:
                query = parse_question(question, current_query=request.query)
            except Exception:
                logger.exception("Failed to parse follow-up")
                raise HTTPException(status_code=502, detail="The AI service failed to process your answer.")

    missing_fields = get_missing_fields(query)

    if missing_fields:
        next_field = missing_fields[0]
        return ChatResponse(
            status="needs_clarification",
            query=query,
            missing_fields=missing_fields,
            pending_field=next_field,
            message=get_followup_message(next_field),
            options=get_channel_options() if next_field == "open_data_channel_type" else None,
        )

    return ChatResponse(
        status="ready",
        query=query,
        missing_fields=[],
        pending_field=None,
        message="I have all the required information.",
    )


@app.post("/api/predict", response_model=PredictionResponse)
def predict_complaint(request: PredictionRequest):
    query = request.query

    missing_fields = get_missing_fields(query)

    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Required fields are missing.",
                "missing_fields": missing_fields,
            },
        )

    try:
        hours = predict_resolution_hours(query)
    except Exception:
        logger.exception("Failed to predict resolution time")
        raise HTTPException(
            status_code=502,
            detail="Failed to generate a prediction.",
        )

    return PredictionResponse(hours=hours)