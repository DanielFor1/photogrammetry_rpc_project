# 《卫星摄影测量》综合编程作业代码仓库

本仓库用于存放《卫星摄影测量》综合编程作业的小组代码、模块说明文档、测试数据、测试输出结果和实验报告。

项目采用模块化方式组织。各成员按照自己负责的模块完成代码、模块说明文档、测试输入数据、测试输出数据和实验报告，后续由组长统一进行 `main.py` 联调、整合和最终提交。

---

## 一、项目任务说明

本次综合编程作业主要包含以下五项任务：

1. J2000 坐标系转换为地心地固坐标系。
2. 建立姿态、轨道内插模型。
3. 严格成像模型构建，包括正投影与反投影变换。
4. 物方控制格网构建。
5. RPC 模型参数解算与精度评定。

根据任务内容，本项目划分为 6 个代码模块。

---

## 二、命名规范说明

本仓库统一采用 `docs/variable_naming_table.md` 中的命名规则。

主要规则如下：

1. 变量名使用英文小写加下划线，即 `snake_case`。
2. 函数名采用“动词 + 名词”的形式，例如 `interpolate_orbit()`、`solve_rpc()`。
3. 文件名使用小写英文加下划线，例如 `orbit_interp.py`、`rpc_solver.py`。
4. CSV 字段名统一使用英文，不使用中文字段名。
5. 经纬高顺序固定为 `lon, lat, height`。
6. 三维直角坐标分量固定为 `X, Y, Z`。
7. 像方坐标统一使用 `row, col`，不使用 `x, y` 表示像方坐标。
8. 矩阵变量统一使用 `_matrix` 后缀，例如 `rotation_matrix`。
9. 结果变量统一使用 `_result` 后缀，例如 `accuracy_result`。
10. 路径变量统一使用 `_path` 后缀，例如 `orbit_path`、`output_path`。

---

## 三、项目模块划分

| 模块编号 | 模块名称 | 主要任务 | 对应文件夹 |
|---|---|---|---|
| 模块 01 | 数据读取、预处理与坐标系转换 | 读取轨道、姿态、成像时刻等原始数据，统一时间、单位和数据结构，完成 J2000 到 ECEF 坐标转换 | `modules/module_01_data_preprocess_coord/` |
| 模块 02 | 轨道内插模块 | 建立轨道内插模型，按扫描行成像时刻插值计算卫星位置和速度 | `modules/module_02_orbit_interp/` |
| 模块 03 | 姿态内插与指向角处理模块 | 建立姿态四元数内插模型，处理相机指向角查找表，计算姿态矩阵或旋转参数 | `modules/module_03_attitude_interp/` |
| 模块 04 | 严格成像模型正投影模块 | 调用坐标转换、轨道内插、姿态内插结果，建立严格成像模型，实现物方点到像方点的正投影计算 | `modules/module_04_forward_projection/` |
| 模块 05 | 严格成像模型反投影与物方控制格网模块 | 实现像点到地面点的反投影或迭代求解，构建物方控制格网，生成 RPC 解算样本点数据 | `modules/module_05_inverse_projection_grid/` |
| 模块 06 | RPC 参数解算与精度评定模块 | 根据样本点建立 RPC 解算方程，完成 RPC 参数求解，利用检查点进行精度评定 | `modules/module_06_rpc_accuracy/` |

---

## 四、模块衔接关系

项目整体流程如下：

```text
模块 01：数据读取、预处理与坐标系转换
        ↓
模块 02：轨道内插
        ↓
模块 03：姿态内插与指向角处理
        ↓
模块 04：严格成像模型正投影
        ↓
模块 05：严格成像模型反投影与物方控制格网
        ↓
模块 06：RPC 参数解算与精度评定
```

其中：

1. 模块 01、模块 02、模块 03 先完成基础数据处理与中间结果生成。
2. 模块 04、模块 05 在基础数据结果上完成严格成像模型正反投影和样本点生成。
3. 模块 06 最后完成 RPC 参数解算与精度评定。

---

## 五、仓库结构说明

