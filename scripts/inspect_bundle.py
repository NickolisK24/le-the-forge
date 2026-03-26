import UnityPy
from pathlib import Path

# Pick ONE bundle to inspect
BUNDLE_PATH = Path(
    "/Volumes/Last Epoch/Last Epoch_Data/StreamingAssets/aa/StandaloneWindows64"
)

bundle_files = list(BUNDLE_PATH.glob("*.bundle"))

print(f"Found {len(bundle_files)} bundles")

if not bundle_files:
    exit()

test_bundle = bundle_files[0]

print(f"\nTesting bundle:")
print(test_bundle.name)

try:
    env = UnityPy.load(test_bundle)

    print("\nObjects found inside bundle:")

    types = set()

    for obj in env.objects:
        types.add(obj.type.name)

    if types:
        for t in sorted(types):
            print("-", t)
    else:
        print("No readable objects found.")

except Exception as e:
    print("\nFailed to read bundle:")
    print(e)