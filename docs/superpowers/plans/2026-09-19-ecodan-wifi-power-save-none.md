# Ecodan Wi-Fi Power-Save None Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the existing Home Assistant Ecodan firmware-update experience while every future OTA firmware image uses no Wi-Fi power saving.

**Architecture:** The fork keeps the upstream generic OTA provisioning design, so the Ecodan retains its existing provisioned Wi-Fi credentials.  A two-file overlay changes the compiled OTA radio policy and makes the in-device update entity follow fork releases; no watchdog, secret, daemon, or Home Assistant automation is introduced.

**Tech Stack:** ESPHome YAML, upstream GitHub Actions release workflow, Home Assistant ESPHome integration.

## Global Constraints

- Modify only `confs/wifi-ota.yaml` and `confs/ota.yaml` for runtime behaviour.
- Preserve `reboot_timeout: 0s`; do not add a Wi-Fi or API watchdog.
- Do not add or commit Wi-Fi, API, or OTA credentials.
- Target only the live `esp32s3-proxy2-z2-en` firmware release for the initial migration.

---

### Task 1: Protect the OTA policy with a regression test

**Files:**
- Create: `tests/test_ota_wifi_policy.py`
- Test: `tests/test_ota_wifi_policy.py`

**Interfaces:**
- Consumes: `confs/wifi-ota.yaml`, `confs/ota.yaml`.
- Produces: an executable Python validation script with exit status 0 only when the permanent OTA policy is correct.

- [ ] **Step 1: Write the failing test**

```python
assert wifi["wifi"]["power_save_mode"] == "none"
assert wifi["wifi"]["reboot_timeout"] == "0s"
assert source == "https://github.com/cparmar/esphome-ecodan-hp/releases/latest/download/manifest.json"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `/usr/bin/python3 tests/test_ota_wifi_policy.py`

Expected: failure because the upstream-derived configuration is still `LIGHT` and its manifest points to the upstream repository.

- [ ] **Step 3: Do not change production YAML until the red failure is observed**

### Task 2: Apply the minimum persistent overlay

**Files:**
- Modify: `confs/wifi-ota.yaml:1-9`
- Modify: `confs/ota.yaml:27-30`
- Test: `tests/test_ota_wifi_policy.py`

**Interfaces:**
- Consumes: the existing upstream release workflow, which substitutes `wifi-ota.yaml` into OTA builds.
- Produces: a generic credential-free OTA image with `power_save_mode: none` and a Home Assistant update entity sourced from the fork.

- [ ] **Step 1: Change only the required values**

```yaml
# confs/wifi-ota.yaml
wifi:
  power_save_mode: none
  reboot_timeout: 0s

# confs/ota.yaml
source: https://github.com/cparmar/esphome-ecodan-hp/releases/latest/download/manifest.json
```

- [ ] **Step 2: Run the regression test to verify it passes**

Run: `/usr/bin/python3 tests/test_ota_wifi_policy.py`

Expected: exit status 0.

- [ ] **Step 3: Render the target release configuration**

Create a temporary release-build copy using the same three substitutions used
by `.github/workflows/build-release-binaries.yml`: select
`esp32s3-proxy2.yaml`, select the English labels, and replace
`confs/wifi.yaml` with `confs/wifi-ota.yaml`; append the generated
`confs/ota.yaml` fragment and validate that temporary `build.yaml` with dummy
credentials.

Expected: configuration validation succeeds with a temporary dummy `secrets.yaml`; the rendered Wi-Fi block reports `power_save_mode: NONE` and `reboot_timeout: 0s`.

- [ ] **Step 4: Commit**

```bash
git add confs/wifi-ota.yaml confs/ota.yaml tests/test_ota_wifi_policy.py
git commit -m "fix: disable Ecodan OTA Wi-Fi power saving"
```

### Task 3: Publish and verify the initial fork release

**Files:**
- No source-file changes.

**Interfaces:**
- Consumes: GitHub Actions release workflow and the committed fork branch.
- Produces: a release tag plus the `esp32s3-proxy2-z2-en-<tag>.ota.bin` asset and matching manifest.

- [ ] **Step 1: Push the branch to the fork**

```bash
git push cparmar feat/wifi-power-save-none
```

- [ ] **Step 2: Merge the branch into fork `main` and create release tag `2026-09-18.01-cdp.1`**

Use GitHub CLI only after the branch and local validation are verified.  The tag triggers the existing upstream release workflow.

- [ ] **Step 3: Verify publication before live install**

Confirm the release has the exact `esp32s3-proxy2-z2-en-2026-09-18.01-cdp.1.ota.bin` asset and manifest MD5 refers to that asset.

### Task 4: Install and validate the live migration

**Files:**
- No source-file changes.

**Interfaces:**
- Consumes: the forked target OTA file and the Ecodan web-server OTA endpoint at `192.168.20.9`.
- Produces: live firmware with the forked release version; later updates come from the fork manifest.

- [ ] **Step 1: Verify live preconditions**

Confirm the Ecodan HTTP endpoint and ESPHome API are reachable and its live firmware identifier remains `esp32s3-proxy2-z2-en-2026-09-18.01`.

- [ ] **Step 2: Upload the verified OTA image through ESPHome web-server OTA**

Use the explicit `esp32s3-proxy2-z2-en-2026-09-18.01-cdp.1.ota.bin` artifact.  Do not alter heat-pump entities or stored Wi-Fi credentials.

- [ ] **Step 3: Reverify after reboot**

Confirm Home Assistant receives normal Ecodan telemetry, reports the new firmware identifier, and the update entity now reads the forked manifest.
