# 《卫星摄影测量》综合编程作业共同变量命名表

说明：本表用于全组统一代码命名、CSV 字段名、函数名和中间结果文件名。所有变量建议使用英文 `snake_case`，中文只写在注释和报告说明中。

---

## 一、通用命名规则

| 类别 | 统一要求 | 示例 |
|---|---|---|
| 变量名 | 使用英文小写 + 下划线 `snake_case` | `orbit_data`, `image_points` |
| 函数名 | 动词 + 名词，表达功能 | `interpolate_orbit()`, `solve_rpc()` |
| 文件名 | 小写英文 + 下划线 | `orbit_interp.py`, `rpc_solver.py` |
| CSV 字段名 | 统一英文，不使用中文字段名 | `time`, `lon`, `lat`, `height`, `row`, `col` |
| 坐标顺序 | 经纬高固定为 `lon, lat, height`；三维直角坐标固定为 `X, Y, Z` | `lon, lat, height` / `X, Y, Z` |
| 像方坐标 | 统一使用 `row, col`，不混用 `x, y` | `row` 表示行号，`col` 表示列号 |
| 矩阵变量 | 矩阵变量后缀统一用 `_matrix` | `rotation_matrix` |
| 结果变量 | 结果变量后缀统一用 `_result` | `accuracy_result` |
| 路径变量 | 路径变量后缀统一用 `_path` | `orbit_path`, `output_path` |

---

## 二、项目文件和模块命名

| 模块 | 代码文件名 | 主要功能 |
|---|---|---|
| 数据预处理 | `data_preprocess.py` | 读取轨道、姿态、成像时刻等原始数据并统一格式 |
| 坐标转换 | `coord_transform.py` | 完成 J2000 到地心地固坐标系转换 |
| 轨道内插 | `orbit_interp.py` | 根据成像时刻计算卫星位置和速度 |
| 姿态内插 | `attitude_interp.py` | 姿态四元数内插、指向角处理、旋转矩阵构建 |
| 严格成像正投影 | `forward_projection.py` | 物方点到像方点的正投影计算 |
| 严格成像反投影 | `inverse_projection.py` | 像点到物方点的反投影或迭代求解 |
| 控制格网 | `control_grid.py` | 生成物方控制格网和 RPC 样本点 |
| RPC 解算 | `rpc_solver.py` | 建立 RPC 方程并求解 RPC 参数 |
| 精度评定 | `accuracy_eval.py` | 检查点误差计算、残差统计、精度输出 |

---

## 三、路径与配置变量命名

| 变量名 | 含义 | 建议所在文件 |
|---|---|---|
| `project_root` | 项目根目录 | `config.py` |
| `raw_data_dir` | 原始数据文件夹 | `config.py` |
| `sample_data_dir` | 小样本测试数据文件夹 | `config.py` |
| `processed_data_dir` | 中间结果文件夹 | `config.py` |
| `result_dir` | 最终结果文件夹 | `config.py` |
| `orbit_path` | 离散轨道数据路径 | `config.py` / `main.py` |
| `attitude_path` | 离散姿态数据路径 | `config.py` / `main.py` |
| `imaging_time_path` | 扫描行成像时刻文件路径 | `config.py` / `main.py` |
| `look_angle_table_path` | 相机指向角查找表路径 | `config.py` / `main.py` |
| `output_path` | 通用输出路径变量 | 各模块函数参数 |

---

## 四、通用数据对象命名

| 变量名 | 数据类型建议 | 含义 |
|---|---|---|
| `orbit_data` | `DataFrame` / `ndarray` | 原始离散轨道数据 |
| `attitude_data` | `DataFrame` / `ndarray` | 原始离散姿态数据 |
| `imaging_time_data` | `DataFrame` / `ndarray` | 扫描行成像时刻数据 |
| `look_angle_table` | `DataFrame` / `ndarray` | 相机指向角查找表 |
| `camera_params` | `dict` | 相机内外部参数或成像参数集合 |
| `ground_points` | `DataFrame` / `ndarray` | 物方点集合 |
| `image_points` | `DataFrame` / `ndarray` | 像方点集合 |
| `check_points` | `DataFrame` / `ndarray` | 精度评定检查点集合 |
| `rpc_sample_points` | `DataFrame` / `ndarray` | RPC 解算样本点集合 |

---

## 五、时间变量和字段命名

| 变量名 / 字段名 | 含义 | 备注 |
|---|---|---|
| `time` | 统一时间字段名 | 所有 CSV 中的时间列都叫 `time` |
| `orbit_time` | 轨道数据对应时刻 | 用于轨道内插 |
| `attitude_time` | 姿态数据对应时刻 | 用于姿态内插 |
| `imaging_time` | 单个成像时刻 | 函数内部单时刻变量 |
| `imaging_time_data` | 全部成像时刻数据 | 通常来自扫描行成像时刻文件 |
| `time_interval` | 时间间隔 | 用于检查采样间隔或插值间隔 |

