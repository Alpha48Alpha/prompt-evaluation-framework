"""Blockchain prompt definitions and sample AI responses used in the evaluation."""

from evaluator import Prompt

# ---------------------------------------------------------------------------
# Prompt A — plain, no audience guidance
# ---------------------------------------------------------------------------

PROMPT_A = Prompt(
    name="Prompt A",
    text="Explain blockchain.",
    response=(
        "Blockchain is a distributed ledger technology that maintains a continuously "
        "growing list of records called blocks, which are linked and secured using "
        "cryptography. Each block contains a cryptographic hash of the previous block, "
        "a timestamp, and transaction data. The distributed nature of the ledger means "
        "that no single entity controls the data. Because each block references the "
        "previous one via its hash, altering any record would require recalculating all "
        "subsequent hashes, which makes the chain immutable. Consensus mechanisms such "
        "as proof-of-work or proof-of-stake are used to validate new blocks across "
        "peer nodes in the network."
    ),
)

# ---------------------------------------------------------------------------
# Prompt B — audience-aware, requests a simple example
# ---------------------------------------------------------------------------

PROMPT_B = Prompt(
    name="Prompt B",
    text="Explain blockchain to a beginner using a simple example.",
    response=(
        "Imagine a shared notebook. "
        "Many friends each keep their own copy. "
        "Every time someone sends money, everyone writes it down. "
        "No single person controls the notebook. "
        "Because everyone has the same copy, no one can secretly change a past entry. "
        "This is why blockchain is considered secure and transparent. "
        "Each 'block' is like one page in that shared notebook. "
        "The 'chain' links all the pages together in order. "
        "For example, when you send Bitcoin to a friend, that transaction becomes "
        "a new block added to the chain. "
        "Every node in the network can verify it. "
        "This means no bank or central authority is needed. "
        "The distributed ledger keeps track of who owns what, automatically."
    ),
)

PROMPTS = [PROMPT_A, PROMPT_B]
