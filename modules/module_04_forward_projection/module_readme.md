# 模块说明文档

---

## 一、模块基本信息

- **模块编号**：4
- **模块名称**：严格成像模型正投影模块 (Forward Projection Module)
- **负责人**：易星辰
- **所属文件夹**：`modules/module_04_forward_projection/`
- **当前完成状态**：已完成

---

## 二、模块功能说明

本模块实现卫星摄影测量中的**严格成像模型正投影变换**。其核心功能是利用卫星的轨道位置、姿态矩阵以及相机的内方位元素，通过共线方程逻辑，将地面物方坐标（ECEF 坐标系下的 X, Y, Z）投影到像平面上，并计算出对应的像方行列号（Row, Col）。

---

## 三、代码文件说明

| 文件名 | 作用 |
| :--- | :--- |
| `forward_projection.py` | 核心算法文件，包含单点投影计算与批量处理函数。 |
| `module_readme.md` | 模块说明文档，包含接口、参数及调用说明。 |

---

## 四、主要函数说明

### 函数 1

- **函数名**：`calculate_forward_projection`
- **输入参数**：`ground_point`, `orbit_result`, `attitude_result`, `camera_params`
- **输出结果**：`image_point_result`
- **调用方式**：内部逻辑调用或由批量处理函数迭代调用。

**参数说明：**

| 参数名 | 类型 | 含义 | 备注 |
| :--- | :--- | :--- | :--- |
| `ground_point` | `dict` | 地面点坐标 | 包含键值 `X`, `Y`, `Z` (单位: m) |
| `orbit_result` | `dict` | 卫星轨道位置 | 包含键值 `X`, `Y`, `Z` (单位: m) |
| `attitude_result` | `ndarray` | 姿态旋转矩阵 | 3x3 矩阵，ECEF 到相机系的转换 |
| `camera_params` | `dict` | 相机内参 | 包含 `f`, `row0`, `col0`, `pixel_size` |

**输出说明：**

| 输出字段 | 类型 | 含义 | 备注 |
| :--- | :--- | :--- | :--- |
| `row` | `float` | 像方行号坐标 | 对应像方 Row |
| `col` | `float` | 像方列号坐标 | 对应像方 Col |

---

## 五、在 main.py 中的调用方式说明

示例：

```python
from modules.module_04_forward_projection.code.forward_projection import batch_forward_projection

# 1. 配置相机参数
camera_config = {
    'f': 50000.0,
    'pixel_size': 5.0,
    'row0': 10000.0,
    'col0': 10000.0
}

# 2. 执行批量正投影计算
batch_forward_projection(
    input_path='data/processed/merged_data.csv',
    output_path='data/result/projection_result.csv',
    camera_params=camera_config
)
```

---

## 六、输入文件说明

| 输入文件名 | 文件格式 | 字段说明 |
| :--- | :--- | :--- |
| `merged_data.csv` | CSV | `X, Y, Z` (地面点), `sat_X, sat_Y, sat_Z` (卫星位置), `m11-m33` (姿态矩阵分量) |

---

## 七、输出文件说明

| 输出文件名 | 文件格式 | 字段说明 |
| :--- | :--- | :--- |
| `projection_result.csv` | CSV | 在输入字段基础上新增 `row`, `col` 字段 |

---

## 八、测试数据说明

- **测试输入数据位置**：`modules/module_04_forward_projection/test_data/input_ground_points.csv`
- **测试输出数据位置**：`modules/module_04_forward_projection/test_data/output_projection_results.csv`
- **是否可以单独运行**：是（运行 `forward_projection.py` 脚本即可）
- **测试结果是否正常**：正常，像点坐标计算逻辑符合摄影测量几何模型。
