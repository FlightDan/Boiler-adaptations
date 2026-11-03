# 构建机型包和安装器

[首页](../README.md) · [English](BUILD.en.md) · [TOON 指南](TOON.md)

要改一台机型，先从它的适配资料和 TOON 入手，再用 Boiler Installer 的构建工具生成机型包。想修改安装器界面或打包方式，则继续使用 Boiler Installer 的应用构建与打包脚本。

下面的命令按 Boiler Installer 公开提交 `c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989` 编写；使用其他版本时，以对应版本的构建说明和输入锁为准。

## 从哪里开始

| 我想做什么 | 入口 |
| --- | --- |
| 看机型适配、复用一份硬件源码 | [机型目录](../brands/onexplayer/) 和 [common](../common/) |
| 理解机型与共用资源如何连接 | [TOON 指南](TOON.md) |
| 构建已有机型包 | [Boiler Installer 的 TOON 构建说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md) |
| 构建 Windows 安装器 | [Boiler Installer 构建说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/README.md#build-from-an-independent-checkout) |

Boiler-devices 中的 `scripts/build-index.py` 接受**已经构建好的机型包**并生成索引候选；它不是机型包构建器。

## 例子：构建 X2 Mini 机型包

下面的命令在 **Boiler Installer** 仓库根目录运行，使用 PowerShell。先按[构建说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md)准备三个目录：已展开的完整 OXP3 `.8` 机型包目录，以及身份桥接和 HDR 的 overlay 目录。它们分别对应 `base`、`bridge_overlay` 和 `hdr_overlay`；把下面三个路径替换成你准备好的实际目录。输出目录应是一个尚不存在的新目录。

```powershell
$Base = "PATH_TO_COMPLETE_OXP3_PACKAGE"
$Bridge = "PATH_TO_BRIDGE_OVERLAY"
$Hdr = "PATH_TO_HDR_OVERLAY"
$Output = "PATH_TO_NEW_X2_OUTPUT"

python -B adaptations/scripts/toon_catalog.py check
python -B adaptations/scripts/toon_catalog.py preflight --model guide:x2-mini --input "base=$Base" --input "bridge_overlay=$Bridge" --input "hdr_overlay=$Hdr"
python -B adaptations/scripts/toon_catalog.py build --model guide:x2-mini --input "base=$Base" --input "bridge_overlay=$Bridge" --input "hdr_overlay=$Hdr" --output "$Output"
```

`check` 检查目录与生成视图；`preflight` 核对指定的输入和锁；`build` 调用机型对应的构建适配器，生成未签名的机型包。运行 `build` 前先处理 `preflight` 报出的缺失项。

完整 OXP3 基础包及两个 overlay 的来源、准备命令和固定输入见 [X2 构建说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/X2_COMPLETE_PACKAGE.md) 与 [桥接 overlay 说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/X2_COMPLETE_REUSE.md)。若要重建 X2 所需的 OXP3 基础包，OXP3 流程还需要 `.2` 基础包和锁定的第三方归档；按文档准备这些输入。

现有 X2 构建器复用完整的 OXP3 基础包，再应用两个 overlay。若要生成只含指定组件的裁剪包，需要为该裁剪方式提供对应构建逻辑，并核对依赖和最终清单。

## 裁剪或复制适配

1. 在 Boiler-devices 中选出要复用的机型文件、共用资源和许可证，按 [TOON 指南](TOON.md)追踪它们的来源和引用。
2. 在自己的 fork 中调整机型资料与组件选择。TOON 描述“需要什么”；实际构建由 Boiler Installer 的固定适配器处理。
3. 复用现有构建器时，按其输入锁准备文件；为不同机型或新的裁剪方式构建时，按项目的包协议实现并检查对应适配器。
4. 运行资源检查、机型包验证，以及安装、维护和恢复所需的测试。记录你实际测试过的设备、系统和功能。

共享资源池使用 Boiler Installer 的 `scripts/prepare-resource-pool.py` 准备；它生成的是资源池和目录。机型构建器处理的是另一份机型包，两者的输入和输出各自核对。

例如，Boiler-devices 已有 BMI260 的共用源码和机型引用；Boiler Installer 当前的资源池机型清单尚未列入该资源。要让它走资源池路径，需要在构建项目中补齐对应资源声明和处理流程，再检查生成结果。

新机型不能只复制一个 TOON 就获得新的可执行构建逻辑；[TOON 构建说明](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/docs/TOON_MODEL_CATALOG.md)列出了当前适配器与输入。

### 可以从哪里复制代码

- [TOON 解析、检查和适配器入口](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/scripts/toon_catalog.py)
- [X2 机型包构建器](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/scripts/build-x2-complete.py)
- [DevicePackage 格式](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/schemas/DevicePackage.schema.json)和[包检查代码](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/protocol/manifest.py)

已有符合格式的机型包目录时，可以在 Boiler Installer 仓库中用下面的命令生成未签名 ZIP。把两个路径换成实际位置：

```powershell
$Package = "PATH_TO_PACKAGE_DIRECTORY"
$Zip = "PATH_TO_NEW_PACKAGE.zip"
python -B scripts/build-device-package.py "$Package" --output "$Zip"
```

## 生成安装器

机型包和 Windows 安装器是不同产物。构建安装器时，在 Boiler Installer 的 Windows x64 独立检出中准备锁定依赖，构建应用，再按选项准备集成内容并运行打包脚本。入口与所需环境见 [Boiler Installer README](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/README.md#build-from-an-independent-checkout) 和 [依赖准备文档](https://github.com/FlightDan/Boiler-installer/blob/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/docs/DEPENDENCY_BOOTSTRAP.md)；各准备脚本可用 `--help` 查看参数。

生成后检查机型包的 manifest、资源文件和哈希，并在适当的测试环境中验证安装、维护与恢复。公开分发时再按项目的设备索引流程处理。
