import UnityPy

CATALOG_PATH = "/Volumes/Last Epoch/Last Epoch_Data/StreamingAssets/aa/catalog.bin"

print("Loading catalog...")

try:
    env = UnityPy.load(CATALOG_PATH)

    print("\nObjects found in catalog:")

    types = set()

    for obj in env.objects:
        types.add(obj.type.name)

    if types:
        for t in sorted(types):
            print("-", t)
    else:
        print("No readable objects found.")

except Exception as e:
    print("\nFailed to load catalog:")
    print(e)