---

## 六、坐标变量和字段命名

| 变量名 / 字段名 | 含义 | 统一要求 |
|---|---|---|
| `X`, `Y`, `Z` | 地心地固坐标或三维直角坐标 | 大写字母固定表示三维直角坐标分量 |
| `lon`, `lat`, `height` | 经度、纬度、高程 | 经纬高顺序固定，不写成 `lat, lon, h` |
| `x_j2000`, `y_j2000`, `z_j2000` | J2000 坐标分量 | 用于转换前数据 |
| `x_ecef`, `y_ecef`, `z_ecef` | 地心地固坐标分量 | 用于转换后数据 |
| `position_j2000` | J2000 坐标向量 | 形如 `[x_j2000, y_j2000, z_j2000]` |
| `position_ecef` | 地心地固坐标向量 | 形如 `[x_ecef, y_ecef, z_ecef]` |
| `ground_point` | 单个物方点 | 单点变量 |
| `ground_points` | 多个物方点 | 点集变量 |

---

## 七、轨道模块变量命名

| 变量名 / 字段名 | 含义 | 建议格式 |
|---|---|---|
| `satellite_position` | 卫星位置向量 | `[X, Y, Z]` |
| `satellite_velocity` | 卫星速度向量 | `[Vx, Vy, Vz]` |
| `X`, `Y`, `Z` | 卫星位置字段 | CSV 字段 |
| `Vx`, `Vy`, `Vz` | 卫星速度字段 | CSV 字段 |
| `orbit_interp_result` | 轨道内插结果 | `time, X, Y, Z, Vx, Vy, Vz` |
| `interpolated_position` | 内插得到的位置 | 函数内部变量 |
| `interpolated_velocity` | 内插得到的速度 | 函数内部变量 |

---

## 八、姿态与相机指向变量命名

| 变量名 / 字段名 | 含义 | 建议格式 |
|---|---|---|
| `q0`, `q1`, `q2`, `q3` | 四元数字段 | 统一顺序为 `q0, q1, q2, q3` |
| `quaternion` | 单个四元数 | `[q0, q1, q2, q3]` |
| `attitude_interp_result` | 姿态内插结果 | `time, q0, q1, q2, q3` |
| `look_angle_table` | 相机指向角查找表 | 原始或读取后的表格数据 |
| `camera_angle_result` | 处理后的相机指向角参数 | 供旋转矩阵构建使用 |
| `rotation_matrix` | 单个旋转矩阵 | `3 x 3` 矩阵 |
| `rotation_matrix_result` | 全部时刻旋转矩阵结果 | `time, r11, ..., r33` |
| `r11`, `r12`, ..., `r33` | 旋转矩阵字段 | 按行展开 |

---

## 九、严格成像模型变量命名

| 变量名 / 字段名 | 含义 | 备注 |
|---|---|---|
| `row` | 像方行坐标 | 统一不用 `y` 表示行号 |
| `col` | 像方列坐标 | 统一不用 `x` 表示列号 |
| `image_point` | 单个像点 | `[row, col]` |
| `image_points` | 多个像点 | `point_id, row, col` |
| `forward_projection_result` | 正投影结果 | 物方点到像方点结果 |
| `inverse_projection_result` | 反投影结果 | 像方点到物方点结果 |
| `ray_direction` | 像点对应视线方向 | 严格成像模型内部变量 |
| `camera_center` | 摄影中心或卫星相机中心 | 严格成像模型内部变量 |
| `iteration_count` | 反投影迭代次数 | 反投影内部变量 |
| `convergence_threshold` | 迭代收敛阈值 | 建议写在 `config.py` |

---

## 十、物方控制格网与样本变量命名

| 变量名 / 字段名 | 含义 | 备注 |
|---|---|---|
| `lon_range` | 经度范围 | `(lon_min, lon_max)` |
| `lat_range` | 纬度范围 | `(lat_min, lat_max)` |
| `height_range` | 高程范围 | `(height_min, height_max)` |
| `lon_step` | 经度格网间隔 | 控制格网参数 |
| `lat_step` | 纬度格网间隔 | 控制格网参数 |
| `height_step` | 高程分层间隔 | 控制格网参数 |
| `control_grid_points` | 物方控制格网点 | `point_id, lon, lat, height` |
| `rpc_sample_points` | RPC 解算样本点 | `point_id, lon, lat, height, row, col` |
| `control_points` | 控制点集合 | 用于 RPC 参数解算 |
| `check_points` | 检查点集合 | 用于精度评定 |

---

## 十一、RPC 解算与精度评定变量命名

