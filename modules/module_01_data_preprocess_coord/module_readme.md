# 模块说明文档

## 一、模块基本信息

- 模块编号：01
- 模块名称：数据读取、预处理与坐标系转换
- 负责人：刘宸宇
- 所属文件夹：modules/module_01_data_preprocess_coord/
- 当前完成状态：未测试

---

## 二、模块功能说明

读取轨道、姿态、成像时刻等原始数据，统一时间、单位和数据结构，完成 J2000 到 ECEF 坐标转换。

---

## 三、代码文件说明

| 文件名 | 作用 |
|---|---|
|data_preprocess.py |数据读取与预处理|
|coord_transform.py |坐标转换|
---

## 四、主要函数说明

### 函数 1

函数名：timecode_to_datetime_str\
输入参数：timecode, reference_timecode, reference_datetime_str\
输出结果：datetime_str\
调用方式：

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
|timecode|
|reference_timecode|
|reference_datetime_str|
输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
|datetime_str|
---

### 函数2

函数名：\
输入参数：\
输出结果：\
调用方式：

参数说明：

| 参数名 | 类型 | 含义 | 备注 |
|---|---|---|---|
输出说明：

| 输出字段 | 类型 | 含义 | 备注 |
|---|---|---|---|
---

## 五、在 main.py 中的调用方式说明

from modules.module_01_data_preprocess_coord.code.data_preprocess.py import loadrawdata

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
