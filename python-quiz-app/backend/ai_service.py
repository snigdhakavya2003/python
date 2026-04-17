from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_question(topic: str, difficulty: str) -> dict:
    prompt = f"""You are a Python interview coach.
Generate a {difficulty} level coding question on the topic: "{topic}".

Return ONLY a JSON object in this exact format (no markdown, no extra text):
{{
  "question": "Clear problem statement here",
  "example_input": "example input if applicable, else empty string",
  "expected_output": "expected output if applicable, else empty string",
  "hint": "one small helpful hint"
}}"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )

    import json
    raw = response.choices[0].message.content.strip()
    # strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except Exception:
        return {
            "question": raw,
            "example_input": "",
            "expected_output": "",
            "hint": "",
        }


def evaluate_answer(topic: str, difficulty: str, question: str, user_answer: str) -> dict:
    prompt = f"""You are a Python interview coach evaluating a student's answer.

Topic: {topic}
Difficulty: {difficulty}
Question: {question}
Student's Answer: {user_answer}

Evaluate and return ONLY a JSON object in this exact format (no markdown, no extra text):
{{
  "verdict": "Correct" or "Partially Correct" or "Incorrect",
  "score": a number from 0 to 10,
  "what_was_good": "what the student did well",
  "what_was_missing": "what was missing or wrong",
  "ideal_answer": "the ideal solution or explanation",
  "tip": "one tip to improve"
}}"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.3,
    )

    import json
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except Exception:
        return {
            "verdict": "Could not evaluate",
            "score": 0,
            "what_was_good": "",
            "what_was_missing": "",
            "ideal_answer": raw,
            "tip": "",
        }
