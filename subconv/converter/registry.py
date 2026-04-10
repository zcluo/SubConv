"""Name registry for proxy name deduplication."""

from __future__ import annotations


class NameRegistry:
    """Tracks proxy names per subscription to ensure uniqueness.

    When a duplicate name is encountered, appends a zero-padded suffix
    (e.g., "HK-01", "HK-02").
    """

    def __init__(self) -> None:
        self._names: dict[str, int] = {}

    def register(self, name: str) -> str:
        """Register a proxy name and return a unique version.

        First occurrence returns the name unchanged.
        Subsequent occurrences return "{name}-{index:02d}".
        """
        index = self._names.get(name)
        if index is None:
            self._names[name] = 0
            return name
        index += 1
        self._names[name] = index
        return f"{name}-{index:02d}"
