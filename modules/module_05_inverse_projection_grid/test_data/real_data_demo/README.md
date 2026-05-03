# 真实数据接入演示

本目录提供把老师发的 ZY-3 NAD 仿真原始数据转换为模块05可吃 CSV 的演示，
**不属于模块05核心代码**，仅用于跨模块对接验证。

## 目录结构

```
real_data_demo/
├── extract_real_data.py   真实数据解析与抽样脚本
├── README.md              本文件
├── raw_data/              原始数据放置目录（不上传仓库，老师另发）
└── output/                小样本输出（已上传，方便组员查看字段格式）
```

## 使用方法

1. 把老师发的下列原始文件放到 `raw_data/`：

   - `1777736353810_DX_ZY3_NAD_gps.txt`         离散轨道（WGS84/ECEF）
   - `1777736353808_DX_ZY3_NAD_att.txt`         离散姿态（J2000，四元数）
   - `1777736353810_DX_ZY3_NAD_imagingTime.txt` 扫描行成像时刻
   - `1777736353811_NAD.cbr`                    相机指向角查找表

2. 运行：

   ```powershell
   cd modules/module_05_inverse_projection_grid/test_data/real_data_demo
   python extract_real_data.py
   ```

3. 在 `output/` 下会生成与 `test_data/input_sample/` 字段一致的 CSV，
   并立即调用模块05 `inverse_projection` 与 `generate_control_grid` 验证流程。

## 抽样规则

- 像点取 `np.linspace(0, 5377, 5)` 的 5 个扫描行 × `np.linspace(0, 8191, 5)` 的 5 个列号，共 25 个；
- 轨道与姿态在这 5 个扫描时刻上抽样；
- 指向角直接抽样 5 列。

抽样行/列与真实行列号的映射保存在 `row_index_map.csv` / `col_index_map.csv`，
方便组员对照影像查阅。

## 旋转矩阵占位说明

`extract_real_data.py` 中 `rotation_matrix_result_sample.csv` 用的是
基于 GPS 卫星位置构造的"近似星下视"占位矩阵（让相机 z 轴指向地心）。
它仅满足让模块05流程能跑通的最低要求，反投影结果与真实地面位置
有约 10 km 量级的偏差。

正式流程必须替换为：

- 模块01：J2000 → ECEF 坐标系转换矩阵；
- 模块03：四元数内插得到精确旋转矩阵。

替换后，反投影结果应精确落到 RPC 测区中心 (114.749°E, 35.879°N) 附近。

## 与参考 RPC 的关系

老师同时提供 `1777736353812_zy3_rpc.txt` 作为参考 RPC 模型，用于模块06
最终精度评定。其测区参数为：

- `LAT_OFF = 35.87926646°`，`LAT_SCALE = 0.07413620°`
- `LONG_OFF = 114.74877615°`，`LONG_SCALE = 0.11823258°`
- `HEIGHT_OFF = 4000 m`，`HEIGHT_SCALE = 4000 m`

控制格网应覆盖该范围（本仓库默认 lon 114.65~114.85, lat 35.83~35.93,
height 0~8000 m，可在 `main.py` 整合时按需调整）。
