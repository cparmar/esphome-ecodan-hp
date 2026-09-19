#!/usr/bin/env python3
"""Regression contract for the fork-owned Ecodan OTA connectivity policy."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WIFI_OTA = ROOT / "confs" / "wifi-ota.yaml"
OTA = ROOT / "confs" / "ota.yaml"
FORK_MANIFEST = (
    "https://github.com/cparmar/esphome-ecodan-hp/releases/latest/download/manifest.json"
)


def test_ota_build_disables_wifi_power_saving_without_a_watchdog() -> None:
    text = WIFI_OTA.read_text(encoding="utf-8")

    assert re.search(r"^\s*power_save_mode:\s*none\s*$", text, re.MULTILINE)
    assert re.search(r"^\s*reboot_timeout:\s*0s\s*$", text, re.MULTILINE)


def test_firmware_update_entity_follows_fork_releases() -> None:
    text = OTA.read_text(encoding="utf-8")

    assert f"source: {FORK_MANIFEST}" in text


if __name__ == "__main__":
    test_ota_build_disables_wifi_power_saving_without_a_watchdog()
    test_firmware_update_entity_follows_fork_releases()
