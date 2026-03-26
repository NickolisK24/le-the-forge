import UnityPy
from pathlib import Path
from tqdm import tqdm

DATA_PATH = Path(
'/Volumes/Last Epoch/Last Epoch_Data'
)

OUTPUT_PATH = Path("extracted_tables")
OUTPUT_PATH.mkdir(exist_ok=True)

asset_files = []

# Collect assets
resources_file = DATA_PATH / "resources.assets"
if resources_file.exists():
    asset_files.append(resources_file)

for i in range(0, 30):
    f = DATA_PATH / f"sharedassets{i}.assets"
    if f.exists():
        asset_files.append(f)

print(f"Scanning {len(asset_files)} asset files...\n")

count = 0

KEYWORDS = [
    "string",
    "localization",
    "table",
    "text",
    "language",
    "english",
]

for asset_file in asset_files:

    print(f"Loading: {asset_file.name}")

    env = UnityPy.load(str(asset_file))

    objects = list(env.objects)

    for obj in tqdm(objects):

        try:

            if obj.type.name in [
                "MonoBehaviour",
                "ScriptableObject"
            ]:

                data = obj.read()

                name = ""

                if hasattr(data, "m_Name"):
                    name = data.m_Name.lower()

                if any(k in name for k in KEYWORDS):

                    out_file = OUTPUT_PATH / f"{count}_{name}.json"

                    with open(out_file, "w", encoding="utf-8") as f:
                        f.write(str(data))

                    print(f"Extracted table: {name}")

                    count += 1

        except Exception:
            continue

print(f"\nTotal tables extracted: {count}")