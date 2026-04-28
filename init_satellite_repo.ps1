# =====================================================================
# 《卫星摄影测量》综合编程作业 GitHub 仓库一键构建脚本
# 使用方法：
# 1. 先 git clone 仓库，并 cd 进入仓库根目录
# 2. 将本脚本保存为 init_satellite_repo.ps1
# 3. 在 PowerShell 中运行：
#    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#    .\init_satellite_repo.ps1
# =====================================================================

$ErrorActionPreference = "Stop"

Write-Host "当前目录：$(Get-Location)"
Write-Host "本脚本会清空并重新生成以下内容：docs、data、modules、examples、README.md、main.py、config.py、requirements.txt、.gitignore"
Write-Host "注意：如果这些文件夹里已有重要代码或文档，请先备份。"
$confirm = Read-Host "确认清空旧结构并重新生成？请输入 Y 继续，输入其他内容取消"

if (($confirm -ne "Y") -and ($confirm -ne "y")) {
    Write-Host "已取消操作。"
    exit
}

# ---------- 1. 清空旧结构 ----------

$removePaths = @(
    "docs",
    "data",
    "modules",
    "examples",
    "README.md",
    "main.py",
    "config.py",
    "requirements.txt",
    ".gitignore"
)

foreach ($path in $removePaths) {
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force
    }
}

# ---------- 2. 创建文件夹 ----------

$dirs = @(
    "docs",

    "data",
    "data\raw",
    "data\sample",
    "data\processed",
    "data\result",

    "modules",
    "modules\module_01_data_preprocess_coord",
    "modules\module_01_data_preprocess_coord\code",
    "modules\module_01_data_preprocess_coord\test_data",
    "modules\module_01_data_preprocess_coord\test_data\input_sample",
    "modules\module_01_data_preprocess_coord\test_data\output_sample",

    "modules\module_02_orbit_interp",
    "modules\module_02_orbit_interp\code",
    "modules\module_02_orbit_interp\test_data",
    "modules\module_02_orbit_interp\test_data\input_sample",
    "modules\module_02_orbit_interp\test_data\output_sample",

    "modules\module_03_attitude_interp",
    "modules\module_03_attitude_interp\code",
    "modules\module_03_attitude_interp\test_data",
    "modules\module_03_attitude_interp\test_data\input_sample",
    "modules\module_03_attitude_interp\test_data\output_sample",

    "modules\module_04_forward_projection",
    "modules\module_04_forward_projection\code",
    "modules\module_04_forward_projection\test_data",
    "modules\module_04_forward_projection\test_data\input_sample",
    "modules\module_04_forward_projection\test_data\output_sample",

    "modules\module_05_inverse_projection_grid",
    "modules\module_05_inverse_projection_grid\code",
    "modules\module_05_inverse_projection_grid\test_data",
    "modules\module_05_inverse_projection_grid\test_data\input_sample",
    "modules\module_05_inverse_projection_grid\test_data\output_sample",

    "modules\module_06_rpc_accuracy",
    "modules\module_06_rpc_accuracy\code",
    "modules\module_06_rpc_accuracy\test_data",
    "modules\module_06_rpc_accuracy\test_data\input_sample",
    "modules\module_06_rpc_accuracy\test_data\output_sample",

    "examples"
)

foreach ($dir in $dirs) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
}

# ---------- 3. 创建空文件夹占位 .gitkeep ----------

$gitkeepFiles = @(
    "data\raw\.gitkeep",
    "data\sample\.gitkeep",
    "data\processed\.gitkeep",
    "data\result\.gitkeep",

    "modules\module_01_data_preprocess_coord\test_data\input_sample\.gitkeep",
    "modules\module_01_data_preprocess_coord\test_data\output_sample\.gitkeep",

    "modules\module_02_orbit_interp\test_data\input_sample\.gitkeep",
    "modules\module_02_orbit_interp\test_data\output_sample\.gitkeep",

    "modules\module_03_attitude_interp\test_data\input_sample\.gitkeep",
    "modules\module_03_attitude_interp\test_data\output_sample\.gitkeep",

    "modules\module_04_forward_projection\test_data\input_sample\.gitkeep",
    "modules\module_04_forward_projection\test_data\output_sample\.gitkeep",

    "modules\module_05_inverse_projection_grid\test_data\input_sample\.gitkeep",
    "modules\module_05_inverse_projection_grid\test_data\output_sample\.gitkeep",

    "modules\module_06_rpc_accuracy\test_data\input_sample\.gitkeep",
    "modules\module_06_rpc_accuracy\test_data\output_sample\.gitkeep"
)

