"""Unit tests for the prompt evaluation framework."""

import pytest

from evaluator import (
    ComparisonReport,
    EvaluationResult,
    Prompt,
    PromptEvaluator,
    score_clarity,
    score_factual_accuracy,
    score_reasoning,
    score_structure,
)
from prompts import PROMPT_A, PROMPT_B, PROMPTS


# ---------------------------------------------------------------------------
# Individual scorer tests
# ---------------------------------------------------------------------------

class TestScoreClarity:
    def test_short_sentences_score_high(self):
        text = "This is short. So is this. Easy to read."
        assert score_clarity(text) >= 8.0

    def test_very_long_sentences_score_lower(self):
        long_sentence = " ".join(["word"] * 40) + "."
        short_sentence = "This is clear."
        assert score_clarity(long_sentence) < score_clarity(short_sentence)

    def test_readability_vocab_adds_bonus(self):
        with_vocab = "For example, think of it like a simple imagine clear just."
        without_vocab = "Technical distributed cryptographic immutable consensus."
        assert score_clarity(with_vocab) >= score_clarity(without_vocab)

    def test_score_bounded_0_to_10(self):
        for text in ["", "word", "x " * 100]:
            result = score_clarity(text)
            assert 0.0 <= result <= 10.0


class TestScoreReasoning:
    def test_connectors_increase_score(self):
        low = "Blockchain stores data."
        high = "Because blockchain stores data, it is immutable. Therefore it is secure."
        assert score_reasoning(high) > score_reasoning(low)

    def test_no_connectors_gives_zero(self):
        assert score_reasoning("Blockchain stores data in blocks.") == 0.0

    def test_score_bounded_0_to_10(self):
        text = " ".join(
            ["because", "therefore", "thus", "since", "hence", "consequently"] * 3
        )
        assert score_reasoning(text) <= 10.0


class TestScoreFactualAccuracy:
    def test_domain_terms_increase_score(self):
        low = "It is a technology that stores records."
        high = (
            "Blockchain is a distributed ledger that records transactions in "
            "blocks secured by cryptographic hash functions."
        )
        assert score_factual_accuracy(high) > score_factual_accuracy(low)

    def test_no_domain_terms_gives_zero(self):
        assert score_factual_accuracy("This is unrelated text.") == 0.0

    def test_score_bounded_0_to_10(self):
        rich = (
            "distributed ledger block chain decentralized cryptograph hash "
            "transaction immutable consensus node peer transparent secure bitcoin record"
        )
        assert score_factual_accuracy(rich) <= 10.0


class TestScoreStructure:
    def test_example_marker_increases_score(self):
        with_example = "For example, blockchain is like a shared notebook."
        without_example = "Blockchain is a distributed ledger."
        assert score_structure(with_example) > score_structure(without_example)

    def test_multi_sentence_bonus(self):
        single = "Blockchain is a ledger."
        multi = "Blockchain is a ledger. It stores data. It is secure."
        assert score_structure(multi) > score_structure(single)

    def test_score_bounded_0_to_10(self):
        text = (
            "For example, first, second, third, finally, such as, "
            "in summary, step, note. " * 5
        )
        assert score_structure(text) <= 10.0


# ---------------------------------------------------------------------------
# EvaluationResult tests
# ---------------------------------------------------------------------------

class TestEvaluationResult:
    def test_average_score(self):
        result = EvaluationResult(
            prompt_name="Test",
            scores={"clarity": 8.0, "reasoning": 6.0, "factual_accuracy": 4.0, "structure": 6.0},
        )
        assert result.average_score == pytest.approx(6.0)

    def test_average_score_empty(self):
        result = EvaluationResult(prompt_name="Empty", scores={})
        assert result.average_score == 0.0

    def test_str_contains_prompt_name(self):
        result = EvaluationResult(
            prompt_name="MyPrompt",
            scores={"clarity": 7.0},
        )
        assert "MyPrompt" in str(result)
        assert "clarity" in str(result)


# ---------------------------------------------------------------------------
# ComparisonReport tests
# ---------------------------------------------------------------------------

class TestComparisonReport:
    def test_winner_is_highest_average(self):
        r1 = EvaluationResult("A", {"clarity": 5.0, "reasoning": 5.0})
        r2 = EvaluationResult("B", {"clarity": 9.0, "reasoning": 9.0})
        report = ComparisonReport(results=[r1, r2])
        assert report.winner == "B"

    def test_single_result_is_winner(self):
        r = EvaluationResult("Solo", {"clarity": 7.0})
        report = ComparisonReport(results=[r])
        assert report.winner == "Solo"

    def test_str_contains_winner(self):
        r1 = EvaluationResult("A", {"clarity": 4.0})
        r2 = EvaluationResult("B", {"clarity": 8.0})
        report = ComparisonReport(results=[r1, r2])
        assert "Winner" in str(report)
        assert "B" in str(report)


# ---------------------------------------------------------------------------
# PromptEvaluator integration tests
# ---------------------------------------------------------------------------

class TestPromptEvaluator:
    def test_evaluate_returns_result_for_each_criterion(self):
        evaluator = PromptEvaluator()
        prompt = Prompt(
            name="Test",
            text="Explain something.",
            response="Blockchain is a distributed ledger. It stores records securely.",
        )
        result = evaluator.evaluate(prompt)
        assert set(result.scores.keys()) == {"clarity", "reasoning", "factual_accuracy", "structure"}

    def test_compare_returns_report_with_winner(self):
        evaluator = PromptEvaluator()
        report = evaluator.compare(PROMPTS)
        assert report.winner is not None
        assert report.winner in {p.name for p in PROMPTS}

    def test_custom_criteria_only_scores_specified(self):
        evaluator = PromptEvaluator(criteria={"clarity": score_clarity})
        prompt = Prompt("T", "text", "Simple and clear sentence.")
        result = evaluator.evaluate(prompt)
        assert list(result.scores.keys()) == ["clarity"]

    def test_all_scores_in_valid_range(self):
        evaluator = PromptEvaluator()
        for prompt in PROMPTS:
            result = evaluator.evaluate(prompt)
            for name, score in result.scores.items():
                assert 0.0 <= score <= 10.0, f"{name} out of range for {prompt.name}"


# ---------------------------------------------------------------------------
# Blockchain-specific consistency check
# ---------------------------------------------------------------------------

class TestBlockchainPromptConsistency:
    """Validate the specific findings stated in the problem statement."""

    def setup_method(self):
        self.evaluator = PromptEvaluator()
        self.report = self.evaluator.compare(PROMPTS)
        self.result_a = next(r for r in self.report.results if r.prompt_name == "Prompt A")
        self.result_b = next(r for r in self.report.results if r.prompt_name == "Prompt B")

    def test_prompt_b_wins_overall(self):
        """Prompt B should have a higher average score (problem statement conclusion)."""
        assert self.result_b.average_score > self.result_a.average_score

    def test_prompt_b_wins_clarity(self):
        """Problem statement: Prompt B produced clearer explanations."""
        assert self.result_b.scores["clarity"] >= self.result_a.scores["clarity"]

    def test_prompt_b_wins_structure(self):
        """Problem statement: Prompt B produced better structure."""
        assert self.result_b.scores["structure"] >= self.result_a.scores["structure"]

    def test_report_winner_is_prompt_b(self):
        assert self.report.winner == "Prompt B"

    def test_both_prompts_score_on_factual_accuracy(self):
        """Both responses are factually grounded; neither should score zero."""
        assert self.result_a.scores["factual_accuracy"] > 0.0
        assert self.result_b.scores["factual_accuracy"] > 0.0
