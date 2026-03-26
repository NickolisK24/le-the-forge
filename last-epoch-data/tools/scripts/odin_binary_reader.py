"""
odin_binary_reader.py
=====================
Pure-Python reader for Odin Serializer's Binary format (DataFormat=0).

Wire format notes (from Odin source BinaryDataWriter.cs):
  - Named entries write name via WriteStringFast, then payload.
  - Unnamed entries write payload directly.
  - WriteStringFast: [uint8 enc: 0=ASCII 1=UTF16] [int32 char_count] [chars]
    - char_count == -1 → null string
  - TypeName entry (0x2F): [int32 type_id] [WriteStringFast type_name]
    - Registers a type in the reader's type table under type_id.
  - TypeID entry (0x30): [int32 type_id]
    - References a previously registered type.
  - NamedStartOfReferenceNode (0x01): [name] [type] [int32 node_id]
  - NamedStartOfStructNode (0x03): [name] [type]
  - StartOfArray (0x06): [int64 element_count]
  - PrimitiveArray (0x08): [int32 count] [int32 bytes_per_element] [raw]
"""

import struct
from typing import Any, Optional


# Named entry types (must read a name string first)
NAMED_ENTRY_TYPES = {
    0x01, 0x03, 0x09, 0x0B, 0x0D, 0x0F, 0x11, 0x13, 0x15,
    0x17, 0x19, 0x1B, 0x1D, 0x1F, 0x21, 0x23, 0x25, 0x27,
    0x29, 0x2B, 0x2D, 0x32,
}

# Sentinel return keys from read_value
_END_NODE   = '__endnode__'
_END_ARRAY  = '__endarray__'
_END_STREAM = '__endstream__'


