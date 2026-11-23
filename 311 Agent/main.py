import logging
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import Query, parse_question
from predictor import predict_resolution_range, get_parser_categories, format_duration

import re
from functools import lru_cache

GENERIC_WORDS = {
    "and", "the", "of", "for", "in", "on", "or", "with", "non", "other",
    "unknown", "condition", "complaint", "request", "general", "service",
    "type", "a", "an", "to", "at",
}

EXTRA_KEYWORDS = {
    "pothole", "streetlight", "light", "lamp", "sidewalk", "road", "crosswalk",
    "signal", "traffic", "sign", "hydrant", "sewer", "manhole", "bridge",
    "noise", "noisy", "loud", "music", "party", "construction", "barking",
    "trash", "garbage", "litter", "dump", "dumping", "dirty", "recycling",
    "rat", "mice", "mouse", "roach", "cockroach", "pest", "bedbug", "rodent",
    "heat", "heating", "hot", "water", "leak", "mold", "paint", "lead",
    "elevator", "plumbing", "ceiling", "boiler", "landlord", "apartment",
    "building", "tenant", "parking", "parked", "blocked", "driveway", "idling", 
    "abandoned", "taxi", "bike", "vehicle", "car", "graffiti", "tree", "branch", 
    "park", "smoke", "smoking", "drug", "homeless", "311",
}

BOROUGH_WORDS = {"manhattan", "brooklyn", "queens", "bronx", "staten", "island"}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

def _normalize(word: str) -> str:
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word

@lru_cache(maxsize=1)
def get_311_keywords() -> frozenset[str]:
    categories = get_parser_categories()
    words: set[str] = set()
    for field in ("complaint_type", "location_type"):
        for category in categories[field]:
            for w in _tokenize(category):
                if w not in GENERIC_WORDS and len(w) > 2:
                    words.add(_normalize(w))
    words |= {_normalize(w) for w in EXTRA_KEYWORDS}
    words |= BOROUGH_WORDS
    return frozenset(words)

def looks_like_complaint(question: str) -> bool:
    keywords = get_311_keywords()
    return any(_normalize(w) in keywords for w in _tokenize(question))

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
    confirmed: bool = False

class ChatResponse(BaseModel):
    status: str
    query: Query
    missing_fields: list[str]
    pending_field: str | None = None
    message: str
    options: list[str] | None = None
    confirmed: bool = False

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

VALID_PENDING_FIELDS = REQUIRED_FIELDS + ["confirmation"]
CONFIRM_OPTIONS = ["Yes", "No"]

YES_WORDS = {
    "yes", "y", "yeah", "yep", "yup", "correct", "right", "thats right",
    "that's right", "looks good", "ok", "okay", "sure", "confirm", "confirmed",
}
NO_WORDS = {"no", "n", "nope", "nah", "wrong", "incorrect", "not quite"}

def normalize_reply(text: str) -> str:
    return re.sub(r"[^a-z' ]", "", text.lower()).strip()

def get_confirmation_message(query: Query) -> str:
    msg = f'I currently have "{query.complaint_type}"'
    if query.location_type:
        msg += f' in "{query.location_type}"'
    return msg + ". Is this correct?"

def core(query: Query) -> tuple:
    return (query.complaint_type, query.location_type)

def confirmation_response(query: Query, corrected: bool = False) -> ChatResponse:
    prefix = "Sorry about that. " if corrected else ""
    return ChatResponse(
        status="needs_clarification",
        query=query,
        missing_fields=get_missing_fields(query),
        pending_field="confirmation",
        message=prefix + get_confirmation_message(query),
        options=CONFIRM_OPTIONS,
        confirmed=False,
    )

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
    low: float
    median: float
    high: float
    estimate: str

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

    confirmed = request.confirmed
    corrected = False

    # First message
    if request.query is None:
        if not looks_like_complaint(question):
            raise HTTPException(
                status_code=422,
                detail="I can only estimate NYC 311 complaints. Describe the issue and where it happened, e.g. 'Streetlight out on 31st Ave in Queens.'",
            )
        try:
            query = parse_question(question)
        except Exception:
            logger.exception("Failed to parse NYC 311 question")
            raise HTTPException(status_code=502, detail="The AI service failed to process your question.")
        confirmed = False

    # Follow-up messages
    else:
        field = request.pending_field
        if field not in VALID_PENDING_FIELDS:
            raise HTTPException(status_code=400, detail="Invalid or missing pending_field.")

        if field == "confirmation":
            reply = normalize_reply(question)

            if reply in YES_WORDS:
                query = request.query
                confirmed = True

            elif reply in NO_WORDS:
                return ChatResponse(
                    status="needs_clarification",
                    query=request.query,
                    missing_fields=get_missing_fields(request.query),
                    pending_field="confirmation",
                    message='No problem. What should I change? (e.g. "it\'s in my home")',
                    confirmed=False,
                )

            else:
                try:
                    query = parse_question(question, current_query=request.query)
                except Exception:
                    logger.exception("Failed to parse correction")
                    raise HTTPException(status_code=502, detail="The AI service failed to process your answer.")

                if query == request.query:
                    return ChatResponse(
                        status="needs_clarification",
                        query=query,
                        missing_fields=get_missing_fields(query),
                        pending_field="confirmation",
                        message="I couldn't tell what to change. Is it the issue or the location that's wrong?",
                        confirmed=False,
                    )
                corrected = True
                confirmed = False

        elif field == "open_data_channel_type":
            lookup = {c.lower(): c for c in get_channel_options()}
            value = lookup.get(question.lower())

            if value is not None:
                query = request.query.model_copy(update={field: value})
            else:
                try:
                    query = parse_question(question, current_query=request.query)
                except Exception:
                    logger.exception("Failed to parse follow-up")
                    raise HTTPException(status_code=502, detail="The AI service failed to process your answer.")

                if not query.open_data_channel_type:
                    return ChatResponse(
                        status="needs_clarification",
                        query=query,
                        missing_fields=get_missing_fields(query),
                        pending_field=field,
                        message="Please choose one of the options below.",
                        options=get_channel_options(),
                        confirmed=confirmed and core(query) == core(request.query),
                    )
        else:
            try:
                query = parse_question(question, current_query=request.query)
            except Exception:
                logger.exception("Failed to parse follow-up")
                raise HTTPException(status_code=502, detail="The AI service failed to process your answer.")

        # Any change to issue/location needs re-confirming
        if core(query) != core(request.query):
            confirmed = False

    # Confirm what we understood before asking anything else
    if not confirmed and query.complaint_type:
        return confirmation_response(query, corrected)

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
            confirmed=confirmed,
        )

    return ChatResponse(
        status="ready",
        query=query,
        missing_fields=[],
        pending_field=None,
        message="I have all the required information.",
        confirmed=True,
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
        low, median, high = predict_resolution_range(query)
    except Exception:
        logger.exception("Failed to predict resolution time")
        raise HTTPException(
            status_code=502,
            detail="Failed to generate a prediction.",
        )

    def strip_about(text):
        return text.removeprefix("about ")

    estimate = (
        f"{format_duration(median)} — most complaints like this resolve "
        f"between {strip_about(format_duration(low))} and {strip_about(format_duration(high))}"
    )
    return PredictionResponse(low=low, median=median, high=high, estimate=estimate)