foreach ($file in $gitkeepFiles) {
    New-Item -Path $file -ItemType File -Force | Out-Null
}

# ---------- 4. 创建 Python 包初始化文件 ----------

$initFiles = @(
    "modules\__init__.py",
    "modules\module_01_data_preprocess_coord\__init__.py",
    "modules\module_01_data_preprocess_coord\code\__init__.py",
    "modules\module_02_orbit_interp\__init__.py",
    "modules\module_02_orbit_interp\code\__init__.py",
    "modules\module_03_attitude_interp\__init__.py",
    "modules\module_03_attitude_interp\code\__init__.py",
    "modules\module_04_forward_projection\__init__.py",
    "modules\module_04_forward_projection\code\__init__.py",
    "modules\module_05_inverse_projection_grid\__init__.py",
    "modules\module_05_inverse_projection_grid\code\__init__.py",
    "modules\module_06_rpc_accuracy\__init__.py",
    "modules\module_06_rpc_accuracy\code\__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -Path $file -ItemType File -Force | Out-Null
}

# ---------- 5. 写入 README.md ----------

@'
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
'@ | Set-Content -Path "README.md" -Encoding UTF8

# ---------- 6. 写入 config.py ----------

@'
from pathlib import Path

project_root = Path(__file__).resolve().parent

raw_data_dir = project_root / "data" / "raw"
sample_data_dir = project_root / "data" / "sample"
processed_data_dir = project_root / "data" / "processed"
result_dir = project_root / "data" / "result"

orbit_path = sample_data_dir / "orbit_sample.csv"
attitude_path = sample_data_dir / "attitude_sample.csv"
imaging_time_path = sample_data_dir / "imaging_time_sample.csv"
look_angle_table_path = sample_data_dir / "look_angle_table_sample.csv"

output_path = processed_data_dir
'@ | Set-Content -Path "config.py" -Encoding UTF8

# ---------- 7. 写入 main.py ----------

@'
"""
main.py

《卫星摄影测量》综合编程作业主程序入口。

注意：
1. 本文件后续由组长统一整合。
2. 各位组员不要直接修改本文件。
3. 各模块只需要在自己的 module_readme.md 中说明函数调用方式。
"""


def main():
    print("《卫星摄影测量》综合编程作业")
    print("当前 main.py 为统一整合入口，后续由组长进行模块联调。")


if __name__ == "__main__":
    main()
'@ | Set-Content -Path "main.py" -Encoding UTF8

# ---------- 8. 写入 requirements.txt ----------

@'
numpy
pandas
scipy
matplotlib
'@ | Set-Content -Path "requirements.txt" -Encoding UTF8

# ---------- 9. 写入 .gitignore ----------

@'
# Python cache
__pycache__/
*.pyc
*.pyo

# Virtual environment
venv/
env/
.venv/

# IDE
.vscode/
.idea/

# Jupyter
.ipynb_checkpoints/

# Large data files
*.tif
*.tiff
*.img
*.dat
*.bin
*.zip
*.rar
*.7z

# System files
.DS_Store
Thumbs.db
'@ | Set-Content -Path ".gitignore" -Encoding UTF8

# ---------- 10. 写入 docs 文档 ----------

@'
# 共同变量命名表

本文件用于记录《卫星摄影测量》综合编程作业的统一命名规则。

## 一、通用命名规则

