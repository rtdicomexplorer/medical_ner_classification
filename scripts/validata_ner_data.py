# validator that checks for tag alignment or detects inconsistent entity spans in your generated data
#let it run before training
from config import ID2LABEL
import json

def validate_ner_sample(tokens, ner_tags):
    problems = []

    if len(tokens) != len(ner_tags):
        problems.append(f"Length mismatch: {len(tokens)} tokens vs {len(ner_tags)} tags")

    # Check for BIO format consistency
    for i, tag_id in enumerate(ner_tags):
        tag = ID2LABEL.get(tag_id, "O")

        if tag.startswith("I-"):
            if i == 0 or ID2LABEL.get(ner_tags[i - 1], "O")[2:] != tag[2:]:
                problems.append(f"Inconsistent I- tag at position {i}: {tag} without preceding B-")

        if tag_id < 0 or tag_id >= len(ID2LABEL):
            problems.append(f"Invalid label ID at position {i}: {tag_id}")

    return problems


def run_validation(json_path, max_errors=5):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"🔍 Validating {len(data)} samples from {json_path}...\n")

    total_errors = 0
    for idx, sample in enumerate(data):
        tokens = sample["tokens"]
        ner_tags = sample["ner_tags"]
        issues = validate_ner_sample(tokens, ner_tags)

        if issues:
            total_errors += 1
            print(f"\n❌ Sample #{idx} has issues:")
            for i, (t, tag_id) in enumerate(zip(tokens, ner_tags)):
                print(f"{i:>2}: {t:15} → {ID2LABEL.get(tag_id, '?')}")
            print("⚠️  Problems:", issues)

            if total_errors >= max_errors:
                print(f"\n⚠️ Stopping early after {max_errors} problematic samples.")
                break

    if total_errors == 0:
        print("✅ No label alignment issues found!")
    else:
        print(f"\n🚨 Found {total_errors} samples with alignment problems.")


if __name__ == "__main__":
    run_validation("./data/test.json")
