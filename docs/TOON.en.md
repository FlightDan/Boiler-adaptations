# TOON: how models refer to hardware resources

[Home](README.en.md) · [中文](TOON.md) · [Build guide](BUILD.en.md)

TOON is a text format for structured data. Here it describes models, components, resource paths, and dependencies. Build tools read those records and pass the files to the relevant build scripts.

## What each file does

| Location | Purpose |
| --- | --- |
| `brands/<brand>/<model>/common-device-sources.toon` | Declares the shared device resources a model uses |
| `common/<type>/<vendor>/<model>/source.toon` | Describes a shared resource's files, provenance, licenses, and conditions; use the actual resource path |
| [Resource-model TOON files in Boiler Installer](https://github.com/FlightDan/Boiler-installer/tree/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/brands/onexplayer/models) | List resource IDs and model parameters for the shared resource pool |
| [Model-guide TOON files in Boiler Installer](https://github.com/FlightDan/Boiler-installer/tree/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/brands/onexplayer) | Describe components, build inputs, and the matching model-package build adapter |

The repositories have different jobs: **Boiler-devices holds adaptation records and the device registry; Boiler Installer provides the model-package and installer build tools.** Each has its own sources and inventories. After changing this repository, follow the build project's source locks and preparation steps to carry the change across; the other repository does not update automatically.

## Example: a model TOON

This is [OXP3's shared-resource reference](../brands/onexplayer/oxp3/common-device-sources.toon):

```text
schema_version: 1
kind: BoilerModelCommonReferences
model_id: "device:oxp3"
source_only: true
resources[4]{id,source}:
  "resource:intel-xevmafix-724",common/gpu/intel/xe/xevmafix-724/source.toon
  "resource:intel-be201-firmware",common/network/intel/be201/source.toon
  "resource:oxp3-speaker-route",common/audio/realtek/alc245/speaker-route/source.toon
  "resource:bmi260-gyro",common/sensors/bosch/bmi260/gyro/source.toon
boot_policies[1]{id,version,source,component_ref}:
  "ssd:gm7-boot-repair",1,common/ssd/acer/gm7/components.toon,ssd-gm7-boot-repair
```

`model_id` identifies the model. `resources[4]{id,source}` contains four resource rows, each with an ID and a definition path relative to the repository root. `boot_policies[1]` lists one separate boot policy. When adding or removing rows, update the count in brackets too.

## Two models using BMI260

[OXP3](../brands/onexplayer/oxp3/common-device-sources.toon) and [X2 Mini](../brands/onexplayer/x2-mini/common-device-sources.toon) each have a model TOON. Both contain this reference:

```text
"resource:bmi260-gyro",common/sensors/bosch/bmi260/gyro/source.toon
```

In the [BMI260 source.toon](../common/sensors/bosch/bmi260/gyro/source.toon), `files[11]{path,size,sha256,origin,license,availability}` describes 11 files: paths are relative to the resource directory, followed by size, hash, origin, license, and availability. It also records hardware matching, compatibility, and recovery information. Model parameters remain with the model; the shared resource does not need a copy in every model directory.

A model TOON can also reference a boot policy through `boot_policies`. Both models, for example, refer to the [GM7 components.toon](../common/ssd/acer/gm7/components.toon). This policy is listed separately from the source entries in `resources`.

## Change or reuse an adaptation

1. Start with the model's TOON and follow its `source` path to the resource definition and code.
2. Put reusable hardware implementations in `common/` and reference them from each model. Keep brand-shared and model-specific content under the relevant brand.
3. When adding a model or resource, maintain its provenance, licenses, inventory, and checks. New models currently need an entry in `MODELS` in `scripts/common-device-sources.py`; new shared resources also need corresponding resource declarations and migration records. The checker currently validates the existing models against a fixed resource set; adjust its checks when using a different set.
4. From the Boiler-devices repository root, run:

```sh
python -B scripts/adaptations.py check
python -B scripts/common-device-sources.py check
```

`common-device-sources.py write` generates the shared-resource index. Review the changes and run `check` afterwards. The current shared TOON gyro checks cover BMI260; other sensors need their own resource definitions and validation.

TOON does not execute programs. Building an installable device package also requires a matching build adapter and its inputs in Boiler Installer. See the [build guide](BUILD.en.md).
