"""Every registry feature row must have status + phase (forbidden to skip)."""

from __future__ import annotations

import re
import unittest

from acceptance._helpers import ALLOWED_STATUS, REGISTRY


def _parse_feature_rows(text: str) -> list[dict[str, str]]:
    """Minimal YAML list parser for features/registry.yaml (no PyYAML dep)."""
    features: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_features = False
    for raw in text.splitlines():
        if raw.startswith("features:"):
            in_features = True
            continue
        if not in_features:
            continue
        if re.match(r"^[A-Za-z_]", raw):
            break
        m_id = re.match(r"^  - id:\s*(.+)$", raw)
        if m_id:
            if current is not None:
                features.append(current)
            current = {"id": m_id.group(1).strip().strip("\"'")}
            continue
        if current is None:
            continue
        m_kv = re.match(r"^    ([A-Za-z0-9_]+):\s*(.*)$", raw)
        if m_kv:
            key, val = m_kv.group(1), m_kv.group(2).strip().strip("\"'")
            current[key] = val
    if current is not None:
        features.append(current)
    return features


class RegistryCompletenessTests(unittest.TestCase):
    def test_every_feature_has_status_and_phase(self) -> None:
        self.assertTrue(REGISTRY.is_file(), f"missing {REGISTRY}")
        rows = _parse_feature_rows(REGISTRY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 1, "registry has no feature rows")
        missing: list[str] = []
        bad_status: list[str] = []
        for row in rows:
            fid = row.get("id", "<unknown>")
            status = row.get("status", "").strip()
            phase = row.get("phase", "").strip()
            if not status or not phase:
                missing.append(fid)
            elif status not in ALLOWED_STATUS:
                bad_status.append(f"{fid}:{status}")
        self.assertEqual(
            missing,
            [],
            f"features missing status and/or phase: {missing}",
        )
        self.assertEqual(
            bad_status,
            [],
            f"features with invalid status: {bad_status}",
        )


if __name__ == "__main__":
    unittest.main()
