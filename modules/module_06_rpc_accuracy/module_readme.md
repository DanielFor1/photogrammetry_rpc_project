# 模块说明文档

## 一、模块基本信息

- 模块编号：06
- 模块名称：RPC 参数解算与精度评定
- 负责人：张瑞锦
- 所属文件夹：`modules/module_06_rpc_accuracy/`
- 当前完成状态：已完成

---

## 二、模块功能说明

本模块实现有理多项式系数 (RPC) 模型的参数解算与精度评定，是卫星摄影测量综合编程作业的最终环节。

主要功能：
1. 根据模块 05 生成的 RPC 样本点（地面坐标 + 像方坐标），建立线性化最小二乘方程，求解 RPC 归一化参数和 78 个有理多项式系数。
2. 内符合精度检查：将训练样本代入 RPC 正变换，与参考像方坐标比较残差。
3. 外符合精度检查（独立检查点）：用独立检查点评定 RPC 模型泛化精度。
4. 外符合精度检查（DEM 空间采样）：从 DEM 采样覆盖范围内的地面点，分析 RPC 正变换像方分布；可与严格模型配合完成完整外符合检验。
5. 综合精度报告：汇总内/外符合精度，输出对比表格。
6. 将 RPC 参数保存为标准格式文本文件。

---

## 三、代码文件说明

| 文件名 | 作用 |
|---|---|
| `rpc_solver.py` | RPC 参数解算：归一化参数计算、基函数构建、最小二乘求解、RPC 正变换、结果保存 |
| `accuracy_eval.py` | RPC 精度评定：内符合检查、外符合检查（独立检查点 / DEM 采样）、综合报告、RPC 文件解析 |
| `__init__.py` | 包标识文件 |

---

## 四、主要函数说明

### 函数 1：solve_rpc

函数名：`solve_rpc(rpc_sample_points)`
输入参数：RPC 样本点数据
输出结果：RPC 参数字典
调用方式：

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import solve_rpc

rpc_params = solve_rpc(rpc_sample_points)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_sample_points` | DataFrame / ndarray | RPC 解算样本点 | 列: point_id, lon, lat, height, row, col |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_params` | dict | RPC 参数集合 | 含 10 个归一化参数 + 4 组各 20 个多项式系数 |

`rpc_params` 字典包含的键：

| 键名 | 含义 |
|---|---|
| `LONG_OFF`, `LONG_SCALE` | 经度归一化偏移和缩放 |
| `LAT_OFF`, `LAT_SCALE` | 纬度归一化偏移和缩放 |
| `HEIGHT_OFF`, `HEIGHT_SCALE` | 高程归一化偏移和缩放 |
| `LINE_OFF`, `LINE_SCALE` | 行号归一化偏移和缩放 |
| `SAMP_OFF`, `SAMP_SCALE` | 列号归一化偏移和缩放 |
| `LINE_NUM_COEFF` | 行方向分子系数 (20 项) |
| `LINE_DEN_COEFF` | 行方向分母系数 (20 项) |
| `SAMP_NUM_COEFF` | 列方向分子系数 (20 项) |
| `SAMP_DEN_COEFF` | 列方向分母系数 (20 项) |

---

### 函数 2：rpc_forward

函数名：`rpc_forward(lat, lon, height, rpc_params)`
输入参数：大地坐标和 RPC 参数
输出结果：像方坐标 (row, col)
调用方式：

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import rpc_forward

row, col = rpc_forward(lat, lon, height, rpc_params)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `lat` | float | 纬度 (度) | |
| `lon` | float | 经度 (度) | |
| `height` | float | 高程 (米) | |
| `rpc_params` | dict | RPC 参数 | solve_rpc 的返回值 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `row` | float | 像方行坐标 | 像素单位 |
| `col` | float | 像方列坐标 | 像素单位 |

---

### 函数 3：save_rpc_result

函数名：`save_rpc_result(rpc_params, output_path)`
输入参数：RPC 参数字典和输出文件路径
输出结果：无（写入文件）
调用方式：

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import save_rpc_result

save_rpc_result(rpc_params, output_path)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_params` | dict | RPC 参数 | solve_rpc 的返回值 |
| `output_path` | str | 输出文件路径 | |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| （文件） | txt | RPC 参数文件 | 格式与标准 RPC 参数文件一致 |

---

### 函数 4：evaluate_accuracy

函数名：`evaluate_accuracy(rpc_params, check_points)`
输入参数：RPC 参数和检查点数据
输出结果：精度评定结果数组
调用方式：

```python
from modules.module_06_rpc_accuracy.code.accuracy_eval import evaluate_accuracy

