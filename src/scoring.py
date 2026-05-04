import re
from typing import Optional

from config import DEMO_MODE, JUDGE_MODEL_NAME, OPENAI_API_KEY
from clients import openai_client


def _normalize(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().lower()


def _demo_score(question: str, reference_answer: str | None, model_answer: str) -> float:
    _ = reference_answer  # Reserved for future demo rules that use the reference text.

    normalized_question = _normalize(question)
    normalized_answer = _normalize(model_answer)

    demo_scores = {
        "who wrote hamlet?": {"william shakespeare": 1.0},
        "what is the capital of france?": {"lyon": 0.1},
        "what is 5+7?": {"12": 1.0},
        "who was the first president of the united states?": {"george washington": 1.0},
        "what is the boiling point of water in celsius?": {"90°c": 0.6},
        "what planet is known as the red planet?": {"mars": 1.0},
        "what is the largest ocean on earth?": {"atlantic ocean": 0.1},
        "who painted the mona lisa?": {"leonardo da vinci": 1.0},
        "what gas do plants absorb from the atmosphere?": {"oxygen": 0.1},
        "what is the square root of 64?": {"8": 1.0},
    }

    answer_scores = demo_scores.get(normalized_question)
    if answer_scores is None:
        return 0.0
    return answer_scores.get(normalized_answer, 0.0)


def _extract_first_score(text: str) -> Optional[float]:
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        value = float(match.group(0))
    except ValueError:
        return None
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def judge_answer(question: str, reference_answer: str | None, model_answer: str) -> float:
    if DEMO_MODE:
        return _demo_score(question, reference_answer, model_answer)

    if not OPENAI_API_KEY or openai_client is None:
        print("Warning: Judge model unavailable. Falling back to demo scoring.")
        return _demo_score(question, reference_answer, model_answer)

    try:
        response = openai_client.chat.completions.create(
            model=JUDGE_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Score semantic correctness of a model answer compared to a reference answer.\n"
                        "Return only one float between 0.0 and 1.0.\n"
                        f"Question: {question}\n"
                        f"Reference answer: {reference_answer}\n"
                        f"Model answer: {model_answer}"
                    ),
                }
            ],
            temperature=0,
        )
        content = response.choices[0].message.content
        if not isinstance(content, str):
            print("Warning: Judge model returned non-text content. Falling back to demo scoring.")
            return _demo_score(question, reference_answer, model_answer)

        score = _extract_first_score(content)
        if score is None:
            print("Warning: Could not parse judge score. Falling back to demo scoring.")
            return _demo_score(question, reference_answer, model_answer)
        return score
    except Exception as exc:
        print(f"Warning: Judge model call failed ({exc}). Falling back to demo scoring.")
        return _demo_score(question, reference_answer, model_answer)
