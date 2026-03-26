import UnityPy
from pathlib import Path
from tqdm import tqdm

# UPDATE THIS PATH IF NEEDED
BUNDLE_ROOT = Path(
    "/Volumes/Last Epoch/Last Epoch_Data/StreamingAssets/aa/StandaloneWindows64"
)

OUTPUT_DIR = Path("extracted_assets")
OUTPUT_DIR.mkdir(exist_ok=True)

bundle_files = list(BUNDLE_ROOT.glob("*.bundle"))

print(f"Found {len(bundle_files)} bundle files to scan.")

total_extracted = 0

for bundle in tqdm(bundle_files, desc="Scanning bundles"):
    try:
        env = UnityPy.load(bundle)

        for obj in env.objects:

            try:
                # --- TEXT ASSETS ---
                if obj.type.name == "TextAsset":
                    data = obj.read()

                    name = data.m_Name or f"textasset_{total_extracted}"

                    output_file = OUTPUT_DIR / f"{name}.txt"

                    with open(output_file, "w", encoding="utf-8") as f:
                        if isinstance(data.m_Script, bytes):
                            f.write(
                                data.m_Script.decode(
                                    "utf-8",
                                    errors="ignore"
                                )
                            )
                        else:
                            f.write(str(data.m_Script))

                    total_extracted += 1

                # --- MONOBEHAVIOUR ---
                elif obj.type.name == "MonoBehaviour":

                    data = obj.read()

                    # Try converting to dict
                    tree = data.read_typetree()

                    name = tree.get(
                        "m_Name",
                        f"monobehaviour_{total_extracted}"
                    )

                    output_file = OUTPUT_DIR / f"{name}.json"

                    with open(output_file, "w", encoding="utf-8") as f:
                        import json
                        json.dump(
                            tree,
                            f,
                            indent=2
                        )

                    total_extracted += 1

            except Exception:
                continue

    except Exception:
        continue

print(f"\nTotal assets extracted: {total_extracted}")