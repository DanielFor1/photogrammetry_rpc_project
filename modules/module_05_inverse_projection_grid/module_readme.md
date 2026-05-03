# 模块 05 ：严格成像模型反投影与物方控制格网模块

## 一、模块基本信息

| 项目 | 内容 |
| --- | --- |
| 模块编号 | 05 |
| 模块名称 | 严格成像模型反投影与物方控制格网模块 |
| 所属课程 | 卫星摄影测量 综合编程作业 |
| 上游模块 | 模块 01 数据预处理与坐标转换；模块 02 轨道内插；模块 03 姿态内插与指向角处理；模块 04 严格成像模型正投影 |
| 下游模块 | 模块 06 RPC 参数解算与精度评定 |
| 代码目录 | `modules/module_05_inverse_projection_grid/code/` |
| 测试数据目录 | `modules/module_05_inverse_projection_grid/test_data/` |

## 二、模块功能说明

模块 05 在严格成像模型已经建立的前提下，完成两件事：

1. **反投影**：给定像点 `(row, col)`，根据该扫描行的轨道、姿态和指向角，反算其在物方的 `(lon, lat, height)`。
2. **物方控制格网与 RPC 样本生成**：在测区内按经纬度范围和高程分层生成均匀控制格网，再调用模块 04 的正投影函数，把每个格网点投影到像方，得到含 `(point_id, lon, lat, height, row, col)` 字段的 RPC 样本点文件，作为模块 06 RPC 解算的输入。

为了在模块 01–04 尚未全部交付时也能独立测试，本模块提供了简化的反投影占位实现以及一个仅用于自测的占位正投影函数。后续接入正式接口时只需替换函数体或替换 CSV 输入即可。

## 三、代码文件说明

| 文件 | 说明 |
| --- | --- |
| `code/inverse_projection.py` | 反投影主代码，含 `inverse_projection()` 函数和独立测试 `main()` |
| `code/control_grid.py` | 控制格网与 RPC 样本生成，含 `generate_control_grid()`、`generate_rpc_sample()` 和占位正投影 `_placeholder_forward_projection()` |

## 四、主要函数说明

### 1. `inverse_projection(image_points_df, orbit_df, rotation_df, camera_angle_df, reference_height=0.0)`

将像点反投影到给定参考高程的地面点。当前实现采用如下简化：

- 用球面近似（`EARTH_RADIUS_M = 6378137.0` 米）代替 WGS84 椭球；
- 用 `row` 在轨道、姿态表中按最近邻取值，未做精确时间插值；
- 用 `col` 在指向角查找表中最近邻取值；
- 视线与 `EARTH_RADIUS_M + reference_height` 球面相交，解一元二次方程取离卫星较近的正解；
- 只支持单参考高程，不做基于真实 DEM 或迭代逼近真实高程。

后续接入严格成像模型或迭代反投影时，只需替换函数体，保持输入输出字段不变。

### 2. `generate_control_grid(lon_range, lat_range, height_range, lon_step, lat_step, height_step)`

按测区经纬度范围和高程分层生成三维均匀控制格网。生成顺序为：高程→纬度→经度三层循环，`point_id` 从 0 顺序编号。

### 3. `generate_rpc_sample(control_grid_df, forward_projection_result_df)`

按 `point_id` 内连接控制格网与正投影结果，得到字段为 `point_id, lon, lat, height, row, col` 的 RPC 样本点。

### 4. `_placeholder_forward_projection(...)`（仅自测用）

用经纬度相对中心点的线性映射近似得到 `(row, col)`，仅在 `control_grid.py` 的独立测试中使用。正式流程必须替换为模块 04 `forward_projection` 的输出。

## 五、函数参数名说明

| 参数名 | 含义 | 单位 |
| --- | --- | --- |
| `image_points_df` | 像点表 | — |
| `orbit_df` | 各扫描时刻轨道参数 | 米 |
| `rotation_df` | 各扫描时刻旋转矩阵（相机系→ECEF） | — |
| `camera_angle_df` | 相机指向角查找表 | 弧度 |
| `reference_height` | 反投影参考高程 | 米 |
| `lon_range` / `lat_range` | 经度／纬度范围 `(min, max)` | 度 |
| `height_range` | 高程范围 `(min, max)` | 米 |
| `lon_step` / `lat_step` | 经度／纬度方向格网间距 | 度 |
| `height_step` | 高程分层间距 | 米 |
| `control_grid_df` | 控制格网 | — |
| `forward_projection_result_df` | 模块 04 正投影结果 | — |

## 六、输入输出字段说明

### 输入

`image_points_sample.csv`

| 字段 | 含义 |
| --- | --- |
| `point_id` | 像点编号 |
| `row` | 像方行号 |
| `col` | 像方列号 |

`orbit_interp_result_sample.csv`（来自模块 02）

| 字段 | 含义 | 单位 |
| --- | --- | --- |
| `scan_time` | 扫描时刻 | 秒（约定） |
| `X`, `Y`, `Z` | 卫星 ECEF 位置 | 米 |

`rotation_matrix_result_sample.csv`（来自模块 03）

| 字段 | 含义 |
| --- | --- |
| `scan_time` | 扫描时刻 |
| `R11..R33` | 相机系→ECEF 旋转矩阵 9 个元素 |

