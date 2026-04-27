from config import DEMO_MODE
from evaluator import run_evaluation, save_results


def main() -> None:
    if DEMO_MODE:
        print("Running in DEMO_MODE: using fallback demo responses instead of live OpenAI calls.")
    rows = run_evaluation()
    save_results(rows)


if __name__ == "__main__":
    main()