| 类别 | 统一要求 | 示例 |
|---|---|---|
| 变量名 | 英文小写 + 下划线 snake_case | orbit_data, image_points |
| 函数名 | 动词 + 名词 | interpolate_orbit(), solve_rpc() |
| 文件名 | 小写英文 + 下划线 | orbit_interp.py, rpc_solver.py |
| CSV字段名 | 统一英文，不使用中文字段名 | time, lon, lat, height, row, col |
| 坐标顺序 | 经纬高固定为 lon, lat, height；三维直角坐标固定为 X, Y, Z | lon, lat, height / X, Y, Z |
| 像方坐标 | 统一使用 row, col | row 表示行号，col 表示列号 |
| 矩阵变量 | 后缀统一用 _matrix | rotation_matrix |
| 结果变量 | 后缀统一用 _result | accuracy_result |
| 路径变量 | 后缀统一用 _path | orbit_path, output_path |

## 二、统一代码文件名

| 模块 | 代码文件名 |
|---|---|
| 数据预处理 | data_preprocess.py |
| 坐标转换 | coord_transform.py |
| 轨道内插 | orbit_interp.py |
| 姿态内插 | attitude_interp.py |
| 严格成像正投影 | forward_projection.py |
| 严格成像反投影 | inverse_projection.py |
| 控制格网 | control_grid.py |
| RPC解算 | rpc_solver.py |
| 精度评定 | accuracy_eval.py |

## 三、统一函数名称

| 函数名 | 功能 |
|---|---|
| load_raw_data() | 读取轨道、姿态、成像时刻等原始数据 |
| j2000_to_ecef() | J2000 坐标系转换到地心地固坐标系 |
| save_preprocessed_data() | 保存预处理结果 |
| interpolate_orbit() | 计算各成像时刻的卫星位置与速度 |
| save_orbit_result() | 保存轨道内插结果 |
| interpolate_attitude() | 计算各成像时刻的姿态四元数 |
| process_camera_look_angle() | 处理相机指向角查找表 |
| build_rotation_matrix() | 生成旋转矩阵 |
| forward_projection() | 物方点到像方点正投影 |
| inverse_projection() | 像方点到物方点反投影 |
| generate_control_grid() | 构建物方控制格网 |
| generate_rpc_sample() | 生成 RPC 解算样本点 |
| solve_rpc() | 求解 RPC 参数 |
| evaluate_accuracy() | 利用检查点进行精度评定 |
| save_rpc_result() | 保存 RPC 参数与精度结果 |

## 四、禁止混用名称

| 不要使用 | 统一使用 |
|---|---|
| x, y | row, col |
| lat, lon, h | lon, lat, height |
| H, h, z_height | height |
| rot, R, mat | rotation_matrix |
| sat_pos | satellite_position |
| sat_vel | satellite_velocity |
| img_pts | image_points |
| obj_pts | ground_points |
| err_x, err_y | row_error, col_error |
| result, res | 具体模块名 + _result |
'@ | Set-Content -Path "docs\variable_naming_table.md" -Encoding UTF8

@'
# 函数接口说明

每个模块需要在自己的 `module_readme.md` 中说明主要函数接口。

建议格式如下：

函数名：
输入参数：
输出结果：
调用方式：

参数说明需要写清楚：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|

输出说明需要写清楚：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|

所有函数名、参数名和输出字段应尽量符合 `docs/variable_naming_table.md`。
'@ | Set-Content -Path "docs\function_interface.md" -Encoding UTF8

@'
# 数据格式规范

## 一、CSV 字段命名

CSV 字段统一使用英文，不使用中文字段名。

## 二、常用字段

| 字段名 | 含义 |
|---|---|
| time | 时间 |
| lon | 经度 |
| lat | 纬度 |
| height | 高程 |
| X, Y, Z | 三维直角坐标分量 |
| Vx, Vy, Vz | 卫星速度分量 |
| q0, q1, q2, q3 | 四元数 |
| row | 像方行坐标 |
| col | 像方列坐标 |
| point_id | 点号 |
| row_error | 行方向误差 |
| col_error | 列方向误差 |
| plane_error | 平面误差 |

## 三、注意事项

1. 像方坐标统一使用 `row, col`。
2. 经纬高顺序统一使用 `lon, lat, height`。
3. 三维直角坐标分量统一使用 `X, Y, Z`。
4. 每个模块如果使用了其他字段，需要在 `module_readme.md` 中说明。
'@ | Set-Content -Path "docs\data_format_standard.md" -Encoding UTF8

