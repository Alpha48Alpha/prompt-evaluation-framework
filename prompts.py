"""
Prompt definitions and sample responses for blockchain explanation evaluation.
"""

PROMPT_A = "Explain blockchain."

PROMPT_B = "Explain blockchain to a beginner using a simple example."

RESPONSE_A = (
    "A blockchain is a distributed ledger technology that records transactions across "
    "a network of computers. Each block contains a cryptographic hash of the previous "
    "block, a timestamp, and transaction data. This chaining of blocks makes the records "
    "tamper-resistant and immutable. Consensus mechanisms such as Proof of Work or Proof "
    "of Stake are used to validate new blocks before they are appended to the chain. "
    "Because no single entity controls the ledger, the system is decentralised and "
    "transparent, enabling trustless peer-to-peer transactions."
)

RESPONSE_B = (
    "Think of a blockchain as a shared notebook — a decentralised ledger — that many "
    "people keep a copy of. Whenever someone writes a new entry, everyone's copy is "
    "updated at the same time, because the network of computers reaches a consensus "
    "before accepting the change. "
    "Once an entry is written, it is immutable: it cannot be erased or changed without "
    "everyone noticing, because each block contains a cryptographic hash of the "
    "previous block — like links in a chain. "
    "For example, imagine Alice sends Bob 1 Bitcoin. That transaction is broadcast to "
    "the peer-to-peer network. The computers group it with other recent transactions "
    "into a block, verify via a consensus mechanism such as Proof of Work that Alice "
    "actually has the funds, and then add the block to the chain. "
    "From that moment on, the record stored in the ledger is permanent and visible to "
    "everyone. This makes blockchain useful for cryptocurrency and beyond, because you "
    "get a trustworthy, tamper-resistant record without needing a bank in the middle."
)
