#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLAG_NAMES = [
    ("flag1", "recon", 10),
    ("flag2", "backup", 10),
    ("flag3", "sqli", 15),
    ("flag4", "idor", 15),
    ("flag5", "lfi", 20),
    ("flag6", "diag", 30),
]
FLAG_RE = re.compile(r"FLAG\{aegisnet_[a-z0-9_]+_[0-9a-f]{24}\}")


def load_env_seed() -> str:
    env_seed = os.environ.get("FLAG_SEED")
    if env_seed:
        return env_seed

    env_paths = [ROOT / ".env", Path("/etc/aegisnet/aegisnet.env")]
    for env_path in env_paths:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            if key == "FLAG_SEED":
                return value.strip().strip('"').strip("'")
    raise SystemExit("Missing FLAG_SEED. Run scripts/init-env.sh, scripts/kali-install.sh, or set FLAG_SEED.")


def derive_flag(seed: str, name: str) -> str:
    digest = hmac.new(seed.encode("utf-8"), name.encode("utf-8"), hashlib.sha256).hexdigest()[:24]
    return f"FLAG{{aegisnet_{name}_{digest}}}"


def extract_flags(text: str) -> set[str]:
    return set(FLAG_RE.findall(text))


def main() -> None:
    parser = argparse.ArgumentParser(description="Score an AegisNet flag submission.")
    parser.add_argument("--from-file", required=True, help="Submission file containing recovered flags.")
    parser.add_argument(
        "--show-missing",
        action="store_true",
        help="Show missing flag names without revealing flag values.",
    )
    args = parser.parse_args()

    submission_path = Path(args.from_file)
    if not submission_path.exists():
        raise SystemExit(f"Submission file not found: {submission_path}")

    seed = load_env_seed()
    expected = {
        label: {
            "value": derive_flag(seed, name),
            "points": points,
        }
        for label, name, points in FLAG_NAMES
    }
    submitted = extract_flags(submission_path.read_text(encoding="utf-8", errors="replace"))

    total = sum(item["points"] for item in expected.values())
    score = 0
    found_labels = []
    missing_labels = []

    for label, item in expected.items():
        if item["value"] in submitted:
            score += item["points"]
            found_labels.append(label)
        else:
            missing_labels.append(label)

    print(f"Score: {score}/{total}")
    print(f"Found: {len(found_labels)}/{len(expected)}")
    if found_labels:
        print("Accepted:", ", ".join(found_labels))
    if args.show_missing and missing_labels:
        print("Missing:", ", ".join(missing_labels))


if __name__ == "__main__":
    main()
