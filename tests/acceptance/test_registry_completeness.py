"""Every registry feature row must have status + phase + maturity."""

from __future__ import annotations

import re
import unittest

from acceptance._helpers import ALLOWED_MATURITY, ALLOWED_STATUS, REGISTRY


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
    def test_every_feature_has_status_phase_and_maturity(self) -> None:
        self.assertTrue(REGISTRY.is_file(), f"missing {REGISTRY}")
        rows = _parse_feature_rows(REGISTRY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 1, "registry has no feature rows")
        missing: list[str] = []
        bad_status: list[str] = []
        bad_maturity: list[str] = []
        for row in rows:
            fid = row.get("id", "<unknown>")
            status = row.get("status", "").strip()
            phase = row.get("phase", "").strip()
            maturity = row.get("maturity", "").strip()
            if not status or not phase or not maturity:
                missing.append(fid)
            if status and status not in ALLOWED_STATUS:
                bad_status.append(f"{fid}:{status}")
            if maturity and maturity not in ALLOWED_MATURITY:
                bad_maturity.append(f"{fid}:{maturity}")
        self.assertEqual(
            missing,
            [],
            f"features missing status, phase, and/or maturity: {missing}",
        )
        self.assertEqual(
            bad_status,
            [],
            f"features with invalid status: {bad_status}",
        )
        self.assertEqual(
            bad_maturity,
            [],
            f"features with invalid maturity: {bad_maturity}",
        )

    def test_iso_not_proven_and_session_substitutes_adapted(self) -> None:
        rows = {
            r["id"]: r
            for r in _parse_feature_rows(REGISTRY.read_text(encoding="utf-8"))
        }
        iso = rows["omarchy.install.iso"]
        self.assertEqual(iso["maturity"], "adapted")
        self.assertNotEqual(iso["maturity"], "proven")
        for fid in ("omarchy.session.hyprland", "omarchy.shell.quickshell"):
            self.assertEqual(rows[fid]["maturity"], "adapted")
            note = rows[fid].get("maturity_note", "")
            self.assertIn("D1", note)


if __name__ == "__main__":
    unittest.main()
