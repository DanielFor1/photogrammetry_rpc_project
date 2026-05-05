# 模块 02：轨道内插实验报告

## 一、实验目的

本模块用于完成卫星轨道数据的时间内插。线阵 CCD 推扫影像中，不同扫描行对应不同成像时刻，因此需要根据离散 GPS 轨道数据，计算每个扫描时刻的卫星位置和速度。

模块 02 的输出结果为：

```text
time, X, Y, Z, Vx, Vy, Vz
```

该结果供后续严格成像模型、正投影、反投影和 RPC 样本点生成使用。

## 二、实验原理

教材第二章中指出，卫星轨道数据通常由离散星历采样得到，而线阵相机扫描频率较高，因此需要通过插值或拟合方法建立轨道参数随时间变化的连续模型。

本模块将卫星轨道参数表示为时间函数：

```text
X(t), Y(t), Z(t), Vx(t), Vy(t), Vz(t)
```

对任意成像时刻 `t`，分别计算卫星位置和速度分量。

本实验采用局部拉格朗日插值。对每一个目标时刻，选取其附近 4 个轨道采样点进行插值。拉格朗日插值公式为：

```text
f(t) = sum( f(t_i) * L_i(t) )
```

其中 `L_i(t)` 为拉格朗日基函数。局部插值相比全局高阶插值更简单，也能避免高阶多项式在长时间区间上的数值振荡。

## 三、实验数据

当前模块 01 尚未完成，因此本实验先从老师提供的原始 ZY3 仿真数据中提取模块 02 所需的标准输入。

原始数据文件：

```text
data/raw/DX_ZY3_NAD_gps.txt
data/raw/DX_ZY3_NAD_imagingTime.txt
```

其中 `DX_ZY3_NAD_gps.txt` 包含离散时刻的卫星位置和速度：

```text
timeCode, PX, PY, PZ, VX, VY, VZ
```

本模块将其整理为：

```text
time, X, Y, Z, Vx, Vy, Vz
```

`DX_ZY3_NAD_imagingTime.txt` 包含逐扫描行成像时刻，本模块只使用其中的 `Time` 列，并整理为：

```text
time
```

生成后的临时测试输入文件为：

```text
modules/module_02_orbit_interp/test_data/input_sample/preprocessed_orbit_sample.csv
modules/module_02_orbit_interp/test_data/input_sample/preprocessed_imaging_time_sample.csv
```

测试数据规模：

```text
轨道采样点：101 行
成像时刻：5378 行
```

## 四、实验步骤

1. 运行 `prepare_sample_data.py`，从原始 txt 文件中提取模块 02 的标准输入 CSV。
2. 读取 `preprocessed_orbit_sample.csv` 和 `preprocessed_imaging_time_sample.csv`。
3. 对每个成像时刻，选取附近 4 个轨道采样点。
4. 分别对 `X, Y, Z, Vx, Vy, Vz` 进行局部拉格朗日插值。
5. 将所有扫描时刻的插值结果保存为 `orbit_interp_result_sample.csv`。

执行命令：

```bash
python modules/module_02_orbit_interp/test_data/prepare_sample_data.py
python modules/module_02_orbit_interp/code/orbit_interp.py --mode sample
```

## 五、核心代码说明

模块核心代码位于：

```text
modules/module_02_orbit_interp/code/orbit_interp.py
```

主要函数包括：

- `lagrange_interpolate()`：对单个分量执行拉格朗日插值。
- `select_local_window()`：为目标成像时刻选择局部轨道采样窗口。
- `check_input_data()`：检查输入字段、时间顺序、时间范围和数据量。
- `interpolate_orbit()`：完成所有扫描时刻的轨道内插。
- `save_orbit_result()`：保存轨道内插结果。

代码设置了两种运行模式：

- `sample`：使用模块 02 当前临时测试数据。
- `formal`：预留给模块 01 的正式输出数据。

正式联调时，只需将模块 01 输出放在：

```text
data/processed/preprocessed_orbit_sample.csv
data/processed/preprocessed_imaging_time_sample.csv
```

然后执行：

```bash
python modules/module_02_orbit_interp/code/orbit_interp.py --mode formal
```

## 六、测试结果

运行 `sample` 模式后，程序输出：

```text
mode: sample
orbit rows: 101
imaging time rows: 5378
output rows: 5378
```

生成结果文件：

```text
modules/module_02_orbit_interp/test_data/output_sample/orbit_interp_result_sample.csv
```

输出字段为：

```text
time, X, Y, Z, Vx, Vy, Vz
```

输出前几行示例：

```text
time,X,Y,Z,Vx,Vy,Vz
131862405.00037192,-2381154.722863589,5164433.28503292,4077441.139352127,3356.4497108137266,-3233.3258239626593,6042.819301858244
131862405.00074388,-2381153.4743888634,5164432.082355387,4077443.387056063,3356.4505599962713,-3233.328228359444,6042.817534441346
```

结果表明，模块能够根据 101 个离散轨道采样点，对 5378 个扫描行成像时刻完成卫星位置和速度插值。

## 七、问题与改进

当前实现重点满足课程作业和小组联调需求，采用简单明确的 fail-fast 方式：

- 输入字段必须严格符合 README 规定。
- 不兼容 `scan_time` 等非标准字段。
- 不自动进行时间外推。
- 不在模块 02 中补算速度字段。

后续如果需要进一步提高精度，可考虑增加不同插值窗口大小的精度对比，或加入多项式拟合、样条插值等方法与当前局部拉格朗日插值结果进行比较。