accuracy_result = evaluate_accuracy(rpc_params, check_points)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_params` | dict | RPC 参数 | solve_rpc 的返回值 |
| `check_points` | DataFrame / ndarray | 检查点数据 | 列: point_id, lon, lat, height, row, col |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `accuracy_result` | ndarray, shape (N, 4) | 精度评定结果 | 列: point_id, row_error, col_error, plane_error |

---

### 函数 5：parse_rpc_file

函数名：`parse_rpc_file(rpc_path)`
输入参数：RPC 参数文件路径
输出结果：RPC 参数字典
调用方式：

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import parse_rpc_file

rpc_params = parse_rpc_file(rpc_path)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_path` | str | RPC 参数文件路径 | |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_params` | dict | RPC 参数 | 与 solve_rpc 返回格式一致 |

---

### 函数 6：sample_dem_points

函数名：`sample_dem_points(dem_path, gcps_arr, n_lat=20, n_lon=20)`
输入参数：DEM 路径、GCP 数组、采样密度
输出结果：采样地面点列表
调用方式：

```python
from modules.module_06_rpc_accuracy.code.accuracy_eval import sample_dem_points

# gcps_arr: (N, 3+) 数组，列 0=lat, 列 1=lon，用于确定影像覆盖范围
ground_points = sample_dem_points(dem_path, gcps_arr, n_lat=20, n_lon=20)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `dem_path` | str | DEM GeoTIFF 文件路径 | 可用test_data/input_sample下tif|
| `gcps_arr` | ndarray, shape (N, 3+) | GCP 数组 | 列 0=lat, 列 1=lon，用于确定覆盖范围 |
| `n_lat` | int | 纬度方向采样点数 | 默认 20 |
| `n_lon` | int | 经度方向采样点数 | 默认 20 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `ground_points` | list of (lat, lon, h) | 采样地面点 | 有效 DEM 内插高程点 |

依赖：rasterio, scipy（仅本函数需要）

---

### 函数 7：external_accuracy_check

函数名：`external_accuracy_check(dem_path, gcps_arr, rpc_params, strict_image_coords, n_lat=20, n_lon=20)`
输入参数：DEM 路径、GCP 数组、RPC 参数、严格模型像方坐标、采样密度
输出结果：外符合精度结果数组
调用方式：

```python
from modules.module_06_rpc_accuracy.code.accuracy_eval import external_accuracy_check

# strict_image_coords 来自模块 04 的 ground_to_image 反投影结果
accuracy_result = external_accuracy_check(
    dem_path, gcps_arr, rpc_params, strict_image_coords
)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `dem_path` | str | DEM 文件路径 | |
| `gcps_arr` | ndarray, shape (N, 3+) | GCP 数组 | 列 0=lat, 列 1=lon，用于确定覆盖范围 |
| `rpc_params` | dict | RPC 参数 | |
| `strict_image_coords` | list of (row, col) | 严格模型像方坐标 | 与 ground_points 一一对应 |
| `n_lat` | int | 纬度方向采样点数 | 默认 20 |
| `n_lon` | int | 经度方向采样点数 | 默认 20 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `accuracy_result` | ndarray, shape (N_valid, 4) | 外符合精度结果 | 列: point_id, row_error, col_error, plane_error |

依赖：rasterio, scipy

---

### 函数 8：comprehensive_accuracy_report

函数名：`comprehensive_accuracy_report(rpc_params, rpc_sample_points, check_points=None, dem_path=None, gcps_arr=None, strict_image_coords=None, output_dir=None)`
输入参数：RPC 参数、训练样本、检查点（可选）、DEM 路径（可选）、GCP 数组（可选）、严格模型坐标（可选）、输出目录（可选）
输出结果：综合报告 dict
调用方式：

```python
from modules.module_06_rpc_accuracy.code.accuracy_eval import comprehensive_accuracy_report

report = comprehensive_accuracy_report(
    rpc_params, rpc_sample_points,
    check_points=check_data,
    dem_path=dem_path,
    gcps_arr=gcps_arr,
    strict_image_coords=strict_coords,
    output_dir=output_dir
)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `rpc_params` | dict | RPC 参数 | |
| `rpc_sample_points` | ndarray | 训练样本点 | (N, 6) |
| `check_points` | ndarray | 独立检查点 | (M, 6), 可选 |
| `dem_path` | str | DEM 文件路径 | 可选 |
| `gcps_arr` | ndarray | GCP 数组 | 用于确定 DEM 采样范围，可选 |
| `strict_image_coords` | list of (row, col) | 严格模型像方坐标 | 可选 |
| `output_dir` | str | 结果输出目录 | 可选 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `report` | dict | 综合报告 | 含 internal, external, external_dem, statistics |

---

## 五、在 main.py 中的调用方式说明

### 方式 1：基本流程（内符合 + 外符合检查点）

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import solve_rpc, save_rpc_result
from modules.module_06_rpc_accuracy.code.accuracy_eval import evaluate_accuracy

