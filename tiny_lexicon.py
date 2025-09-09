"""
A tiny handcrafted polarity lexicon to demonstrate dictionary use (Lec 3)
without external libraries. Real projects can expand this safely.
"""
LEXICON = {
    # positives
    "good": 1.5, "great": 2.0, "excellent": 2.5, "clean": 0.8, "pleasant": 0.9,
    "welcoming": 1.2, "attentive": 1.3, "efficient": 1.0, "fantastic": 2.2,
    "glad": 0.7, "hospitable": 1.4, "friendly": 1.2, "helpful": 1.1,
    "quick": 0.7, "professional": 1.1, "bedside": 0.4, "manner": 0.3,

    # negatives
    "bad": -1.5, "worst": -2.5, "dirty": -1.5, "rude": -2.0, "slow": -0.9,
    "unpleasant": -1.2, "unwelcoming": -1.3, "inefficient": -1.1,
    "painful": -1.0, "confusing": -0.8, "expensive": -0.7, "wait": -0.4,
    "waiting": -0.4, "crowded": -0.7, "skeptical": -0.3,

    # domain hints
    "doctor": 0.4, "nurse": 0.3, "front": 0.0, "desk": 0.0, "clinic": 0.2,
    "care": 0.3, "urgent": 0.0, "health": 0.2, "area": 0.0, "rooms": 0.0,
}
