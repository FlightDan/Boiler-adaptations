# Boiler device-source conventions

`common/` owns actual cross-model hardware resources. `brands/<vendor>/common/`
owns vendor-shared material, while models contain only their configuration and
TOON references. `devices/` is registry, compatibility, and discovery metadata;
it is not a second implementation root. Source-only records do not activate a
runtime, establish device acceptance, or authorize a package hook.

Model TOON references must use a common resource rather than copying its
payload. Model parameters such as board audio routes and mount matrices remain
model-owned. The current ownership migration is limited to Intel xe VMA, Intel
BE201 firmware, Realtek ALC245 speaker routing, Bosch BMI260 gyro, and the
already-agreed Acer GM7 policy. Do not move CPU, battery, HDR, lights, or input
material as part of that change.

GM7 matching is by the actual reviewed SSD identity, never handheld DMI. A
selected compatible package provider has priority; otherwise the existing
generic fallback applies. A matching repair is default-checked, an unknown or
nonmatching device is not selected, and an explicit user opt-out remains sticky
for the same reviewed target. This policy remains a fileless provider; common
device sources must not include an arbitrary boot handler.

Keep historical source locks immutable. Record current imports, raw source
hashes, licenses, transforms, and acceptance limits in a new versioned
migration record. The fixed public CPU baseline is
`72f864e0498c10366493c74608c5ffed62cc99ca`; do not import experimental CPU
research. Private research, device captures, credentials, keys, local helpers,
and `.local/` are never public source inputs. Update `source-files.txt` for
every new public source file.