# 1. 求解 RPC
rpc_params = solve_rpc(rpc_sample_points)

# 2. 内符合精度（训练样本回代）
internal_result = evaluate_accuracy(rpc_params, rpc_sample_points)

# 3. 外符合精度（独立检查点）
external_result = evaluate_accuracy(rpc_params, check_points)

# 4. 保存 RPC 参数
save_rpc_result(rpc_params, output_path)
```

### 方式 2：综合精度报告

```python
from modules.module_06_rpc_accuracy.code.rpc_solver import solve_rpc, save_rpc_result
from modules.module_06_rpc_accuracy.code.accuracy_eval import comprehensive_accuracy_report

# 1. 求解 RPC
rpc_params = solve_rpc(rpc_sample_points)

# 2. 综合精度报告（内符合 + 外符合 + DEM 采样）
# gcps_arr: (lat, lon, height) 数组，用于确定 DEM 采样范围
# strict_image_coords: 严格模型反投影像方坐标，来自模块 04
report = comprehensive_accuracy_report(
    rpc_params, rpc_sample_points,
    check_points=check_points,
    dem_path='data/reference_dem.tif',
    gcps_arr=gcps_arr,
    strict_image_coords=strict_coords,
    output_dir='data/result'
)

# 3. 保存 RPC 参数
save_rpc_result(rpc_params, output_path)
```

### 方式 3：外符合精度（配合严格模型，课本方法）

```python
from modules.module_06_rpc_accuracy.code.accuracy_eval import external_accuracy_check

# gcps_arr: (lat, lon, height) 数组，用于确定 DEM 采样范围
# strict_image_coords 由模块 04 的 ground_to_image + 反投影精化得到
external_result = external_accuracy_check(
    dem_path, gcps_arr, rpc_params, strict_image_coords
)
```

---

## 六、输入文件说明

| 输入文件名 | 文件格式 | 字段说明 |
|---|---|---|
| `rpc_sample_points_sample.csv` | CSV | point_id, lon, lat, height, row, col |
| `check_points_sample.csv` | CSV | point_id, lon, lat, height, row, col |
| `reference_dem.tif` | GeoTIFF | DEM 高程数据（外符合检查可选） |
| `rpc_params_sample.txt` | TXT | RPC 参数文件（精度评定时读取） |

说明：
- `rpc_sample_points_sample.csv` 来自模块 05 的输出，包含用于 RPC 解算的样本点。
- `check_points_sample.csv` 为独立检查点，用于外符合精度评定。
- `reference_dem.tif` 为 DEM 参考数据，用于外符合精度的 DEM 空间采样（可选）。

---

## 七、输出文件说明

| 输出文件名 | 文件格式 | 字段说明 |
|---|---|---|
| `rpc_params_sample.txt` | TXT | 10 个归一化参数 + 4 组各 20 个多项式系数 |
| `accuracy_result_sample.csv` | CSV | 内符合精度: point_id, row_error, col_error, plane_error |
| `accuracy_external_result_sample.csv` | CSV | 外符合精度: point_id, row_error, col_error, plane_error |

---

## 八、测试数据说明

- 测试输入数据位置：`test_data/input_sample/`
- 测试输出数据位置：`test_data/output_sample/`
- 是否可以单独运行：是
- 测试结果是否正常：是

单独运行方式：

```bash
# 先运行 RPC 解算
python modules/module_06_rpc_accuracy/code/rpc_solver.py

# 再运行精度评定（含内符合、外符合、DEM 采样）
python modules/module_06_rpc_accuracy/code/accuracy_eval.py
```

---

## 九、额外变量说明

本模块内部使用了以下变量命名表以外的变量，在此说明：

| 变量名 | 含义 | 备注 |
|---|---|---|
| `norm_lon` | 归一化经度 | (lon - LONG_OFF) / LONG_SCALE |
| `norm_lat` | 归一化纬度 | (lat - LAT_OFF) / LAT_SCALE |
| `norm_height` | 归一化高程 | (height - HEIGHT_OFF) / HEIGHT_SCALE |
| `norm_row` | 归一化行号 | (row - LINE_OFF) / LINE_SCALE |
| `norm_col` | 归一化列号 | (col - SAMP_OFF) / SAMP_SCALE |
| `basis_matrix` | 多项式基函数矩阵 | (N, 20) 形状 |
| `design_matrix` | 最小二乘设计矩阵 | 线性化后的系数矩阵 |
| `observation_vector` | 观测值向量 | 线性化后的右端向量 |
| `ground_points` | DEM 采样地面点 | (N, 4), 列: point_id, lon, lat, height |
| `image_coords` | RPC 正变换像方坐标 | (N, 2), 列: row, col |
| `strict_image_coords` | 严格模型像方坐标 | (N, 2), 来自模块 04 |
