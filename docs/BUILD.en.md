# Build a device package and installer

[Home](README.en.md) · [中文](BUILD.md) · [TOON guide](TOON.en.md)

To work on a model, start with its adaptation files and TOON, then use the Boiler Installer build tools to make a device package. To change the installer interface or packaging, continue with the application build and packaging scripts in Boiler Installer.

The commands below describe Boiler Installer public commit `c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989`. For another version, use that version's build instructions and input locks.

## Where to start

| Goal | Entry point |
| --- | --- |
| Inspect a model or reuse hardware source | [Model directories](../brands/onexplayer/) and [common](../common/) |
| Understand model-to-resource references | [TOON guide](TOON.en.md) |
| Build an existing device package | [Boiler Installer TOON build guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md) |
| Build the Windows installer | [Boiler Installer build instructions](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/README.md#build-from-an-independent-checkout) |

`scripts/build-index.py` in Boiler-devices takes an **already built device package** and prepares an index candidate. It does not build the package itself.

## Example: build the X2 Mini package

Run these PowerShell commands from the **Boiler Installer** repository root. First prepare three directories from the [build guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md): an extracted complete OXP3 `.8` package, an identity bridge overlay, and an HDR overlay. The X2 input names are `base`, `bridge_overlay`, and `hdr_overlay`. Replace the three paths below with your actual directories; choose an output directory that does not already exist.

```powershell
$Base = "PATH_TO_COMPLETE_OXP3_PACKAGE"
$Bridge = "PATH_TO_BRIDGE_OVERLAY"
$Hdr = "PATH_TO_HDR_OVERLAY"
$Output = "PATH_TO_NEW_X2_OUTPUT"

python -B adaptations/scripts/toon_catalog.py check
python -B adaptations/scripts/toon_catalog.py preflight --model guide:x2-mini --input "base=$Base" --input "bridge_overlay=$Bridge" --input "hdr_overlay=$Hdr"
python -B adaptations/scripts/toon_catalog.py build --model guide:x2-mini --input "base=$Base" --input "bridge_overlay=$Bridge" --input "hdr_overlay=$Hdr" --output "$Output"
```

`check` checks the catalog and generated views; `preflight` checks the supplied inputs and locks; `build` invokes the model's build adapter and produces an unsigned device package. Resolve any missing inputs reported by `preflight` before running `build`.

The [X2 package guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/X2_COMPLETE_PACKAGE.md) and [bridge overlay guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/X2_COMPLETE_REUSE.md) explain the OXP3 base, overlays, fixed inputs, and preparation commands. To rebuild the OXP3 package used as the X2 base, the OXP3 pipeline also requires its `.2` base and locked third-party archives.

The current X2 builder reuses the complete OXP3 base and applies both overlays. To produce a trimmed package containing only selected components, provide build logic for that selection and check its dependencies and final inventory.

## Trim or reuse an adaptation

1. In Boiler-devices, select the model files, shared resources, and licenses you need. Follow their origins and references using the [TOON guide](TOON.en.md).
2. Adjust model data and component selections in your fork. TOON describes what is needed; a fixed adapter in Boiler Installer performs the build.
3. When reusing an existing builder, prepare the inputs specified by its locks. For a different model or a new way to trim the package, implement and check an appropriate adapter against the project's package contract.
4. Run resource checks, package validation, and the tests needed for installation, maintenance, and recovery. Record the devices, systems, and features you tested.

Boiler Installer's `scripts/prepare-resource-pool.py` prepares a shared resource pool and its catalog. The model builder handles a separate device package; check the inputs and outputs of each.

For example, Boiler-devices contains the shared BMI260 sources and model references, but Boiler Installer's current resource-pool model lists do not include that resource. To use it through the resource-pool path, add the corresponding resource declaration and handling in the build project, then check the result.

Copying a TOON file alone does not create a new executable builder. The [TOON build guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md) lists the adapters and inputs.

### Code to start from

- [TOON parsing, checks, and adapter entry point](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/scripts/toon_catalog.py)
- [X2 device-package builder](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/scripts/build-x2-complete.py)
- [DevicePackage format](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/schemas/DevicePackage.schema.json) and [package validator](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/protocol/manifest.py)

If you already have a device-package directory in that format, run this from the Boiler Installer repository to produce an unsigned ZIP. Replace both paths with your own:

```powershell
$Package = "PATH_TO_PACKAGE_DIRECTORY"
$Zip = "PATH_TO_NEW_PACKAGE.zip"
python -B scripts/build-device-package.py "$Package" --output "$Zip"
```

## Build the installer

The model package and the Windows installer are separate artifacts. To build the installer, prepare its locked dependencies in an independent Windows x64 checkout of Boiler Installer, build the application, prepare the selected integration content, and run the packaging script. See the [Boiler Installer README](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/README.md#build-from-an-independent-checkout) and [dependency preparation guide](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/docs/DEPENDENCY_BOOTSTRAP.md); use `--help` for each preparation script's arguments.

Check the resulting package manifest, resource files, and hashes, then test installation, maintenance, and recovery in an appropriate environment. For public distribution, follow the project's device-index workflow.
