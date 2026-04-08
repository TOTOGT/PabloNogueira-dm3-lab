import yaml
from pathlib import Path

def load_bridge(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def check_entropy_chain(pillar):
    cid = pillar["id"]
    entropy = pillar.get("entropy", {})
    M = entropy.get("M")
    E = entropy.get("E")
    if pillar["claim_level"] == "formally_verified":
        assert M is not None, f"{cid}: missing M entropy operator"
        assert E is not None, f"{cid}: missing E entropy operator"
        thms = {t["id"] for t in entropy.get("theorems", [])}
        required = {"M_toy_iff_E_toy", "E_toy_iff_sphere"} if cid == "poincare_toy_model" else set()
        missing = required - thms
        assert not missing, f"{cid}: missing entropy theorems {missing}"

def check_operator_decomposition(pillar):
    cid = pillar["id"]
    ops = pillar.get("operators", {})
    composite = ops.get("composite", {})
    if composite:
        assert composite.get("decomposition_verified") in (True, False)
        if pillar["claim_level"] == "formally_verified":
            assert composite["decomposition_verified"], f"{cid}: operator decomposition not verified"

def check_sorry_count(pillar):
    cid = pillar["id"]
    lean = pillar.get("lean", {})
    if pillar["claim_level"] == "formally_verified":
        assert lean.get("sorry_count", 1) == 0, f"{cid}: nonzero sorry_count for verified pillar"

def validate_bridge(path: str):
    pillars = load_bridge(path)
    for p in pillars:
        check_entropy_chain(p)
        check_operator_decomposition(p)
        check_sorry_count(p)
    print("bridge v9.1: all checks passed")

if __name__ == "__main__":
    validate_bridge("coherence_bridge_v9_1.yaml")
