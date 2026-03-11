"""
Unit tests for the PromptEvaluator and scoring helpers.
"""

import sys
import os

# Ensure the project root is on sys.path so imports work without installation.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from evaluator import (
    EvaluationResult,
    PromptEvaluator,
    _score_clarity,
    _score_reasoning,
    _score_factual_accuracy,
    _score_structure,
)
from prompts import PROMPT_A, PROMPT_B, RESPONSE_A, RESPONSE_B


# ---------------------------------------------------------------------------
# Individual scoring function tests
# ---------------------------------------------------------------------------

class TestScoreClarity:
    def test_returns_value_between_0_and_10(self):
        score = _score_clarity(RESPONSE_B)
        assert 0.0 <= score <= 10.0

    def test_beginner_response_scores_higher_than_technical(self):
        # Response B uses analogies and plain language — should score higher.
        assert _score_clarity(RESPONSE_B) >= _score_clarity(RESPONSE_A)

    def test_empty_string_does_not_raise(self):
        score = _score_clarity("")
        assert 0.0 <= score <= 10.0

    def test_analogy_text_boosts_clarity(self):
        analogy = "Think of it like a simple example. Imagine you have a notebook."
        plain = "It is a distributed system with cryptographic hashing mechanisms."
        assert _score_clarity(analogy) > _score_clarity(plain)


class TestScoreReasoning:
    def test_returns_value_between_0_and_10(self):
        score = _score_reasoning(RESPONSE_A)
        assert 0.0 <= score <= 10.0

    def test_causal_language_boosts_reasoning(self):
        causal = "Because the hash links blocks, therefore tampering is detectable."
        plain = "Blocks are linked. Tampering is detectable."
        assert _score_reasoning(causal) > _score_reasoning(plain)

    def test_no_reasoning_markers_returns_zero(self):
        assert _score_reasoning("Blockchain stores data.") == 0.0


class TestScoreFactualAccuracy:
    def test_returns_value_between_0_and_10(self):
        score = _score_factual_accuracy(RESPONSE_A)
        assert 0.0 <= score <= 10.0

    def test_domain_terms_boost_score(self):
        rich = (
            "A blockchain is a decentralised ledger where each block contains "
            "a transaction and a cryptographic hash of the previous block."
        )
        sparse = "It stores information in a chain."
        assert _score_factual_accuracy(rich) > _score_factual_accuracy(sparse)

    def test_response_a_has_reasonable_factual_score(self):
        # Response A is technically dense — should score well.
        assert _score_factual_accuracy(RESPONSE_A) >= 3.0


class TestScoreStructure:
    def test_returns_value_between_0_and_10(self):
        score = _score_structure(RESPONSE_B)
        assert 0.0 <= score <= 10.0

    def test_transition_words_boost_structure(self):
        structured = "First, data is gathered. Then, it is validated. Finally, it is stored."
        unstructured = "Data is gathered validated stored."
        assert _score_structure(structured) > _score_structure(unstructured)

    def test_more_sentences_increases_structure_bonus(self):
        multi = "Step one. Step two. Step three. Step four. Step five."
        single = "Everything happens at once."
        assert _score_structure(multi) > _score_structure(single)


# ---------------------------------------------------------------------------
# EvaluationResult tests
# ---------------------------------------------------------------------------

class TestEvaluationResult:
    def test_overall_is_mean_of_criteria(self):
        result = EvaluationResult(
            prompt="p", response="r",
            clarity=8.0, reasoning=6.0, factual_accuracy=7.0, structure=5.0,
        )
        assert result.overall == pytest.approx((8.0 + 6.0 + 7.0 + 5.0) / 4, abs=0.01)

    def test_as_dict_contains_all_keys(self):
        result = EvaluationResult(prompt="p", response="r")
        d = result.as_dict()
        for key in ("clarity", "reasoning", "factual_accuracy", "structure", "overall"):
            assert key in d

    def test_scores_default_to_zero(self):
        result = EvaluationResult(prompt="p", response="r")
        assert result.clarity == 0.0
        assert result.reasoning == 0.0
        assert result.factual_accuracy == 0.0
        assert result.structure == 0.0