class OdinBinaryReader:
    """Reads an Odin Serializer binary blob into plain Python dicts/lists."""

    def __init__(self, data: bytes, external_refs: list = None):
        self._buf = data
        self._pos = 0
        self._type_registry: dict[int, str] = {}   # type_id → type_name
        self._ref_registry: dict[int, Any] = {}    # node_id → object
        self._external_refs: list = external_refs or []

    # ── Primitive readers ───────────────────────────────────────────────────────

    def _unpack(self, fmt: str) -> Any:
        val = struct.unpack_from(fmt, self._buf, self._pos)
        self._pos += struct.calcsize(fmt)
        return val[0]

    def _read_string(self) -> Optional[str]:
        """Read a WriteStringFast string: [enc:1][count:4][chars]."""
        enc   = self._buf[self._pos]; self._pos += 1
        count = self._unpack('<i')
        if count < 0:
            return None
        if count == 0:
            return ''
        if enc == 0:          # 8-bit ASCII / Latin-1
            s = self._buf[self._pos:self._pos + count].decode('latin-1', errors='replace')
            self._pos += count
        else:                 # 1 = UTF-16 LE
            s = self._buf[self._pos:self._pos + count * 2].decode('utf-16-le', errors='replace')
            self._pos += count * 2
        return s

    def _read_type(self) -> Optional[str]:
        """
        Consume a TypeName or TypeID entry and return the resolved type string.
        Advances _pos past the type entry.
        """
        if self._pos >= len(self._buf):
            return None
        et = self._buf[self._pos]; self._pos += 1
        if et == 0x2F:   # TypeName — new type; register it
            tid  = self._unpack('<i')
            name = self._read_string()
            self._type_registry[tid] = name
            return name
        elif et == 0x30: # TypeID — reference previously registered type
            tid = self._unpack('<i')
            return self._type_registry.get(tid, f'<type#{tid}>')
        else:
            self._pos -= 1   # not a type entry; push byte back
            return None

    # ── Node / array readers ────────────────────────────────────────────────────

    def _read_node(self, node_id: int) -> dict:
        """Read field entries until EndOfNode, return as dict."""
        obj: dict = {}
        if node_id >= 0:
            self._ref_registry[node_id] = obj  # register before recursing for cycles
        while True:
            key, val = self._read_entry()
            if key in (_END_NODE, _END_STREAM, None):
                break
            if key == _END_ARRAY:
                continue  # shouldn't appear here but be resilient
            obj[key] = val
        return obj

    def _read_array(self, length: int) -> list:
        """Read entries until EndOfArray (or length reached), return as list."""
        items: list = []
        while len(items) < length:
            key, val = self._read_entry()
            if key in (_END_ARRAY, _END_STREAM, None):
                return items
            if key == _END_NODE:
                break
            items.append(val)
        # consume EndOfArray if present
        if self._pos < len(self._buf) and self._buf[self._pos] == 0x07:
            self._pos += 1
        return items

    # ── Main entry reader ───────────────────────────────────────────────────────

    def _read_entry(self) -> tuple[Optional[str], Any]:
        """
        Read one binary entry.  Returns (field_name, value).
        Unnamed entries use None as the key.
        Sentinels __endnode__, __endarray__, __endstream__ signal structure boundaries.
        """
        if self._pos >= len(self._buf):
            return _END_STREAM, None

        et = self._buf[self._pos]; self._pos += 1

        # ── Sentinel entries ──
        if et == 0x31:  return _END_STREAM, None
        if et == 0x05:  return _END_NODE, None
        if et == 0x07:  return _END_ARRAY, None

        # ── Read name if this is a named variant ──
        name = self._read_string() if et in NAMED_ENTRY_TYPES else None

        # ── Dispatch ──
        if et in (0x01, 0x02):   # StartOfReferenceNode
            type_name = self._read_type()
            node_id   = self._unpack('<i')
            return name, self._read_node(node_id)

        if et in (0x03, 0x04):   # StartOfStructNode
            type_name = self._read_type()
            return name, self._read_node(-1)

        if et == 0x06:            # StartOfArray
            length = self._unpack('<q')
            return name, self._read_array(length)

        if et == 0x08:            # PrimitiveArray
            count = self._unpack('<i')
            bpe   = self._unpack('<i')
            raw   = self._buf[self._pos:self._pos + count * bpe]
            self._pos += count * bpe
            return name, list(raw)

        if et in (0x09, 0x0A):   # InternalReference
            ref_id = self._unpack('<i')
            return name, self._ref_registry.get(ref_id, {'$ref': ref_id})

        if et in (0x0B, 0x0C):   # ExternalReferenceByIndex
            idx = self._unpack('<i')
            return name, (self._external_refs[idx] if 0 <= idx < len(self._external_refs)
                          else {'$extRef': idx})

        if et in (0x0D, 0x0E):   # ExternalReferenceByGuid
            guid = self._buf[self._pos:self._pos + 16]; self._pos += 16
            return name, {'$extRefGuid': guid.hex()}

        if et in (0x32, 0x33):   # ExternalReferenceByString
            return name, {'$extRefStr': self._read_string()}

        if et in (0x0F, 0x10):   return name, self._unpack('<b')   # SByte
        if et in (0x11, 0x12):   return name, self._unpack('B')    # Byte
        if et in (0x13, 0x14):   return name, self._unpack('<h')   # Short
        if et in (0x15, 0x16):   return name, self._unpack('<H')   # UShort
        if et in (0x17, 0x18):   return name, self._unpack('<i')   # Int
        if et in (0x19, 0x1A):   return name, self._unpack('<I')   # UInt
        if et in (0x1B, 0x1C):   return name, self._unpack('<q')   # Long
        if et in (0x1D, 0x1E):   return name, self._unpack('<Q')   # ULong
        if et in (0x1F, 0x20):   return name, round(self._unpack('<f'), 7)  # Float
        if et in (0x21, 0x22):   return name, self._unpack('<d')   # Double
        if et in (0x25, 0x26):   return name, chr(self._unpack('<H'))       # Char
        if et in (0x27, 0x28):   return name, self._read_string()  # String
        if et in (0x29, 0x2A):   # Guid (16 bytes)
            g = self._buf[self._pos:self._pos + 16]; self._pos += 16
            return name, g.hex()
        if et in (0x2B, 0x2C):   # Boolean
            v = self._buf[self._pos]; self._pos += 1
            return name, bool(v)
        if et in (0x2D, 0x2E):   return name, None  # Null

        raise ValueError(f"Unknown Odin entry type 0x{et:02X} at offset {self._pos - 1}")

    # ── Public API ──────────────────────────────────────────────────────────────

    def read_all(self) -> dict:
        """Parse the entire binary stream and return a nested dict."""
        root: dict = {}
        unnamed_idx = 0
        while self._pos < len(self._buf):
            key, val = self._read_entry()
            if key in (_END_STREAM, None):
                break
            if key in (_END_NODE, _END_ARRAY):
                continue
            if key is None:
                root[str(unnamed_idx)] = val
                unnamed_idx += 1
            else:
                root[key] = val
        return root


# ── Convenience wrapper ─────────────────────────────────────────────────────────

def decode_odin_file(json_path: str) -> dict:
    """
    Load an AssetStudio-exported MonoBehaviour JSON that contains Odin
    serializationData, decode the binary blob, return the decoded object.
    """
    import json
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    sd = data.get('serializationData', {})
    raw_bytes = sd.get('SerializedBytes', [])
    if not raw_bytes:
        return {}

    ext_refs = sd.get('ReferencedUnityObjects', [])
    reader = OdinBinaryReader(bytes(raw_bytes), external_refs=ext_refs)
    return reader.read_all()


# ── CLI for quick inspection ────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys, json, pathlib

    if len(sys.argv) < 2:
        print("Usage: python odin_binary_reader.py <MonoBehaviour.json> [max_depth]")
        sys.exit(1)

    path = sys.argv[1]
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    def truncate(obj, depth=0):
        if depth > max_depth:
            if isinstance(obj, dict): return f'{{...{len(obj)} keys}}'
            if isinstance(obj, list): return f'[...{len(obj)} items]'
        if isinstance(obj, dict):
            return {k: truncate(v, depth+1) for k, v in list(obj.items())[:30]}
        if isinstance(obj, list):
            if len(obj) > 20 and all(isinstance(x, int) for x in obj):
                return f'[bytes: {len(obj)} elements]'
            return [truncate(v, depth+1) for v in obj[:20]]
        return obj

    try:
        result = decode_odin_file(path)
        print(json.dumps(truncate(result), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback; traceback.print_exc()
        sys.exit(1)