`camera_angle_result_sample.csv`（来自模块 03）

| 字段 | 含义 | 单位 |
| --- | --- | --- |
| `col` | 列号 | — |
| `psi_x`, `psi_y` | 沿轨／垂轨方向指向角 | 弧度 |

### 输出

`inverse_projection_result_sample.csv`：`point_id, lon, lat, height`
`control_grid_sample.csv`：`point_id, lon, lat, height`
`rpc_sample_points_sample.csv`：`point_id, lon, lat, height, row, col`

经纬高顺序固定为 `lon, lat, height`，与共同变量命名表一致。

## 七、在 `main.py` 中的调用方式说明

模块 05 暂不修改 `main.py`。后续整合时，可在 `main.py` 中按如下方式调用（伪代码）：

```python
import pandas as pd
from modules.module_05_inverse_projection_grid.code.inverse_projection import inverse_projection
from modules.module_05_inverse_projection_grid.code.control_grid import (
    generate_control_grid,
    generate_rpc_sample,
)

# 1. 读取上游模块结果
orbit_df = pd.read_csv('data/processed/orbit_interp_result.csv')
rotation_df = pd.read_csv('data/processed/rotation_matrix_result.csv')
camera_angle_df = pd.read_csv('data/processed/camera_angle_result.csv')
image_points_df = pd.read_csv('data/sample/image_points.csv')

# 2. 反投影
inverse_projection_result_df = inverse_projection(
    image_points_df, orbit_df, rotation_df, camera_angle_df,
    reference_height=0.0,
)
inverse_projection_result_df.to_csv(
    'data/processed/inverse_projection_result.csv', index=False)

# 3. 控制格网
control_grid_df = generate_control_grid(
    lon_range=(lon_min, lon_max),
    lat_range=(lat_min, lat_max),
    height_range=(h_min, h_max),
    lon_step=lon_step,
    lat_step=lat_step,
    height_step=height_step,
)
control_grid_df.to_csv('data/processed/control_grid.csv', index=False)

# 4. 调用模块 04 正投影得到 (row, col)
from modules.module_04_forward_projection.code.forward_projection import forward_projection
forward_projection_result_df = forward_projection(
    control_grid_df, orbit_df, rotation_df, camera_angle_df,
)

# 5. 合并生成 RPC 样本点，交给模块 06
rpc_sample_points_df = generate_rpc_sample(
    control_grid_df, forward_projection_result_df)
rpc_sample_points_df.to_csv(
    'data/processed/rpc_sample_points.csv', index=False)
```

## 八、测试数据说明

### 8.1 构造的小样本（`test_data/input_sample/`）

为保证模块05能独立运行，这里提供一组手工构造的小样本：

- 卫星位于约 505 km 高的 ZY-3 类轨道，星下点中心 `(114.749°E, 35.879°N)`，沿轨方向纬度从 35.839° 缓慢移动到 35.919°；
- 姿态矩阵令相机 z 轴指向地心、x/y 轴近似东向/北向；
- 相机指向角全部置 0，对应近似垂直下视；
- 像点 `image_points_sample.csv` 选取 5 个不同 `row`、`col` 固定为 25。

预期结果：5 个像点反投影应落在 lon ≈ 114.749°、lat 沿 35.839°→35.919° 线性变化、height ≈ 0 m，与 `output_sample/inverse_projection_result_sample.csv` 一致。

控制格网测试取测区 lon ∈ [114.65°, 114.85°]、lat ∈ [35.83°, 35.93°]、height ∈ [0, 8000 m]，间距 0.05° / 0.05° / 2000 m，共 5×3×5 = 75 个控制点。

独立运行命令：

```powershell
cd modules/module_05_inverse_projection_grid/code
python inverse_projection.py
python control_grid.py
```

### 8.2 真实数据接入（`test_data/real_data_demo/`）

`real_data_demo/` 提供把老师发的 ZY-3 NAD 仿真原始数据（gps / att / imagingTime / cbr）转换为模块05可吃 CSV 的演示脚本 `extract_real_data.py`，并立即调用模块05验证流程。详见该目录下的 `README.md`。

注意：

- 原始数据文件不上传仓库（已加入 `.gitignore`），老师另发；
- 真实数据接入时，旋转矩阵 `rotation_matrix_result_sample.csv` 暂用基于 GPS 位置构造的"近似星下视"占位矩阵，等模块01（J2000→ECEF）+ 模块03（四元数内插）完成后替换；
- 替换后反投影结果应精确落到测区中心 `(114.749°E, 35.879°N)` 附近。

## 九、额外变量说明

- `EARTH_RADIUS_M`：球面近似地球半径，6378137.0 米，仅用于本模块当前简化实现，正式接入 WGS84 椭球后可删除。
- `view_vector_camera`、`view_vector_ecef`：相机系/地心地固系下的视线方向单位向量，用于反投影几何求解。
- `target_radius`：反投影所对应的等高球面半径，等于 `EARTH_RADIUS_M + reference_height`。
- 旋转矩阵字段命名 `R11..R33` 而非 `_matrix` 后缀，是因为命名规则要求矩阵变量使用 `_matrix` 后缀，而 CSV 中只能存平铺的 9 个元素；在 Python 内部，重组后的矩阵变量名仍为 `rotation_matrix`，符合命名规则。