@'
# 小组提交规范

1. 不要随意修改其他模块的代码文件。
2. 不要直接修改 `main.py`，`main.py` 后续由组长统一整合。
3. 每个模块的函数名、输入参数、输出结果和变量命名尽量按照 `variable_naming_table.md` 编写。
4. 如果使用变量命名表以外的变量，一定要在自己的 `module_readme.md` 中单独说明。
5. 提交前请先确认自己的代码可以单独运行。
6. 测试数据可以自己按照代码输入格式简单构造，不需要使用原始作业数据。
7. 需要在 `module_readme.md` 中写清楚模块名称、输入文件、输出文件、主要函数、调用方式和测试状态。
8. 可以参考已有代码思路，但不要 1:1 复制。
'@ | Set-Content -Path "docs\group_rules.md" -Encoding UTF8

# ---------- 11. 写入模块代码模板 ----------

@'
"""
data_preprocess.py

数据读取与预处理模块。
"""


def load_raw_data(orbit_path, attitude_path, imaging_time_path):
    """
    读取轨道、姿态、成像时刻等原始数据。

    参数：
        orbit_path: 离散轨道数据路径
        attitude_path: 离散姿态数据路径
        imaging_time_path: 扫描行成像时刻文件路径

    返回：
        orbit_data, attitude_data, imaging_time_data
    """
    print("load_raw_data() 待实现")
    return None, None, None


def save_preprocessed_data(preprocessed_data, output_path):
    """
    保存预处理结果。

    参数：
        preprocessed_data: 预处理后的数据
        output_path: 输出路径
    """
    print("save_preprocessed_data() 待实现")


if __name__ == "__main__":
    print("模块 01：data_preprocess.py 单独测试入口")
'@ | Set-Content -Path "modules\module_01_data_preprocess_coord\code\data_preprocess.py" -Encoding UTF8

@'
"""
coord_transform.py

坐标转换模块。
"""


def j2000_to_ecef(position_j2000, imaging_time):
    """
    将 J2000 坐标转换为地心地固坐标。

    参数：
        position_j2000: J2000 坐标向量 [x_j2000, y_j2000, z_j2000]
        imaging_time: 成像时刻

    返回：
        position_ecef: 地心地固坐标向量 [x_ecef, y_ecef, z_ecef]
    """
    print("j2000_to_ecef() 待实现")
    position_ecef = None
    return position_ecef


if __name__ == "__main__":
    print("模块 01：coord_transform.py 单独测试入口")
'@ | Set-Content -Path "modules\module_01_data_preprocess_coord\code\coord_transform.py" -Encoding UTF8

@'
"""
orbit_interp.py

轨道内插模块。
"""


def interpolate_orbit(orbit_data, imaging_time_data):
    """
    根据成像时刻计算卫星位置与速度。

    参数：
        orbit_data: 轨道数据
        imaging_time_data: 成像时刻数据

    返回：
        orbit_interp_result: 轨道内插结果
    """
    print("interpolate_orbit() 待实现")
    orbit_interp_result = None
    return orbit_interp_result


def save_orbit_result(orbit_interp_result, output_path):
    """
    保存轨道内插结果。
    """
    print("save_orbit_result() 待实现")


if __name__ == "__main__":
    print("模块 02：orbit_interp.py 单独测试入口")
'@ | Set-Content -Path "modules\module_02_orbit_interp\code\orbit_interp.py" -Encoding UTF8

@'
"""
attitude_interp.py

姿态内插与相机指向角处理模块。
"""


def interpolate_attitude(attitude_data, imaging_time_data):
    """
    计算各成像时刻的姿态四元数。

    返回：
        attitude_interp_result
    """
    print("interpolate_attitude() 待实现")
    attitude_interp_result = None
    return attitude_interp_result


def process_camera_look_angle(look_angle_table):
    """
    处理相机指向角查找表。

    返回：
        camera_angle_result
    """
    print("process_camera_look_angle() 待实现")
    camera_angle_result = None
    return camera_angle_result