```text
satellite_photogrammetry_project/
│
├── README.md
├── main.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── group_rules.md
│   ├── variable_naming_table.md
│   ├── function_interface.md
│   └── data_format_standard.md
│
├── data/
│   ├── raw/
│   ├── sample/
│   ├── processed/
│   └── result/
│
├── modules/
│   ├── module_01_data_preprocess_coord/
│   │   ├── code/
│   │   │   ├── data_preprocess.py
│   │   │   └── coord_transform.py
│   │   ├── test_data/
│   │   ├── module_readme.md
│   │   └── report.md
│   │
│   ├── module_02_orbit_interp/
│   │   ├── code/
│   │   │   └── orbit_interp.py
│   │   ├── test_data/
│   │   ├── module_readme.md
│   │   └── report.md
│   │
│   ├── module_03_attitude_interp/
│   │   ├── code/
│   │   │   └── attitude_interp.py
│   │   ├── test_data/
│   │   ├── module_readme.md
│   │   └── report.md
│   │
│   ├── module_04_forward_projection/
│   │   ├── code/
│   │   │   └── forward_projection.py
│   │   ├── test_data/
│   │   ├── module_readme.md
│   │   └── report.md
│   │
│   ├── module_05_inverse_projection_grid/
│   │   ├── code/
│   │   │   ├── inverse_projection.py
│   │   │   └── control_grid.py
│   │   ├── test_data/
│   │   ├── module_readme.md
│   │   └── report.md
│   │
│   └── module_06_rpc_accuracy/
│       ├── code/
│       │   ├── rpc_solver.py
│       │   └── accuracy_eval.py
│       ├── test_data/
│       ├── module_readme.md
│       └── report.md
│
└── examples/
    └── demo_pipeline.py
```

---

## 六、主要文件夹说明

| 文件夹或文件 | 作用 |
|---|---|
| `README.md` | 项目总说明文档 |
| `main.py` | 项目主程序入口，后续由组长统一整合 |
| `config.py` | 项目路径和公共配置文件 |
| `requirements.txt` | Python 依赖库列表 |
| `.gitignore` | Git 忽略文件配置 |
| `docs/` | 公共规范文档，包括变量命名、函数接口、数据格式和小组规则 |
| `data/raw/` | 原始数据文件夹，不建议上传大体积原始数据 |
| `data/sample/` | 小样本测试数据文件夹 |
| `data/processed/` | 中间结果文件夹 |
| `data/result/` | 最终结果、RPC 参数、残差和精度统计结果 |
| `modules/` | 各功能模块代码、测试数据、模块说明和实验报告 |
| `examples/` | 示例调用代码 |

---

## 七、各模块代码文件、主要函数与建议输入输出

### 模块 01：数据读取、预处理与坐标系转换

代码文件：

```text
modules/module_01_data_preprocess_coord/code/data_preprocess.py
modules/module_01_data_preprocess_coord/code/coord_transform.py
```

主要函数：

```python
load_raw_data()
j2000_to_ecef()
save_preprocessed_data()
```

建议输入文件：

```text
data/raw/orbit_data.*
data/raw/attitude_data.*
data/raw/imaging_time.*
data/sample/orbit_sample.csv
data/sample/attitude_sample.csv
data/sample/imaging_time_sample.csv
```

建议输出文件：

```text
data/processed/ecef_result_sample.csv
data/processed/preprocessed_orbit_sample.csv
data/processed/preprocessed_attitude_sample.csv
data/processed/preprocessed_imaging_time_sample.csv
```

建议字段：

```text
orbit_sample.csv:
time, X, Y, Z, Vx, Vy, Vz

attitude_sample.csv:
time, q0, q1, q2, q3

imaging_time_sample.csv:
time

ecef_result_sample.csv:
time, x_ecef, y_ecef, z_ecef
```

---

### 模块 02：轨道内插模块

代码文件：

```text
modules/module_02_orbit_interp/code/orbit_interp.py
```

主要函数：

```python
interpolate_orbit()
save_orbit_result()
```

建议输入文件：

```text
data/processed/preprocessed_orbit_sample.csv
data/processed/preprocessed_imaging_time_sample.csv
```

建议输出文件：

```text
data/processed/orbit_interp_result_sample.csv
```

建议字段：

```text
orbit_interp_result_sample.csv:
time, X, Y, Z, Vx, Vy, Vz
```

---

### 模块 03：姿态内插与指向角处理模块

代码文件：

```text
modules/module_03_attitude_interp/code/attitude_interp.py
```

主要函数：

```python
interpolate_attitude()
process_camera_look_angle()
build_rotation_matrix()
```

建议输入文件：

```text
data/processed/preprocessed_attitude_sample.csv
data/processed/preprocessed_imaging_time_sample.csv
data/sample/look_angle_table_sample.csv
```

建议输出文件：

```text
data/processed/attitude_interp_result_sample.csv
data/processed/camera_angle_result_sample.csv
data/processed/rotation_matrix_result_sample.csv
```

建议字段：

```text
attitude_interp_result_sample.csv:
time, q0, q1, q2, q3

rotation_matrix_result_sample.csv:
time, r11, r12, r13, r21, r22, r23, r31, r32, r33
```

---

### 模块 04：严格成像模型正投影模块

代码文件：

```text
modules/module_04_forward_projection/code/forward_projection.py
```

主要函数：

```python
forward_projection()
```

建议输入文件：

```text
data/processed/orbit_interp_result_sample.csv
data/processed/rotation_matrix_result_sample.csv
data/processed/camera_angle_result_sample.csv
data/sample/ground_points_sample.csv
```

建议输出文件：

