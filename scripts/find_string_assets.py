from pathlib import Path

SEARCH_PATH = Path("extracted_localization")

KEYWORDS = [
    "damage",
    "mana",
    "health",
    "fire",
    "cold",
    "lightning",
    "critical",
    "chance",
    "passive",
    "skill",
    "attack",
]

print("Scanning for likely localization files...\n")

matches = []

for file in SEARCH_PATH.glob("*.bytes"):

    try:
        text = file.read_bytes()

        decoded = text.decode("utf-8", errors="ignore").lower()

        hit_count = sum(
            1 for k in KEYWORDS
            if k in decoded
        )

        if hit_count >= 3:

            matches.append((file.name, hit_count))

    except Exception:
        continue


matches.sort(key=lambda x: x[1], reverse=True)

print("Likely localization candidates:\n")

for name, score in matches[:20]:
    print(f"{name}  (score={score})")