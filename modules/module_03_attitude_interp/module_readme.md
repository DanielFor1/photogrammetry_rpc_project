# 模块说明文档

## 一、模块基本信息

- 模块编号：03
- 模块名称：姿态内插与指向角处理模块
- 负责人：陈思彤
- 所属文件夹：modules/module_03_attitude_interp/
- 当前完成状态：已完成

---

## 二、模块功能说明

本模块主要实现以下功能：
1. 读取离散姿态四元数数据
2. 使用球面线性插值(SLERP)内插每个扫描行时刻的姿态
3. 处理相机指向角查找表，建立列号到指向角的映射
4. 将四元数转换为旋转矩阵

---

## 三、代码文件说明

| 文件名 | 作用 |
|---|---|
| attitude_interp.py | 姿态内插与指向角处理主代码 |
---

## 四、主要函数说明

### 函数1：slerp

- 函数名：slerp(q0, q1, t)
- 输入参数：起始四元数、结束四元数、插值系数
- 输出结果：插值后的单位四元数
- 调用方式：内部调用，用户一般不直接调用

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|--------|------|------|------|
| q0 | np.ndarray | 起始四元数 [q0,q1,q2,q3] | q0为实部 |
| q1 | np.ndarray | 结束四元数 [q0,q1,q2,q3] | q0为实部 |
| t | float | 插值系数 | 范围 [0,1] |

### 函数2：interpolate_attitude

- 函数名：interpolate_attitude(attitude_data, imaging_time_data)
- 输入参数：离散姿态DataFrame、扫描行时间DataFrame
- 输出结果：插值后的姿态四元数DataFrame
- 调用方式：from attitude_interp import interpolate_attitude

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|--------|------|------|------|
| attitude_data | pd.DataFrame | 离散姿态数据 | 字段：time,q0,q1,q2,q3 |
| imaging_time_data | pd.DataFrame | 扫描行时间 | 字段：time |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|----------|------|------|------|
| time | float | 扫描行时刻 | |
| q0 | float | 四元数实部 | |
| q1 | float | 四元数x分量 | |
| q2 | float | 四元数y分量 | |
| q3 | float | 四元数z分量 | |

### 函数3：process_camera_look_angle

- 函数名：process_camera_look_angle(look_angle_table)
- 输入参数：指向角查找表DataFrame
- 输出结果：tan值DataFrame
- 调用方式：from attitude_interp import process_camera_look_angle

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|--------|------|------|------|
| look_angle_table | pd.DataFrame | 指向角查找表 | 字段：col,psi_x,psi_y |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|----------|------|------|------|
| col | int | CCD探元列号 | |
| tan_psi_x | float | tan(垂轨指向角) | |
| tan_psi_y | float | tan(沿轨指向角) | |

### 函数4：build_rotation_matrix

- 函数名：build_rotation_matrix(quaternion, camera_angle_result=None)
- 输入参数：四元数DataFrame
- 输出结果：旋转矩阵DataFrame
- 调用方式：from attitude_interp import build_rotation_matrix

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|--------|------|------|------|
| quaternion | pd.DataFrame | 四元数数据 | 字段：time,q0,q1,q2,q3 |
| camera_angle_result | pd.DataFrame | 指向角结果 | 可选，本函数未使用 |

输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|----------|------|------|------|
| time | float | 扫描行时刻 | |
| r11 | float | 旋转矩阵第1行第1列 | |
| r12 | float | 旋转矩阵第1行第2列 | |
| r13 | float | 旋转矩阵第1行第3列 | |
| r21 | float | 旋转矩阵第2行第1列 | |
| r22 | float | 旋转矩阵第2行第2列 | |
| r23 | float | 旋转矩阵第2行第3列 | |
| r31 | float | 旋转矩阵第3行第1列 | |
| r32 | float | 旋转矩阵第3行第2列 | |
| r33 | float | 旋转矩阵第3行第3列 | |

---

## 五、在 main.py 中的调用方式说明


from modules.module_03_attitude_interp.code.attitude_interp import (
    interpolate_attitude,
    process_camera_look_angle,
    build_rotation_matrix
)

# 读取1号同学预处理后的数据
attitude_data = pd.read_csv("data/processed/preprocessed_attitude_sample.csv")
imaging_time_data = pd.read_csv("data/processed/preprocessed_imaging_time_sample.csv")
look_angle_table = pd.read_csv("data/sample/look_angle_table_sample.csv")

# 调用函数
attitude_result = interpolate_attitude(attitude_data, imaging_time_data)
camera_result = process_camera_look_angle(look_angle_table)
rotation_result = build_rotation_matrix(attitude_result)

# 保存结果
attitude_result.to_csv("data/processed/attitude_interp_result_sample.csv", index=False)
camera_result.to_csv("data/processed/camera_angle_result_sample.csv", index=False)
rotation_result.to_csv("data/processed/rotation_matrix_result_sample.csv", index=False)

---

## 六、输入文件说明

| 输入文件名 | 文件格式 | 字段说明 |
|------------|----------|----------|
| preprocessed_attitude_sample.csv | CSV | time, q0, q1, q2, q3 |
| preprocessed_imaging_time_sample.csv | CSV | time |
| look_angle_table_sample.csv | CSV | col, psi_x, psi_y |

---

## 七、输出文件说明

| 输出文件名 | 文件格式 | 字段说明 |
|---|---|---|
| attitude_interp_result_sample.csv | CSV | time, q0, q1, q2, q3 |
| camera_angle_result_sample.csv | CSV | col, tan_psi_x, tan_psi_y |
| rotation_matrix_result_sample.csv | CSV | time, r11, r12, r13, r21, r22, r23, r31, r32, r33 |
---

## 八、测试数据说明

- 测试输入数据位置：test_data/input_sample/
- 测试输出数据位置：test_data/output_sample/
- 是否可以单独运行：是
- 测试结果是否正常：是

---

## 九、额外变量说明

无。

| 变量名 | 含义 | 备注 |
|---|---|---|
