"""Entry point: run the blockchain prompt evaluation and print the report."""

from evaluator import PromptEvaluator
from prompts import PROMPTS


def main() -> None:
    evaluator = PromptEvaluator()
    report = evaluator.compare(PROMPTS)
    print(report)


if __name__ == "__main__":
    main()