| 变量名 / 字段名 | 含义 | 备注 |
|---|---|---|
| `rpc_params` | RPC 参数结果 | 可为 `dict` / `ndarray` / `txt` |
| `rpc_coefficients` | RPC 系数向量 | 函数内部或输出变量 |
| `normal_matrix` | 法方程矩阵 | 最小二乘求解内部变量 |
| `design_matrix` | 设计矩阵 | 最小二乘求解内部变量 |
| `observation_vector` | 观测值向量 | 最小二乘求解内部变量 |
| `residuals` | 残差向量 | 解算后误差 |
| `row_error` | 行方向误差 | 精度评定字段 |
| `col_error` | 列方向误差 | 精度评定字段 |
| `plane_error` | 平面误差 | `sqrt(row_error^2 + col_error^2)` |
| `rmse_row` | 行方向 RMSE | 精度统计指标 |
| `rmse_col` | 列方向 RMSE | 精度统计指标 |
| `rmse_plane` | 平面 RMSE | 精度统计指标 |
| `accuracy_result` | 精度评定结果 | `point_id, row_error, col_error, plane_error` |

---

## 十二、统一函数名称表

| 函数名 | 负责模块 | 功能 |
|---|---|---|
| `load_raw_data()` | 数据预处理 | 读取轨道、姿态、成像时刻等原始数据 |
| `j2000_to_ecef()` | 坐标转换 | J2000 坐标系转换到地心地固坐标系 |
| `save_preprocessed_data()` | 数据预处理 | 保存预处理结果 |
| `interpolate_orbit()` | 轨道内插 | 计算各成像时刻的卫星位置与速度 |
| `save_orbit_result()` | 轨道内插 | 保存轨道内插结果 |
| `interpolate_attitude()` | 姿态内插 | 计算各成像时刻的姿态四元数 |
| `process_camera_look_angle()` | 姿态与相机指向 | 处理相机指向角查找表 |
| `build_rotation_matrix()` | 姿态与相机指向 | 生成旋转矩阵 |
| `forward_projection()` | 严格成像模型 | 物方点到像方点正投影 |
| `inverse_projection()` | 严格成像模型 | 像方点到物方点反投影 |
| `generate_control_grid()` | 控制格网 | 构建物方控制格网 |
| `generate_rpc_sample()` | 控制格网 / RPC 样本 | 生成 RPC 解算样本点 |
| `solve_rpc()` | RPC 解算 | 求解 RPC 参数 |
| `evaluate_accuracy()` | 精度评定 | 利用检查点进行精度评定 |
| `save_rpc_result()` | RPC 解算 / 精度评定 | 保存 RPC 参数与精度结果 |

---

## 十三、统一中间结果文件命名

| 文件名 | 内容 | 主要字段 |
|---|---|---|
| `orbit_sample.csv` | 轨道小样本输入 | `time, X, Y, Z, Vx, Vy, Vz` |
| `attitude_sample.csv` | 姿态小样本输入 | `time, q0, q1, q2, q3` |
| `imaging_time_sample.csv` | 成像时刻小样本 | `time` |
| `look_angle_table_sample.csv` | 相机指向角查找表小样本 | 按实际数据字段统一 |
| `ecef_result_sample.csv` | 坐标转换示例结果 | `time, x_ecef, y_ecef, z_ecef` |
| `orbit_interp_result_sample.csv` | 轨道内插结果 | `time, X, Y, Z, Vx, Vy, Vz` |
| `attitude_interp_result_sample.csv` | 姿态内插结果 | `time, q0, q1, q2, q3` |
| `rotation_matrix_result_sample.csv` | 旋转矩阵结果 | `time, r11, ..., r33` |
| `ground_points_sample.csv` | 物方点小样本 | `point_id, lon, lat, height` |
| `forward_projection_result_sample.csv` | 正投影结果 | `point_id, row, col` |
| `inverse_projection_result_sample.csv` | 反投影结果 | `point_id, lon, lat, height` |
| `control_grid_sample.csv` | 物方控制格网 | `point_id, lon, lat, height` |
| `rpc_sample_points_sample.csv` | RPC 样本点 | `point_id, lon, lat, height, row, col` |
| `rpc_params_sample.txt` | RPC 参数结果 | 按解算结果格式保存 |
| `accuracy_result_sample.csv` | 精度评定结果 | `point_id, row_error, col_error, plane_error` |

---

## 十四、禁止混用名称对照表

| 不要使用 | 统一使用 | 说明 |
|---|---|---|
| `x, y` | `row, col` | 像方坐标统一用行列号 |
| `lat, lon, h` | `lon, lat, height` | 经纬高顺序固定 |
| `H`, `h`, `z_height` | `height` | 高程字段统一为 `height` |
| `rot`, `R`, `mat` | `rotation_matrix` | 旋转矩阵命名统一 |
| `sat_pos` | `satellite_position` | 卫星位置命名统一 |
| `sat_vel` | `satellite_velocity` | 卫星速度命名统一 |
| `img_pts` | `image_points` | 像点集合命名统一 |
| `obj_pts` | `ground_points` | 物方点集合命名统一 |
| `err_x`, `err_y` | `row_error`, `col_error` | 误差方向命名统一 |
| `result`, `res` | 具体模块名 + `_result` | 避免 `result` 含义不清 |
