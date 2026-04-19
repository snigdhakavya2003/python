from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from topics import TOPICS
from ai_service import generate_question, evaluate_answer

app = FastAPI(title="Python Quiz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──────────────────────────────────────────────────────────────────
class QuestionRequest(BaseModel):
    topic: str
    difficulty: str


class EvaluateRequest(BaseModel):
    topic: str
    difficulty: str
    question: str
    user_answer: str


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/topics")
def get_topics():
    return {"topics": TOPICS}


@app.post("/get-question")
def get_question(req: QuestionRequest):
    # validate
    all_topics = [t for topics in TOPICS.values() for t in topics]
    if req.topic not in all_topics:
        raise HTTPException(status_code=400, detail="Invalid topic")
    if req.difficulty not in ["Beginner", "Intermediate", "Advanced"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty")

    result = generate_question(req.topic, req.difficulty)
    return result


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    if not req.user_answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")

    result = evaluate_answer(req.topic, req.difficulty, req.question, req.user_answer)
    return result


@app.get("/")
def root():
    return {"message": "Python Quiz API is running!"}
