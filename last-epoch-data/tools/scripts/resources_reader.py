"""
resources_reader.py
====================
Shared binary parser utilities for reading Unity-serialized data from
resources.assets. Handles the serialization format used by Last Epoch's
IL2CPP build where TypeTrees are stripped.

All primitives are padded to 4-byte boundaries (Unity's serialization rule).
Pointer-type fields (object references) are serialized as 12-byte PPtrs:
  fileID (int32) + pathID (int64).
Arrays are: count (uint32) + elements.
Lists<T> are serialized the same as arrays (not as C# List, but as count + elements).
"""

import struct


class BinaryReader:
    """Cursor-based binary reader with Unity alignment semantics."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def align4(self):
        self.pos = (self.pos + 3) & ~3

    def read_i8(self) -> int:
        v = struct.unpack_from("<b", self.data, self.pos)[0]
        self.pos += 1
        return v

    def read_u8(self) -> int:
        v = self.data[self.pos]
        self.pos += 1
        return v

    def read_u8_aligned(self) -> int:
        v = self.read_u8()
        self.align4()
        return v

    def read_bool(self) -> bool:
        v = bool(self.data[self.pos])
        self.pos += 1
        self.align4()
        return v

    def read_i16(self) -> int:
        v = struct.unpack_from("<h", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_u16(self) -> int:
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_u16_aligned(self) -> int:
        v = self.read_u16()
        self.align4()
        return v

    def read_i32(self) -> int:
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_i64(self) -> int:
        v = struct.unpack_from("<q", self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_f32(self) -> float:
        v = struct.unpack_from("<f", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_f32r(self, decimals: int = 4) -> float:
        return round(self.read_f32(), decimals)

    def read_string(self) -> str:
        """Read Unity-serialized string: u32 length + chars + align4."""
        self.align4()
        n = self.read_u32()
        if n > 1_000_000:
            raise ValueError(f"String length {n} at pos {self.pos} is unreasonably large")
        s = self.data[self.pos:self.pos + n].decode("utf-8", errors="replace")
        self.pos += n
        self.align4()
        return s

    def read_pptr(self) -> tuple[int, int]:
        """Read a PPtr: (fileID: i32, pathID: i64). 12 bytes total."""
        file_id = self.read_i32()
        path_id = self.read_i64()
        return file_id, path_id

    def read_vector2int(self) -> tuple[int, int]:
        """Read UnityEngine.Vector2Int: (x: i32, y: i32)."""
        x = self.read_i32()
        y = self.read_i32()
        return x, y

    def read_i32_array(self) -> list[int]:
        """Read a Unity array of int32: count + elements."""
        count = self.read_u32()
        vals = list(struct.unpack_from(f"<{count}i", self.data, self.pos))
        self.pos += count * 4
        return vals

    def read_count(self) -> int:
        """Read array/list count (uint32)."""
        return self.read_u32()

    def skip(self, n: int):
        self.pos += n

    def remaining(self) -> int:
        return len(self.data) - self.pos

    @property
    def at_end(self) -> bool:
        return self.pos >= len(self.data)


def monobehaviour_data_start(raw: bytes) -> tuple[str, int]:
    """
    Parse MonoBehaviour header and return (m_Name, data_start_offset).

    MonoBehaviour binary layout (Unity IL2CPP, stripped TypeTree):
      m_GameObject: PPtr (12 bytes: fileID i32 + pathID i64)
      m_Enabled:    uint8 (1 byte) + 3 pad
      m_Script:     PPtr (12 bytes)
      m_Name:       string (4-byte length + chars + align4)
      <data fields follow>
    """
    r = BinaryReader(raw)
    r.read_pptr()          # m_GameObject
    r.read_u8_aligned()    # m_Enabled
    r.read_pptr()          # m_Script
    name = r.read_string() # m_Name
    return name, r.pos
