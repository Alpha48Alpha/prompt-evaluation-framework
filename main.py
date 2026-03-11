"""
Entry point: run the prompt evaluation and print the comparison report.
"""

from evaluator import PromptEvaluator
from prompts import PROMPT_A, PROMPT_B, RESPONSE_A, RESPONSE_B


def main() -> None:
    evaluator = PromptEvaluator()

    result_a = evaluator.evaluate(PROMPT_A, RESPONSE_A)
    result_b = evaluator.evaluate(PROMPT_B, RESPONSE_B)

    report = evaluator.compare(result_a, result_b)
    print(report)


if __name__ == "__main__":
    main()
