import csv
import os
import time

from clients import get_model_answer, wolfram_alpha_query
from config import CSV_PATH, MODEL_NAME, OUTPUT_PATH
from scoring import judge_answer


def load_questions(csv_path: str) -> list[str]:
    questions: list[str] = []
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as file:
            rows = list(csv.reader(file))
    except FileNotFoundError:
        return []

    if not rows:
        return []

    first_data_row_index = None
    for index, row in enumerate(rows):
        if not row:
            continue
        first_cell = row[0].strip() if row[0] else ""
        if not first_cell or first_cell.startswith("#"):
            continue
        first_data_row_index = index
        break

    if first_data_row_index is None:
        return []

    first_data_row = rows[first_data_row_index]
    normalized_header = [cell.strip().lower() for cell in first_data_row]
    question_col_index = normalized_header.index("question") if "question" in normalized_header else None

    if question_col_index is not None:
        for row in rows[first_data_row_index + 1:]:
            if question_col_index >= len(row):
                continue
            question = row[question_col_index].strip()
            if not question or question.startswith("#"):
                continue
            questions.append(question)
        return questions

    for row in rows[first_data_row_index:]:
        if not row:
            continue
        first_cell = row[0].strip() if row[0] else ""
        if not first_cell or first_cell.startswith("#"):
            continue
        questions.append(first_cell)

    return questions


def run_evaluation() -> list[dict]:
    questions = load_questions(CSV_PATH)
    rows: list[dict] = []

    for question in questions:
        reference_answer, cached = wolfram_alpha_query(question)
        start = time.time()
        answer = get_model_answer(MODEL_NAME, question)
        elapsed_ms = int((time.time() - start) * 1000)
        score = judge_answer(question, reference_answer, answer)

        rows.append(
            {
                "Question": question,
                "Model": MODEL_NAME,
                "Answer": answer,
                "ReferenceAnswer": reference_answer,
                "Score": score,
                "Cached": cached,
                "TimeInMillisecondsToGetAnswer": elapsed_ms,
            }
        )

    print(f"Questions loaded: {len(questions)}")
    print(f"Total evaluations: {len(rows)}")
    if rows:
        average_score = sum(float(row["Score"]) for row in rows) / len(rows)
        average_latency_ms = int(
            sum(int(row["TimeInMillisecondsToGetAnswer"]) for row in rows) / len(rows)
        )
        print(f"Average model score: {average_score:.2f}")
        print(f"Average latency: {average_latency_ms} ms")
        print(f"Sample result: {rows[0]}")

    return rows


def save_results(rows: list[dict]) -> None:
    os.makedirs("outputs", exist_ok=True)
    fieldnames = [
        "Question",
        "Model",
        "Answer",
        "ReferenceAnswer",
        "Score",
        "Cached",
        "TimeInMillisecondsToGetAnswer",
    ]
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Results saved to outputs/results.csv")
