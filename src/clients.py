from typing import Optional

import requests

from config import DEMO_MODE, OPENAI_API_KEY, WOLFRAM_APP_ID
from cache import get_cached_wolfram_answer, set_cached_wolfram_answer

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


openai_client = OpenAI(api_key=OPENAI_API_KEY) if OpenAI is not None and OPENAI_API_KEY else None


def wolfram_alpha_query(question: str) -> tuple[Optional[str], bool]:
    if not WOLFRAM_APP_ID:
        print("WOLFRAM_APP_ID is missing. Reference answer will be None.")
        return None, False

    cached_answer = get_cached_wolfram_answer(question)
    if cached_answer is not None:
        print(f"Cache hit for question: {question}")
        return cached_answer, True

    try:
        response = requests.get(
            "https://api.wolframalpha.com/v2/query",
            params={
                "input": question,
                "appid": WOLFRAM_APP_ID,
                "output": "JSON",
                "format": "plaintext",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None, False

    try:
        payload = response.json()
    except ValueError:
        return None, False

    query_result = payload.get("queryresult")
    if not isinstance(query_result, dict):
        return None, False

    pods = query_result.get("pods")
    if not isinstance(pods, list):
        return None, False

    for pod in pods:
        if not isinstance(pod, dict):
            continue
        subpods = pod.get("subpods")
        if not isinstance(subpods, list):
            continue
        for subpod in subpods:
            if not isinstance(subpod, dict):
                continue
            plaintext = subpod.get("plaintext")
            if isinstance(plaintext, str):
                cleaned = plaintext.strip()
                if cleaned:
                    set_cached_wolfram_answer(question, cleaned)
                    return cleaned, False

    return None, False


def get_demo_answer(question: str) -> str:
    normalized = question.strip().lower()

    if "who wrote hamlet?" in normalized or "who wrote hamlet" in normalized:
        return "William Shakespeare"
    if "what is the capital of france?" in normalized or "what is the capital of france" in normalized:
        return "Lyon"
    if "what is 5+7?" in normalized or "what is 5+7" in normalized or "what is 5 + 7?" in normalized or "what is 5 + 7" in normalized:
        return "12"
    if (
        "who was the first president of the united states?" in normalized
        or "who was the first president of the united states" in normalized
    ):
        return "George Washington"
    if (
        "what is the boiling point of water in celsius?" in normalized
        or "what is the boiling point of water in celsius" in normalized
    ):
        return "90°C"
    if (
        "what planet is known as the red planet?" in normalized
        or "what planet is known as the red planet" in normalized
    ):
        return "Mars"
    if (
        "what is the largest ocean on earth?" in normalized
        or "what is the largest ocean on earth" in normalized
    ):
        return "Atlantic Ocean"
    if "who painted the mona lisa?" in normalized or "who painted the mona lisa" in normalized:
        return "Leonardo da Vinci"
    if (
        "what gas do plants absorb from the atmosphere?" in normalized
        or "what gas do plants absorb from the atmosphere" in normalized
    ):
        return "Oxygen"
    if "what is the square root of 64?" in normalized or "what is the square root of 64" in normalized:
        return "8"

    return "This is a demo factual answer for testing the evaluation pipeline."


def get_model_answer(model_name: str, question: str) -> str:
    # Demo mode allows the project to be reviewed and tested without requiring paid API usage.
    if DEMO_MODE:
        return get_demo_answer(question)
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY is missing. Falling back to demo answer.")
        return get_demo_answer(question)
    if openai_client is None:
        print("Warning: OpenAI client is unavailable. Falling back to demo answer.")
        return get_demo_answer(question)

    try:
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Give a short, factual answer to this question.\n"
                        f"Question: {question}"
                    ),
                }
            ],
            temperature=0,
        )
        content = response.choices[0].message.content
        if isinstance(content, str) and content.strip():
            return content.strip()
        print("Warning: OpenAI returned empty content. Falling back to demo answer.")
        return get_demo_answer(question)
    except Exception as exc:
        print(f"Warning: OpenAI call failed ({exc}). Falling back to demo answer.")
        return get_demo_answer(question)