# ---------------------------------------------------------------------------
# PromptEvaluator tests
# ---------------------------------------------------------------------------

class TestPromptEvaluator:
    def setup_method(self):
        self.evaluator = PromptEvaluator()

    def test_evaluate_returns_evaluation_result(self):
        result = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        assert isinstance(result, EvaluationResult)

    def test_evaluate_stores_prompt_and_response(self):
        result = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        assert result.prompt == PROMPT_A
        assert result.response == RESPONSE_A

    def test_evaluate_all_scores_in_range(self):
        for prompt, response in [(PROMPT_A, RESPONSE_A), (PROMPT_B, RESPONSE_B)]:
            result = self.evaluator.evaluate(prompt, response)
            for score in result.as_dict().values():
                assert 0.0 <= score <= 10.0, f"Score out of range: {score}"

    def test_prompt_b_overall_not_worse_than_prompt_a(self):
        """Prompt B (beginner-friendly) should match or beat Prompt A overall."""
        result_a = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        result_b = self.evaluator.evaluate(PROMPT_B, RESPONSE_B)
        assert result_b.overall >= result_a.overall

    def test_compare_returns_string(self):
        result_a = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        result_b = self.evaluator.evaluate(PROMPT_B, RESPONSE_B)
        report = self.evaluator.compare(result_a, result_b)
        assert isinstance(report, str)

    def test_compare_report_contains_prompts(self):
        result_a = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        result_b = self.evaluator.evaluate(PROMPT_B, RESPONSE_B)
        report = self.evaluator.compare(result_a, result_b)
        assert PROMPT_A in report
        assert PROMPT_B in report

    def test_compare_report_contains_criteria(self):
        result_a = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        result_b = self.evaluator.evaluate(PROMPT_B, RESPONSE_B)
        report = self.evaluator.compare(result_a, result_b)
        for criterion in ("Clarity", "Reasoning", "Factual Accuracy", "Structure"):
            assert criterion in report

    def test_compare_report_contains_conclusion(self):
        result_a = self.evaluator.evaluate(PROMPT_A, RESPONSE_A)
        result_b = self.evaluator.evaluate(PROMPT_B, RESPONSE_B)
        report = self.evaluator.compare(result_a, result_b)
        assert "Conclusion:" in report

    def test_compare_winner_a_when_a_better(self):
        """When A scores higher, report should declare A the winner."""
        result_a = EvaluationResult(
            prompt="A", response="r",
            clarity=9.0, reasoning=9.0, factual_accuracy=9.0, structure=9.0,
        )
        result_b = EvaluationResult(
            prompt="B", response="r",
            clarity=5.0, reasoning=5.0, factual_accuracy=5.0, structure=5.0,
        )
        report = self.evaluator.compare(result_a, result_b)
        assert "Prompt A produced the stronger overall response." in report

    def test_compare_winner_b_when_b_better(self):
        """When B scores higher, report should declare B the winner."""
        result_a = EvaluationResult(
            prompt="A", response="r",
            clarity=3.0, reasoning=3.0, factual_accuracy=3.0, structure=3.0,
        )
        result_b = EvaluationResult(
            prompt="B", response="r",
            clarity=8.0, reasoning=8.0, factual_accuracy=8.0, structure=8.0,
        )
        report = self.evaluator.compare(result_a, result_b)
        assert "Prompt B produced the stronger overall response." in report

    def test_compare_tie_when_equal(self):
        result_a = EvaluationResult(
            prompt="A", response="r",
            clarity=5.0, reasoning=5.0, factual_accuracy=5.0, structure=5.0,
        )
        result_b = EvaluationResult(
            prompt="B", response="r",
            clarity=5.0, reasoning=5.0, factual_accuracy=5.0, structure=5.0,
        )
        report = self.evaluator.compare(result_a, result_b)
        assert "equally strong" in report
