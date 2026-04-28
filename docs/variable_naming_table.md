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
