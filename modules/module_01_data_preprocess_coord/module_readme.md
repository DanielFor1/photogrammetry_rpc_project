# 模块说明文档

## 一、模块基本信息

- 模块编号：01
- 模块名称：数据读取、预处理与坐标系转换
- 负责人：刘宸宇
- 所属文件夹：`modules/module_01_data_preprocess_coord/`
- 当前完成状态：已完成

---

## 二、模块功能说明

读取轨道、姿态、成像时刻等原始数据，统一时间、单位和数据结构，完成 J2000 到 ECEF 坐标转换。

---

## 三、代码文件说明

| 文件名 | 作用 |
|---|---|
| `data_preprocess.py` | 数据读取与预处理 |
| `coord_transform.py` | 坐标转换 |
| `__init__.py` | 包标识文件 |
---

## 四、主要函数说明

### 函数 1

函数名：`timecode_to_datetime_str`\
输入参数：`timecode`, `reference_timecode`, `reference_datetime_str`\
输出结果：`datetime_str`\
调用方式：

```python
from modules.module_01_data_preprocess_coord.code.data_preprocess import timecode_to_datetime_str

datetime_str = timecode_to_datetime_str(timecode, reference_timecode, reference_datetime_str)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `timecode` | float | 待转换的时间代码 |
| `reference_timecode` | float | 参考时间代码 |
| `reference_datetime_str` | str | 参考 UTC 时间字符串 | 格式："%Y %m %d %H:%M:%S.%f" |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `datetime_str` | str | 转换后的 UTC 时间字符串 | 格式："%Y %m %d %H:%M:%S.%f" |
---

### 函数2

函数名：`load_raw_data`\
输入参数：`orbit_path`, `attitude_path`, `imaging_time_path`\
输出结果：`(orbit_data, attitude_data, imaging_time_data)`\
调用方式：

```python
from modules.module_01_data_preprocess_coord.code.data_preprocess import load_raw_data

orbit_data, attitude_data, imaging_time_data = load_raw_data(orbit_path, attitude_path, imaging_time_path)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `orbit_path` | str | 离散轨道数据文件路径 | TXT 格式 |
| `attitude_path` | str | 离散姿态数据文件路径 | TXT 格式 |
| `imaging_time_path` | str | 扫描行成像时刻文件路径 | TXT 格式 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `orbit_data` | numpy structured array | 轨道数据 | 包含 orbit_time, orbit_datetime_str, satellite_position(3), satellite_velocity(3) |
| `attitude_data` | numpy structured array | 姿态数据 | 包含 attitude_time, attitude_datetime_str, euler(3), quaternion(4) |
| `imaging_time_data` | numpy structured array | 成像时刻数据 | 包含 rel_line, imaging_time, imaging_datetime_str |
---

### 函数3

函数名：`j2000_to_ecef`\
输入参数：`position_j2000`, `imaging_time`\
输出结果：`position_ecef`\
调用方式：

```python
from modules.module_01_data_preprocess_coord.code.coord_transform import j2000_to_ecef

position_ecef = j2000_to_ecef(position_j2000, imaging_time)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `position_j2000` | list or numpy array | J2000 坐标系下的位置向量 | 形如 [x_j2000, y_j2000, z_j2000] |
| `imaging_time` | float | 成像时刻的时间代码 | 

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `position_ecef` | numpy array | 地心地固坐标系下的位置向量 | 形如 [x_ecef, y_ecef, z_ecef] |
---

### 函数4

函数名：`save_preprocessed_data`\
输入参数：`preprocessed_data`, `output_path`\
输出结果：无（保存文件）\
调用方式：

```python
from modules.module_01_data_preprocess_coord.code.data_preprocess import save_preprocessed_data

save_preprocessed_data(preprocessed_data, output_path)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `preprocessed_data` | tuple | 预处理后的数据 | 即 load_raw_data 返回的 (orbit_data, attitude_data, imaging_time_data) |
| output_path | str | 输出目录路径 | 

