# LLM Evaluation Pipeline

A lightweight evaluation pipeline for benchmarking LLM answers against external reference answers.  
It is designed to be easy to run, easy to review, and safe to demo even without paid API quota.

## What This Project Does

Given a CSV of questions, the pipeline:
- loads questions
- gets reference answers from Wolfram Alpha (REST API)
- caches reference answers in Redis
- generates model answers with the OpenAI SDK (or demo fallback)
- scores semantic correctness with an LLM judge
- saves results to a benchmark CSV file

## How The Pipeline Works

1. **Load questions from CSV**  
   Reads questions from `data/General_Knowledge_Questions.csv` (supports header and no-header formats).

2. **Retrieve reference answers (Wolfram Alpha REST)**  
   Calls `https://api.wolframalpha.com/v2/query` and extracts the first useful plaintext answer.

3. **Cache reference answers (Redis)**  
   Uses Redis to cache Wolfram answers for 4 hours to reduce repeated API calls.

4. **Generate model answers (OpenAI SDK + demo fallback)**  
   Uses the configured model for short factual answers.  
   If demo mode is enabled or API usage fails, it falls back to deterministic demo answers.

5. **Score answer accuracy (LLM judge)**  
   Uses a judge model to output a semantic correctness score between `0.0` and `1.0`.

6. **Save benchmark results**  
   Writes results to `outputs/results.csv`.

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
In this mode, answer generation and scoring use deterministic fallback logic, so reviewers can run and inspect the project end-to-end without API quota.
