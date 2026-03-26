import UnityPy
from pathlib import Path
from tqdm import tqdm

DATA_PATH = Path(
'/Volumes/Last Epoch/Last Epoch_Data'
)

OUTPUT_PATH = Path("extracted_localization")
OUTPUT_PATH.mkdir(exist_ok=True)

# Collect asset files
asset_files = []

# Always include resources.assets
resources_file = DATA_PATH / "resources.assets"
if resources_file.exists():
    asset_files.append(resources_file)

# Add sharedassets automatically
for i in range(0, 20):
    f = DATA_PATH / f"sharedassets{i}.assets"
    if f.exists():
        asset_files.append(f)

print(f"Found {len(asset_files)} asset files to scan.")

count = 0

for asset_file in asset_files:

    print(f"\nLoading: {asset_file.name}")

    env = UnityPy.load(str(asset_file))

    objects = list(env.objects)

    for obj in tqdm(objects):

        try:

            if obj.type.name == "TextAsset":

                data = obj.read()

                name = data.m_Name.lower()

                if any(k in name for k in [
                "global",
                "names",
                "string",
                "localization",
                "lang",
                "english",
                "en"
            ]):

                    out_path = OUTPUT_PATH / f"{data.m_Name}.bytes"

                content = data.m_Script

                if isinstance(content, str):
                    content = content.encode("utf-8")

                with open(out_path, "wb") as f:
                    f.write(content)

                print(f"Extracted: {data.m_Name}")

                count += 1

        except Exception:
            continue

print(f"\nTotal extracted: {count}")