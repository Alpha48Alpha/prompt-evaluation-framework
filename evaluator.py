"""Core prompt evaluation framework.

Scores AI responses against four criteria:
  - clarity
  - reasoning
  - factual_accuracy
  - structure
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Prompt:
    """Represents a single prompt together with its AI response."""

    name: str
    text: str
    response: str


@dataclass
class EvaluationResult:
    """Holds per-criterion scores and derived statistics for one prompt."""

    prompt_name: str
    scores: Dict[str, float]

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def __str__(self) -> str:
        lines = [f"Prompt: {self.prompt_name}"]
        for criterion, score in self.scores.items():
            lines.append(f"  {criterion:<20} {score:.2f} / 10")
        lines.append(f"  {'average':<20} {self.average_score:.2f} / 10")
        return "\n".join(lines)


@dataclass
class ComparisonReport:
    """Side-by-side comparison of two or more evaluation results."""

    results: List[EvaluationResult]
    winner: Optional[str] = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.results:
            best = max(self.results, key=lambda r: r.average_score)
            self.winner = best.prompt_name

    def __str__(self) -> str:
        lines = ["=" * 60, "PROMPT EVALUATION REPORT", "=" * 60, ""]
        for result in self.results:
            lines.append(str(result))
            lines.append("")
        lines += [
            "-" * 60,
            f"Winner: {self.winner}",
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

_READABILITY_WORDS = {
    "simple", "example", "imagine", "like", "easy", "means", "basically",
    "think", "picture", "just", "clear", "understand", "shows",
}

_REASONING_CONNECTORS = {
    "because", "therefore", "thus", "so", "which means", "as a result",
    "consequently", "since", "this is why", "that is why", "hence",
    "this allows", "this ensures", "in order to",
}

_BLOCKCHAIN_FACTS = {
    "ledger", "distributed", "block", "chain", "decentralized",
    "cryptograph", "hash", "transaction", "immutable", "consensus",
    "node", "peer", "transparent", "secure", "bitcoin", "record",
}

# Scoring calibration constants
_MAX_REASONING_CONNECTORS = 5   # connectors needed to reach a full reasoning score
_REASONING_SCORE_PER_MATCH = 10.0 / _MAX_REASONING_CONNECTORS

_MAX_FACTUAL_TERMS = 6          # domain terms needed to reach a full factual-accuracy score

_STRUCTURE_MARKERS = {
    "for example", "such as", "first", "second", "third", "finally",
    "in summary", "to summarize", "in conclusion", "step", "note",
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def _sentence_count(text: str) -> int:
    sentences = re.split(r"[.!?]+", text.strip())
    return max(1, sum(1 for s in sentences if s.strip()))


def _word_count(text: str) -> int:
    return len(_tokenize(text))


# ---------------------------------------------------------------------------
# Individual criterion scorers (each returns 0–10)
# ---------------------------------------------------------------------------

def score_clarity(response: str) -> float:
    """Higher score for shorter average sentence length and beginner-friendly words."""
    wc = _word_count(response)
    sc = _sentence_count(response)
    avg_sentence_len = wc / sc

    # Sentence length score: ideal range ~10-15 words per sentence
    if avg_sentence_len <= 15:
        length_score = 10.0
    elif avg_sentence_len <= 20:
        length_score = 8.0
    elif avg_sentence_len <= 25:
        length_score = 6.0
    elif avg_sentence_len <= 30:
        length_score = 4.0
    else:
        length_score = 2.0

    # Bonus for readability vocabulary
    tokens = set(_tokenize(response))
    vocab_bonus = min(2.0, len(tokens & _READABILITY_WORDS) * 0.5)

    return min(10.0, length_score + vocab_bonus)


def score_reasoning(response: str) -> float:
    """Higher score for more logical-connector phrases."""
    lower = response.lower()
    matches = sum(1 for phrase in _REASONING_CONNECTORS if phrase in lower)
    return min(10.0, matches * _REASONING_SCORE_PER_MATCH)


def score_factual_accuracy(response: str) -> float:
    """Higher score for more blockchain domain terms present."""
    lower = response.lower()
    matches = sum(1 for term in _BLOCKCHAIN_FACTS if term in lower)
    return min(10.0, matches * (10.0 / _MAX_FACTUAL_TERMS))


def score_structure(response: str) -> float:
    """Higher score for presence of structural cues (examples, ordered steps, etc.)."""
    lower = response.lower()
    marker_score = min(6.0, sum(1 for m in _STRUCTURE_MARKERS if m in lower) * 1.5)

    # Bonus for having an explicit example (response contains "example" + colon/comma nearby)
    has_example = bool(re.search(r"\bexample\b", lower))
    example_bonus = 2.0 if has_example else 0.0

    # Bonus for multi-sentence responses (>= 3 sentences implies some structure)
    sentence_bonus = 2.0 if _sentence_count(response) >= 3 else 0.0

    return min(10.0, marker_score + example_bonus + sentence_bonus)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

CRITERIA = {
    "clarity": score_clarity,
    "reasoning": score_reasoning,
    "factual_accuracy": score_factual_accuracy,
    "structure": score_structure,
}


class PromptEvaluator:
    """Evaluates one or more prompts and produces a comparison report."""

    def __init__(self, criteria: Optional[Dict] = None) -> None:
        self.criteria = criteria if criteria is not None else CRITERIA

    def evaluate(self, prompt: Prompt) -> EvaluationResult:
        """Score a single prompt's response against all active criteria."""
        scores = {
            name: scorer(prompt.response)
            for name, scorer in self.criteria.items()
        }
        return EvaluationResult(prompt_name=prompt.name, scores=scores)

    def compare(self, prompts: List[Prompt]) -> ComparisonReport:
        """Evaluate all prompts and return a comparison report."""
        results = [self.evaluate(p) for p in prompts]
        return ComparisonReport(results=results)