输出说明：无返回值，直接保存 CSV 文件。

### 函数5

函数名：`datetime_to_jd`\
输入参数：`datetime_str`\
输出结果：`JD`\
调用方式：

```python
from modules.module_01_data_preprocess_coord.code.coord_transform import datetime_to_jd

JD = datetime_to_jd(datetime_str)
```

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `datetime_str` | str | UTC 时间字符串 | 格式："%Y %m %d %H:%M:%S.%f" |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
| `JD` | float | 儒略日 |
---

## 五、在 main.py 中的调用方式说明

```python
from modules.module_01_data_preprocess_coord.code.data_preprocess import load_raw_data, save_preprocessed_data
from modules.module_01_data_preprocess_coord.code.coord_transform import j2000_to_ecef
# 数据预处理
orbit_data, attitude_data, imaging_time_data = load_raw_data(orbit_path, attitude_path, imaging_time_path)
preprocessed_data = (orbit_data, attitude_data, imaging_time_data)
save_preprocessed_data(preprocessed_data, output_path)

# 坐标转换（示例：对轨道数据进行 J2000 -> ECEF 转换）
for pos, t in zip(orbit_data['satellite_position'], orbit_data['orbit_time']):
    ecef_pos = j2000_to_ecef(pos, t)
```

---

## 六、输入文件说明

| 输入文件名 | 文件格式 | 字段说明 |
|---|---|---|
| `orbit_sample.txt` | TXT | 摘自原数据文件 |
| `attitude_sample.txt` | TXT | 摘自原数据文件 |
| `imaging_time_sample.txt` | TXT | 摘自原数据文件 |
---

## 七、输出文件说明

| 输出文件名 | 文件格式 | 字段说明 |
|---|---|---|
| `preprocessed_orbit_sample.csv` | CSV | time, X, Y, Z, Vx, Vy, Vz |
| `preprocessed_attitude_sample.csv` | CSV | time,q0,q1,q2,q3 |
| `preprocessed_imaging_time_sample.csv` | CSV | time |
| `ecef_result_sample.csv` | CSV | time,x_ecef,y_ecef,z_ecef |

---

## 八、测试数据说明

- 测试输入数据位置：`test_data/input_sample/`
- 测试输出数据位置：`test_data/output_sample/`
- 是否可以单独运行：是
- 测试结果是否正常：是

单独运行方式：

```bash
# 先运行数据预处理
python modules/module_01_data_preprocess_coord/code/data_preprocess.py

# 再运行坐标转换
python modules/module_01_data_preprocess_coord/code/coord_transform.py
```

---

## 九、额外变量说明

| 变量名 | 含义 | 备注 |
|---|---|---|
| `reference_timecode` | 参考时间代码（轨道数据第一个时刻） | 用于 timecode 到 datetime 转换 |
| `reference_datetime_str` | 参考 UTC 时间字符串（轨道数据第一个时刻） | 用于 timecode 到 datetime 转换 |
| `W` | GMST 对应的旋转角（弧度） | 用于 J2000 到 ECEF 转换 |
| `delta_psi / delta_eps` | 黄经章动 / 交角章动（弧度） | 用于 J2000 到 ECEF 转换 |
| `L`,`Lp`,`Omega`,`F` | 章动参数（弧度） | 用于计算章动效应 |
| `eps_mean / eps_true` | 平黄赤交角 / 真黄赤交角（弧度） | 用于 J2000 到 ECEF 转换 |
| `gmst_seconds` | 格林尼治恒星时（秒） | 用于计算 GMST 旋转角 |
| `T` | 儒略世纪数 | 从 J2000.0 起算的世纪数，用于天文计算 |
| `JD` | 儒略日 | 由 datetime_to_jd 函数计算得到 |
| `reference_datetime` | 参考 datetime 对象 | datetime.strptime 解析后的结果 |
| `ecef_list` | ECEF 坐标列表 | 临时存储多个点的 ECEF 转换结果 |