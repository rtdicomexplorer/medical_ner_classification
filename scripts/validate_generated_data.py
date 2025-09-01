# validator that checks for tag alignment or detects inconsistent entity spans in your generated data
#let it run before training
from config import ID2LABEL
import json
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils import validate_ner_sample_smart


def run_validation(json_path, max_errors=5, show_tokens=False):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"🔍 Validating {len(data)} samples from {json_path}...\n")

    total_errors = 0
    for idx, sample in enumerate(data):
        tokens = sample["tokens"]
        ner_tags = sample["ner_tags"]
        issues = validate_ner_sample_smart(tokens, ner_tags)

        if issues:
            total_errors += 1
            print(f"\n❌ Sample #{idx} has issues:")
            print("⚠️  Problems:", issues)

            if show_tokens:
                for i, (t, tag_id) in enumerate(zip(tokens, ner_tags)):
                    print(f"{i:>2}: {t:15} → {ID2LABEL.get(tag_id, '?')}")

            if total_errors >= max_errors:
                print(f"\n⚠️ Stopping early after {max_errors} problematic samples.")
                break

    if total_errors == 0:
        print("✅ No label alignment issues found!")
    else:
        print(f"\n🚨 Found {total_errors} samples with alignment problems.")


if __name__ == "__main__":
    run_validation("./data/all_data.json")
