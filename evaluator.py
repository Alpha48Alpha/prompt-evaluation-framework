"""
Core evaluation logic for scoring AI responses across multiple criteria.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

# Keywords associated with each criterion.  A higher hit-rate contributes
# positively to the heuristic score.
_CLARITY_MARKERS: List[str] = [
    "example", "imagine", "simple", "easy", "think of", "like", "analogy",
    "basically", "in other words", "for instance", "such as",
]

_REASONING_MARKERS: List[str] = [
    "because", "therefore", "thus", "since", "as a result", "this means",
    "which means", "so that", "consequently", "due to", "in order to",
]

_FACTUAL_MARKERS: List[str] = [
    "blockchain", "block", "transaction", "hash", "cryptograph", "ledger",
    "decentrali", "consensus", "network", "immutable", "peer-to-peer",
    "timestamp", "proof of work", "proof of stake", "bitcoin",
]

_STRUCTURE_MARKERS: List[str] = [
    "first", "second", "third", "finally", "next", "then", "step", "lastly",
    "in conclusion", "to summarise", "to summarize", "for example",
    "importantly", "additionally", "furthermore",
]


def _sentence_count(text: str) -> int:
    """Return a rough sentence count."""
    return max(1, len(re.split(r"[.!?]+", text.strip())))


def _word_count(text: str) -> int:
    return len(text.split())


def _marker_ratio(text: str, markers: List[str]) -> float:
    """Return the fraction of markers present in the lowercased text."""
    lowered = text.lower()
    hits = sum(1 for m in markers if m in lowered)
    return hits / len(markers)


def _score_clarity(text: str) -> float:
    """
    Heuristic clarity score [0, 10].

    Higher scores when the response uses analogies / plain-language cues and
    maintains a moderate sentence-length (easier to follow).
    """
    marker_score = _marker_ratio(text, _CLARITY_MARKERS) * 6.0
    words = _word_count(text)
    sentences = _sentence_count(text)
    avg_words_per_sentence = words / sentences
    # Ideal range: 10-25 words per sentence
    if 10 <= avg_words_per_sentence <= 25:
        length_score = 4.0
    elif avg_words_per_sentence < 10:
        length_score = 2.0
    else:
        length_score = max(0.0, 4.0 - (avg_words_per_sentence - 25) * 0.15)
    return round(min(10.0, marker_score + length_score), 2)


def _score_reasoning(text: str) -> float:
    """
    Heuristic reasoning score [0, 10].

    Higher scores when the response contains causal / logical connectives.
    """
    return round(min(10.0, _marker_ratio(text, _REASONING_MARKERS) * 10.0), 2)


def _score_factual_accuracy(text: str) -> float:
    """
    Heuristic factual-accuracy score [0, 10].

    Checks presence of domain-specific terminology as a proxy for accuracy.
    """
    return round(min(10.0, _marker_ratio(text, _FACTUAL_MARKERS) * 10.0), 2)


def _score_structure(text: str) -> float:
    """
    Heuristic structure score [0, 10].

    Higher scores for use of transition words, examples, and having multiple
    distinct sentences.
    """
    marker_score = _marker_ratio(text, _STRUCTURE_MARKERS) * 6.0
    sentence_bonus = min(4.0, _sentence_count(text) * 0.5)
    return round(min(10.0, marker_score + sentence_bonus), 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    """Scores for a single prompt/response pair."""

    prompt: str
    response: str
    clarity: float = field(default=0.0)
    reasoning: float = field(default=0.0)
    factual_accuracy: float = field(default=0.0)
    structure: float = field(default=0.0)

    @property
    def overall(self) -> float:
        """Mean of all criterion scores."""
        return round(
            (self.clarity + self.reasoning + self.factual_accuracy + self.structure)
            / 4,
            2,
        )

    def as_dict(self) -> Dict[str, float]:
        return {
            "clarity": self.clarity,
            "reasoning": self.reasoning,
            "factual_accuracy": self.factual_accuracy,
            "structure": self.structure,
            "overall": self.overall,
        }


class PromptEvaluator:
    """Evaluate and compare AI responses to different prompt formulations."""

    def evaluate(self, prompt: str, response: str) -> EvaluationResult:
        """Score a single prompt/response pair across all criteria."""
        result = EvaluationResult(prompt=prompt, response=response)
        result.clarity = _score_clarity(response)
        result.reasoning = _score_reasoning(response)
        result.factual_accuracy = _score_factual_accuracy(response)
        result.structure = _score_structure(response)
        return result

    def compare(
        self, result_a: EvaluationResult, result_b: EvaluationResult
    ) -> str:
        """
        Return a human-readable comparison report for two evaluation results.
        """
        criteria = ["clarity", "reasoning", "factual_accuracy", "structure"]
        lines: List[str] = [
            "=" * 60,
            "PROMPT EVALUATION COMPARISON REPORT",
            "=" * 60,
            "",
            f"Prompt A: {result_a.prompt}",
            f"Prompt B: {result_b.prompt}",
            "",
            f"{'Criterion':<22} {'Prompt A':>10} {'Prompt B':>10} {'Winner':>10}",
            "-" * 55,
        ]

        for criterion in criteria:
            score_a = getattr(result_a, criterion)
            score_b = getattr(result_b, criterion)
            if score_a > score_b:
                winner = "A"
            elif score_b > score_a:
                winner = "B"
            else:
                winner = "Tie"
            lines.append(
                f"{criterion.replace('_', ' ').title():<22} {score_a:>10.2f}"
                f" {score_b:>10.2f} {winner:>10}"
            )

        lines += [
            "-" * 55,
            f"{'Overall':<22} {result_a.overall:>10.2f} {result_b.overall:>10.2f}",
            "",
        ]

        if result_a.overall > result_b.overall:
            lines.append("Conclusion: Prompt A produced the stronger overall response.")
        elif result_b.overall > result_a.overall:
            lines.append("Conclusion: Prompt B produced the stronger overall response.")
        else:
            lines.append("Conclusion: Both prompts produced equally strong responses.")

        lines.append("=" * 60)
        return "\n".join(lines)
