# Ecodan OTA Wi-Fi Power-Save Design

## Goal

Keep Home Assistant's existing Ecodan firmware-update flow while making every
future OTA release use `power_save_mode: NONE`.

## Evidence

The live Ecodan identifies itself as
`esp32s3-proxy2-z2-en-2026-09-18.01`.  That upstream release's workflow
replaces `confs/wifi.yaml` with `confs/wifi-ota.yaml` when building OTA
artifacts.  The released `wifi-ota.yaml` sets `power_save_mode: LIGHT` and
does not embed station credentials.  ESPHome preserves the device's
provisioned credentials across OTA updates.

## Design

The `cparmar/esphome-ecodan-hp` fork remains otherwise aligned with upstream.
It makes only two behavioural changes:

1. `confs/wifi-ota.yaml` sets `power_save_mode: NONE`.  The existing
   `reboot_timeout: 0s` remains unchanged: no Wi-Fi or API watchdog is added.
2. `confs/ota.yaml` points the existing `Firmware Update` entity at the fork's
   `releases/latest` manifest.  Therefore, after one manual migration OTA,
   subsequent updates in Home Assistant continue from the fork and retain the
   Wi-Fi policy.  The manifest's OTA, factory-image and release URLs are also
   fork-owned, so an update never silently switches back to upstream artifacts.

The initial fork image will be installed through the already enabled
ESPHome web-server OTA path.  This creates a brief telemetry interruption but
does not change heat-pump settings or provisioned Wi-Fi credentials.

The fork's release workflow accepts both a published release and an explicit
manual dispatch with the existing release tag.  The latter is a deterministic
fallback when GitHub does not emit a release workflow run for a CLI-published
release; both paths build and upload to the same tag.

## Constraints

- No Wi-Fi password, API key, or OTA password is stored in the fork.
- No watchdog, additional daemon, Home Assistant automation, or local update
  server is introduced.
- The release target is the live board/language/zone combination:
  `esp32s3-proxy2-z2-en`.
- Upstream updates remain deliberate: sync/rebase then release the forked
  version after the standard build validation passes.

## Validation

1. A regression test verifies the OTA Wi-Fi policy and fork manifest URL.
2. ESPHome validates the rendered generic OTA configuration.
3. The fork's release workflow produces the matching OTA artifact and manifest.
4. Before the live installation, verify the target artifact's board, zone and
   language in its filename and checksum in the manifest.
5. After installation, verify Home Assistant reports the forked version,
   ESPHome API connectivity, and the next update source.
