# TOON：机型如何引用硬件资源

[首页](../README.md) · [English](TOON.en.md) · [构建指南](BUILD.md)

TOON 是本项目用来写结构化资料的文本格式。这里的 TOON 用来描述机型、组件、资源路径和依赖；构建工具读取这些资料，再由对应的构建脚本处理文件。

## 这些文件各管一件事

| 位置 | 作用 |
| --- | --- |
| `brands/<品牌>/<机型>/common-device-sources.toon` | 声明这个机型引用哪些共用设备资源 |
| `common/<设备类型>/<厂商>/<型号>/source.toon` | 描述一份共用资源的文件、来源、许可证和适用条件；具体路径以资源目录为准 |
| [Boiler Installer 的资源机型 TOON](https://github.com/FlightDan/Boiler-installer/tree/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/brands/onexplayer/models) | 列出机型申请的资源 ID 和机型参数，供共享资源池使用 |
| [Boiler Installer 的机型指南 TOON](https://github.com/FlightDan/Boiler-installer/tree/c1c70ea7d1234b59372bb5c595ec2fd0fe5b1989/adaptations/brands/onexplayer) | 描述组件、构建输入及对应的机型包构建适配器 |

两个仓库承担不同的工作：**Boiler-devices 保存适配资料和设备注册信息；Boiler Installer 提供机型包与安装器的构建工具。** 两边各有自己的源码和清单；修改本仓库后，需要按构建项目的来源锁和准备流程同步，另一个仓库不会自动更新。

## 例子：一个机型的 TOON

这是 [OXP3 的共用资源引用](../brands/onexplayer/oxp3/common-device-sources.toon)：

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

`model_id` 是机型身份；`resources[4]{id,source}` 表示有四行资源，每行按顺序填写资源 ID 和相对于仓库根目录的定义路径。`boot_policies[1]` 单独列出一条启动策略。增删行时，方括号里的数量也要对应修改。

## 两个机型引用 BMI260

[OXP3](../brands/onexplayer/oxp3/common-device-sources.toon) 和 [X2 Mini](../brands/onexplayer/x2-mini/common-device-sources.toon) 分别有自己的机型 TOON，两边都引用：

```text
"resource:bmi260-gyro",common/sensors/bosch/bmi260/gyro/source.toon
```

[BMI260 的 source.toon](../common/sensors/bosch/bmi260/gyro/source.toon) 中，`files[11]{path,size,sha256,origin,license,availability}` 描述 11 个文件：路径相对于该资源目录，后面依次是大小、哈希、来源、许可证和文件可用状态；此外还有硬件匹配、兼容和恢复信息。机型参数仍归机型管理；相同资源不需要复制到每个机型目录。

机型 TOON 还可以通过 `boot_policies` 引用启动策略。例如，两台机型都引用 [GM7 的 components.toon](../common/ssd/acer/gm7/components.toon)；这个条目是策略定义，与 `resources` 中的源码资源分别列出。

## 修改或复用

1. 先查看目标机型的 TOON，再沿 `source` 路径找到资源定义和源码。
2. 相同硬件需要共用实现时，在 `common/` 维护一份资源，由各机型引用；品牌共用和机型专属内容分别放回对应品牌目录。
3. 调整机型参数或增加资源时，同时维护来源、许可证、文件清单和相关检查。新机型目前需要在 `scripts/common-device-sources.py` 的 `MODELS` 中登记；新增共用资源也要同步其资源清单与迁移记录。检查器目前按固定资源集合校验已有机型；采用不同资源组合时，需要相应调整检查逻辑。
4. 在 Boiler-devices 仓库根目录运行：

```sh
python -B scripts/adaptations.py check
python -B scripts/common-device-sources.py check
```

`common-device-sources.py write` 会生成共用资源索引；修改记录后先检查差异，再运行 `check`。当前共用 TOON 的陀螺仪检查针对 BMI260；其他传感器需要相应的资源定义和检查支持。

TOON 本身不执行程序。要生成可安装的机型包，还需要 Boiler Installer 中对应的构建适配器和它要求的输入，步骤见[构建指南](BUILD.md)。
