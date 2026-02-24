import hashlib
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "safety_rules.json"

def compute_hash(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

if __name__ == "__main__":
    rule_hash = compute_hash(CONFIG_PATH)
    print("\nSAFETY RULES SHA256 HASH:")
    print(rule_hash)