```text
data/processed/forward_projection_result_sample.csv
```

建议字段：

```text
ground_points_sample.csv:
point_id, lon, lat, height

forward_projection_result_sample.csv:
point_id, row, col
```

注意：像方坐标统一使用 `row, col`，不要写成 `x, y` 或 `image_x, image_y`。

---

### 模块 05：严格成像模型反投影与物方控制格网模块

代码文件：

```text
modules/module_05_inverse_projection_grid/code/inverse_projection.py
modules/module_05_inverse_projection_grid/code/control_grid.py
```

主要函数：

```python
inverse_projection()
generate_control_grid()
generate_rpc_sample()
```

建议输入文件：

```text
data/processed/orbit_interp_result_sample.csv
data/processed/rotation_matrix_result_sample.csv
data/processed/camera_angle_result_sample.csv
data/sample/image_points_sample.csv
```

建议输出文件：

```text
data/processed/inverse_projection_result_sample.csv
data/processed/control_grid_sample.csv
data/processed/rpc_sample_points_sample.csv
```

建议字段：

```text
image_points_sample.csv:
point_id, row, col

inverse_projection_result_sample.csv:
point_id, lon, lat, height

control_grid_sample.csv:
point_id, lon, lat, height

rpc_sample_points_sample.csv:
point_id, lon, lat, height, row, col
```

---

### 模块 06：RPC 参数解算与精度评定模块

代码文件：

```text
modules/module_06_rpc_accuracy/code/rpc_solver.py
modules/module_06_rpc_accuracy/code/accuracy_eval.py
```

主要函数：

```python
solve_rpc()
evaluate_accuracy()
save_rpc_result()
```

建议输入文件：

```text
data/processed/rpc_sample_points_sample.csv
data/sample/check_points_sample.csv
```

建议输出文件：

```text
data/result/rpc_params_sample.txt
data/result/accuracy_result_sample.csv
```

建议字段：

```text
rpc_sample_points_sample.csv:
point_id, lon, lat, height, row, col

check_points_sample.csv:
point_id, lon, lat, height, row, col

accuracy_result_sample.csv:
point_id, row_error, col_error, plane_error
```

---

## 八、每个模块需要提交的内容

每个模块需要在自己的模块文件夹中提交以下内容：

1. 本模块代码文件。
2. 模块说明文档 `module_readme.md`。
3. 本模块在 `main.py` 中的函数调用方式说明。
4. 函数参数名说明。
5. 输入、输出字段说明。
6. 测试输入数据。
7. 测试输出数据。
8. 本模块对应的实验报告 `report.md`。

---

## 九、代码提交规范

请各位组员注意：

1. 不要随意修改其他模块的代码文件。
2. 不要直接修改 `main.py`，`main.py` 后续由组长统一整合。
3. 每个模块的函数名、输入参数、输出结果和变量命名尽量按照 `docs/variable_naming_table.md` 中的统一要求编写。
4. 如果使用变量命名表以外的变量，一定要在自己的 `module_readme.md` 中单独说明。
5. 提交前请先确认自己的代码可以单独运行。
6. 测试数据可以自己按照代码输入格式简单构造，不需要使用原始作业数据。
7. 需要在 `module_readme.md` 中写清楚模块名称、输入文件、输出文件、主要函数、调用方式和测试状态。
8. 可以参考已有代码思路，但不要 1:1 复制。

---

## 十、运行环境

建议使用 Python 3.8 及以上版本。

安装依赖：

```bash
pip install -r requirements.txt
```

---

## 十一、运行方式

当前阶段各模块先进行单独测试，不要求直接运行完整项目。

后续统一整合后，可通过以下命令运行主程序：

```bash
python main.py
```

单独测试某一模块时，可以运行对应模块中的代码文件，例如：

```bash
python modules/module_02_orbit_interp/code/orbit_interp.py
```

---

## 十二、Git 使用说明

每次开始修改前，建议先同步远程仓库：

```bash
git pull
```

修改完成并测试通过后，提交到 GitHub：

```bash
git add .
git commit -m "填写本次修改说明"
git push
```

---

## 十三、时间安排

| 时间 | 任务 |
|---|---|
| 5 月 5 日 20:00 前 | 各模块完成代码、说明文档、测试数据、测试输出和实验报告上传 |
| 5 月 6 日—5 月 10 日 | 完成 PPT 制作 |
| 后续 | 由组长统一进行代码联调、`main.py` 整合和最终提交 |

---

## 十四、注意事项

1. 原始大体积数据不建议直接上传到 GitHub。
2. 每个模块只需要上传小样本测试数据。
3. 中间结果文件名尽量保持统一，避免后续整合困难。
4. 如果模块之间数据格式不一致，需要在 `module_readme.md` 中说明。
5. 最终整合时以各模块的 `module_readme.md`、测试数据和测试输出结果为主要依据。
