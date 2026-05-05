# 模块 02：轨道内插模块说明

## 一、模块基本信息

- 模块编号：模块 02
- 模块名称：轨道内插模块
- 所属文件夹：`modules/module_02_orbit_interp/`
- 主要代码文件：`code/orbit_interp.py`
- 测试数据准备脚本：`test_data/prepare_sample_data.py`
- 当前完成状态：已完成局部拉格朗日轨道内插、临时测试数据模式和正式联调模式。

## 二、模块功能

本模块根据离散轨道数据和逐扫描行成像时刻，计算每个成像时刻对应的卫星位置与速度。

线阵 CCD 推扫成像中，每一行影像对应一个不同的成像时刻，因此后续严格成像模型需要每个扫描时刻的轨道参数。本模块输出的 `orbit_interp_result` 将作为后续正投影、反投影和 RPC 样本生成模块的基础输入。

## 三、核心算法

根据教材第二章的轨道数据建模思路，离散星历数据可表示为时间的函数：

```text
X(t), Y(t), Z(t), Vx(t), Vy(t), Vz(t)
```

本模块采用局部拉格朗日插值。对每一个成像时刻 `time`，选取其附近 4 个轨道采样点，分别对 `X, Y, Z, Vx, Vy, Vz` 六个分量进行插值。

拉格朗日插值形式为：

```text
f(t) = sum( f(t_i) * L_i(t) )
```

其中 `L_i(t)` 为拉格朗日基函数。代码使用局部窗口，不使用全局高阶插值，以避免高阶多项式带来的数值不稳定。

## 四、输入数据

正式联调时推荐输入文件：

```text
data/processed/preprocessed_orbit_sample.csv
data/processed/preprocessed_imaging_time_sample.csv
```

轨道数据字段：

```text
time, X, Y, Z, Vx, Vy, Vz
```

成像时刻字段：

```text
time
```

当前模块 01 尚未完成时，模块 02 使用临时测试数据：

```text
modules/module_02_orbit_interp/test_data/input_sample/preprocessed_orbit_sample.csv
modules/module_02_orbit_interp/test_data/input_sample/preprocessed_imaging_time_sample.csv
```

这些临时测试数据由 `test_data/prepare_sample_data.py` 从原始文件中提取生成：

```text
data/raw/DX_ZY3_NAD_gps.txt
data/raw/DX_ZY3_NAD_imagingTime.txt
```

## 五、输出数据

正式联调输出文件：

```text
data/processed/orbit_interp_result_sample.csv
```

临时测试输出文件：

```text
modules/module_02_orbit_interp/test_data/output_sample/orbit_interp_result_sample.csv
```

输出字段：

```text
time, X, Y, Z, Vx, Vy, Vz
```

每一行表示一个扫描时刻对应的卫星位置和速度。

## 六、主要函数

### `interpolate_orbit(orbit_data, imaging_time_data, window_size=4)`

根据离散轨道数据和成像时刻进行轨道内插。

参数：

- `orbit_data`：`pandas.DataFrame`，包含 `time, X, Y, Z, Vx, Vy, Vz`
- `imaging_time_data`：`pandas.DataFrame`，包含 `time`
- `window_size`：局部拉格朗日插值窗口大小，默认值为 4

返回：

- `orbit_interp_result`：`pandas.DataFrame`，包含 `time, X, Y, Z, Vx, Vy, Vz`

### `save_orbit_result(orbit_interp_result, output_path)`

将轨道内插结果保存为 CSV 文件。

### `lagrange_interpolate(time_values, data_values, target_time)`

对单个分量执行拉格朗日插值。

## 七、运行方式

生成临时测试输入数据：

```bash
python modules/module_02_orbit_interp/test_data/prepare_sample_data.py
```

使用临时测试数据运行：

```bash
python modules/module_02_orbit_interp/code/orbit_interp.py --mode sample
```

使用模块 01 正式输出运行：

```bash
python modules/module_02_orbit_interp/code/orbit_interp.py --mode formal
```

默认运行模式为 `sample`。

## 八、在主流程中的调用方式

```python
import pandas as pd
from modules.module_02_orbit_interp.code.orbit_interp import (
    interpolate_orbit,
    save_orbit_result,
)

orbit_data = pd.read_csv("data/processed/preprocessed_orbit_sample.csv")
imaging_time_data = pd.read_csv("data/processed/preprocessed_imaging_time_sample.csv")

orbit_interp_result = interpolate_orbit(orbit_data, imaging_time_data)
save_orbit_result(
    orbit_interp_result,
    "data/processed/orbit_interp_result_sample.csv",
)
```

## 九、数据检查原则

本模块按 fail-fast 原则实现，不做静默兼容或自动修正：

- 缺少规定字段时直接报错。
- 轨道时间不严格递增时直接报错。
- 成像时刻超出轨道时间范围时直接报错。
- 轨道点数量少于插值窗口大小时直接报错。

正式输出字段统一使用 `time, X, Y, Z, Vx, Vy, Vz`，不使用 `scan_time` 等额外字段。