def build_rotation_matrix(quaternion, camera_angle_result=None):
    """
    根据四元数和相机指向角生成旋转矩阵。

    返回：
        rotation_matrix
    """
    print("build_rotation_matrix() 待实现")
    rotation_matrix = None
    return rotation_matrix


if __name__ == "__main__":
    print("模块 03：attitude_interp.py 单独测试入口")
'@ | Set-Content -Path "modules\module_03_attitude_interp\code\attitude_interp.py" -Encoding UTF8

@'
"""
forward_projection.py

严格成像模型正投影模块。
"""


def forward_projection(ground_points, orbit_interp_result, rotation_matrix_result, camera_angle_result):
    """
    实现物方点到像方点的正投影计算。

    参数：
        ground_points: 物方点集合，字段建议为 point_id, lon, lat, height
        orbit_interp_result: 轨道内插结果
        rotation_matrix_result: 旋转矩阵结果
        camera_angle_result: 相机指向角处理结果

    返回：
        forward_projection_result: 正投影结果，字段建议为 point_id, row, col
    """
    print("forward_projection() 待实现")
    forward_projection_result = None
    return forward_projection_result


if __name__ == "__main__":
    print("模块 04：forward_projection.py 单独测试入口")
'@ | Set-Content -Path "modules\module_04_forward_projection\code\forward_projection.py" -Encoding UTF8

@'
"""
inverse_projection.py

严格成像模型反投影模块。
"""


def inverse_projection(image_points, orbit_interp_result, rotation_matrix_result, camera_angle_result):
    """
    实现像点到物方点的反投影或迭代求解。

    参数：
        image_points: 像方点集合，字段建议为 point_id, row, col

    返回：
        inverse_projection_result: 反投影结果，字段建议为 point_id, lon, lat, height
    """
    print("inverse_projection() 待实现")
    inverse_projection_result = None
    return inverse_projection_result


if __name__ == "__main__":
    print("模块 05：inverse_projection.py 单独测试入口")
'@ | Set-Content -Path "modules\module_05_inverse_projection_grid\code\inverse_projection.py" -Encoding UTF8

@'
"""
control_grid.py

物方控制格网与 RPC 样本点生成模块。
"""


def generate_control_grid(lon_range, lat_range, height_range, lon_step, lat_step, height_step):
    """
    构建物方控制格网。

    返回：
        control_grid_points
    """
    print("generate_control_grid() 待实现")
    control_grid_points = None
    return control_grid_points


def generate_rpc_sample(control_grid_points, forward_projection_result):
    """
    生成 RPC 解算样本点。

    返回：
        rpc_sample_points
    """
    print("generate_rpc_sample() 待实现")
    rpc_sample_points = None
    return rpc_sample_points


if __name__ == "__main__":
    print("模块 05：control_grid.py 单独测试入口")
'@ | Set-Content -Path "modules\module_05_inverse_projection_grid\code\control_grid.py" -Encoding UTF8

@'
"""
rpc_solver.py

RPC 参数解算模块。
"""


def solve_rpc(rpc_sample_points):
    """
    根据 RPC 样本点建立解算方程并求解 RPC 参数。

    返回：
        rpc_params
    """
    print("solve_rpc() 待实现")
    rpc_params = None
    return rpc_params


def save_rpc_result(rpc_params, output_path):
    """
    保存 RPC 参数结果。
    """
    print("save_rpc_result() 待实现")


if __name__ == "__main__":
    print("模块 06：rpc_solver.py 单独测试入口")
'@ | Set-Content -Path "modules\module_06_rpc_accuracy\code\rpc_solver.py" -Encoding UTF8

@'
"""
accuracy_eval.py

RPC 精度评定模块。
"""


def evaluate_accuracy(rpc_params, check_points):
    """
    利用检查点进行精度评定。

    返回：
        accuracy_result
    """
    print("evaluate_accuracy() 待实现")
    accuracy_result = None
    return accuracy_result


if __name__ == "__main__":
    print("模块 06：accuracy_eval.py 单独测试入口")
'@ | Set-Content -Path "modules\module_06_rpc_accuracy\code\accuracy_eval.py" -Encoding UTF8

# ---------- 12. 写入 examples 示例 ----------

