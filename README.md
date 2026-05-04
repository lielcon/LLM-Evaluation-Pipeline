# LLM Evaluation Pipeline

A lightweight evaluation pipeline for benchmarking LLM answers against external reference answers.  
It is designed to be easy to run, easy to review, and safe to demo even without paid API quota.

## What This Project Does

Given a CSV of questions, the pipeline:
- loads questions
- gets reference answers from Wolfram Alpha (REST API)
- caches reference answers in Redis
- generates model answers with the OpenAI SDK (or deterministic demo fallback)
- scores semantic correctness with an LLM judge (or realistic demo scoring)
- saves results to a benchmark CSV file
- reports average model score and average latency

In demo mode, the project runs on 10 predefined factual questions and simulates realistic benchmarking behavior with correct, partially correct, and incorrect answers to produce meaningful score variation.

## How The Pipeline Works

1. **Load questions from CSV**  
   Reads questions from `data/General_Knowledge_Questions.csv` (supports header and no-header formats).

2. **Retrieve reference answers (Wolfram Alpha REST)**  
   Calls `https://api.wolframalpha.com/v2/query` and extracts the first useful plaintext answer.

3. **Cache reference answers (Redis)**  
   Uses Redis to cache Wolfram answers for 4 hours to reduce repeated API calls.

4. **Generate model answers (OpenAI SDK + demo fallback)**  
   Uses the configured model for short factual answers.  
   If demo mode is enabled or API usage fails, it falls back to deterministic demo answers over 10 predefined questions.

5. **Score answer accuracy (LLM judge)**  
   Uses a judge model to output a semantic correctness score between `0.0` and `1.0`.  
   In demo mode, scoring is deterministic and intentionally varied to reflect correct, partially correct, and incorrect outputs.

6. **Save benchmark results**  
   Writes results to `outputs/results.csv`.
   Also prints average model score and average latency for quick benchmarking summaries.

## Tech Stack

- Python
- OpenAI Python SDK (`openai`)
- Requests (`requests`)
- Redis (`redis`)
- Python Dotenv (`python-dotenv`)
- Wolfram Alpha REST API

## Setup

1. Clone/download the project.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration (`.env`)

Create a `.env` file in the project root with:

```env
WOLFRAM_APP_ID=your_wolfram_app_id
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o-mini
JUDGE_MODEL_NAME=gpt-4o-mini
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
DEMO_MODE=true
```

## Run

```bash
pip install -r requirements.txt
python src/main.py
```

Results will be saved to `outputs/results.csv`.

## Demo Mode (Recruiter-Friendly)

Set `DEMO_MODE=true` to run the full pipeline without paid OpenAI usage.  
The system is fully functional with real APIs, but also includes a demo mode that allows it to run without requiring paid API usage.

Demo mode includes:
- deterministic answers for 10 predefined questions
- realistic scoring with `1.0` (correct), `0.6` (partially correct), and `0.1` (incorrect)
- average model score calculation
- average latency calculation

This keeps the project reproducible and easy to evaluate while still resembling real benchmarking behavior.

## Evaluation Metrics

- **Per-question score:** semantic correctness score for each answer (`0.0` to `1.0`)
- **Average model score:** mean score across all evaluated questions
- **Average latency:** mean answer-generation time in milliseconds