@'
"""
demo_pipeline.py

本文件仅用于说明后续主流程可能的调用顺序。
当前阶段各模块先单独完成和测试，最终由组长统一整合。
"""


def demo_pipeline():
    print("示例流程：")
    print("1. load_raw_data()")
    print("2. j2000_to_ecef()")
    print("3. interpolate_orbit()")
    print("4. interpolate_attitude()")
    print("5. build_rotation_matrix()")
    print("6. forward_projection()")
    print("7. inverse_projection()")
    print("8. generate_control_grid()")
    print("9. generate_rpc_sample()")
    print("10. solve_rpc()")
    print("11. evaluate_accuracy()")


if __name__ == "__main__":
    demo_pipeline()
'@ | Set-Content -Path "examples\demo_pipeline.py" -Encoding UTF8

# ---------- 13. 写入 module_readme.md 模板 ----------

$moduleReadmeContent = @'
# 模块说明文档

## 一、模块基本信息

- 模块编号：
- 模块名称：
- 负责人：
- 所属文件夹：
- 当前完成状态：

---

## 二、模块功能说明

请简要说明本模块实现的主要功能。

---

## 三、代码文件说明

| 文件名 | 作用 |
|---|---|

---

## 四、主要函数说明

### 函数 1

函数名：
输入参数：
输出结果：
调用方式：

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|

---

## 五、在 main.py 中的调用方式说明

示例：

from modules.module_xx_xxx.code.xxx import xxx_function

result = xxx_function(input_data)

---

## 六、输入文件说明

| 输入文件名 | 文件格式 | 字段说明 |
|---|---|---|

---

## 七、输出文件说明

| 输出文件名 | 文件格式 | 字段说明 |
|---|---|---|

---

## 八、测试数据说明

- 测试输入数据位置：
- 测试输出数据位置：
- 是否可以单独运行：
- 测试结果是否正常：

---

## 九、额外变量说明

如果使用了变量命名表以外的变量，请在这里说明。

| 变量名 | 含义 | 备注 |
|---|---|---|
'@

$moduleReadmePaths = @(
    "modules\module_01_data_preprocess_coord\module_readme.md",
    "modules\module_02_orbit_interp\module_readme.md",
    "modules\module_03_attitude_interp\module_readme.md",
    "modules\module_04_forward_projection\module_readme.md",
    "modules\module_05_inverse_projection_grid\module_readme.md",
    "modules\module_06_rpc_accuracy\module_readme.md"
)

foreach ($path in $moduleReadmePaths) {
    $moduleReadmeContent | Set-Content -Path $path -Encoding UTF8
}

# ---------- 14. 写入 report.md 模板 ----------

$reportContent = @'
# 实验报告

## 一、实验目的

说明本模块在整个《卫星摄影测量》综合编程作业中的作用。

## 二、实验原理

简要说明本模块涉及的摄影测量原理、坐标转换原理、内插方法、成像模型或 RPC 解算方法。

## 三、实验数据

说明本模块使用的输入数据，包括数据来源、字段含义和数据格式。

## 四、实验步骤

1. 读取或构造输入数据。
2. 调用本模块主要函数。
3. 输出计算结果。
4. 检查输出结果是否符合预期。

## 五、核心代码说明

简要说明本模块主要代码逻辑。

## 六、测试结果

说明测试输入、测试输出和运行结果。

## 七、问题与改进

说明当前模块存在的问题，以及后续可以改进的地方。
'@

$reportPaths = @(
    "modules\module_01_data_preprocess_coord\report.md",
    "modules\module_02_orbit_interp\report.md",
    "modules\module_03_attitude_interp\report.md",
    "modules\module_04_forward_projection\report.md",
    "modules\module_05_inverse_projection_grid\report.md",
    "modules\module_06_rpc_accuracy\report.md"
)

foreach ($path in $reportPaths) {
    $reportContent | Set-Content -Path $path -Encoding UTF8
}

Write-Host "仓库结构、README、代码模板和文档模板已创建完成。"
Write-Host "建议接着执行：git status"
Write-Host "确认无误后执行：git add . ; git commit -m '初始化卫星摄影测量项目仓库结构' ; git push"
