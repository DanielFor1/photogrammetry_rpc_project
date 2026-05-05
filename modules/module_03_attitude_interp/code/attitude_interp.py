"""
模块03：姿态内插与指向角处理模块

功能：
1. 读取离散姿态四元数数据
2. 使用球面线性插值(SLERP)内插每个扫描行时刻的姿态
3. 处理相机指向角查找表，建立列号到指向角的映射
4. 将四元数转换为旋转矩阵

"""

import numpy as np
import pandas as pd


def slerp(q0: np.ndarray, q1: np.ndarray, t: float) -> np.ndarray:
    """
    球面线性插值（SLERP）

    参数：
        q0: 起始四元数 [q0, q1, q2, q3] (q0为实部w)
        q1: 结束四元数
        t: 插值系数，范围 [0, 1]

    返回：
        插值后的单位四元数
    """
    q0 = q0 / np.linalg.norm(q0)
    q1 = q1 / np.linalg.norm(q1)

    dot = np.dot(q0, q1)

    if dot < 0:
        q1 = -q1
        dot = -dot

    DOT_THRESHOLD = 0.9995

    if dot > DOT_THRESHOLD:
        result = (1 - t) * q0 + t * q1
    else:
        theta = np.arccos(dot)
        sin_theta = np.sin(theta)
        ratio0 = np.sin((1 - t) * theta) / sin_theta
        ratio1 = np.sin(t * theta) / sin_theta
        result = ratio0 * q0 + ratio1 * q1

    return result / np.linalg.norm(result)


def quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    """
    将四元数转换为旋转矩阵

    参数：
        q: 四元数 [q0, q1, q2, q3]，q0为实部(w)

    返回：
        3x3旋转矩阵
    """
    w, x, y, z = q[0], q[1], q[2], q[3]

    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z

    return np.array([
        [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
        [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
        [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)]
    ])


def interpolate_attitude(attitude_data, imaging_time_data):
    """
    计算各成像时刻的姿态四元数。

    参数：
        attitude_data: DataFrame，字段 time, q0, q1, q2, q3
        imaging_time_data: DataFrame，字段 time

    返回：
        attitude_interp_result: DataFrame，字段 time, q0, q1, q2, q3
    """
    att_times = attitude_data['time'].values
    att_quats = attitude_data[['q0', 'q1', 'q2', 'q3']].values
    scan_times = imaging_time_data['time'].values

    results = []

    for scan_time in scan_times:
        idx = np.searchsorted(att_times, scan_time)

        if idx == 0:
            q_interp = att_quats[0].copy()
        elif idx >= len(att_times):
            q_interp = att_quats[-1].copy()
        else:
            t0, t1 = att_times[idx - 1], att_times[idx]
            q0, q1 = att_quats[idx - 1], att_quats[idx]
            t_norm = (scan_time - t0) / (t1 - t0) if t1 > t0 else 0
            q_interp = slerp(q0, q1, t_norm)

        results.append([scan_time, q_interp[0], q_interp[1], q_interp[2], q_interp[3]])

    attitude_interp_result = pd.DataFrame(results, columns=['time', 'q0', 'q1', 'q2', 'q3'])
    return attitude_interp_result


def process_camera_look_angle(look_angle_table):
    """
    处理相机指向角查找表。

    参数：
        look_angle_table: DataFrame，字段 col, psi_x, psi_y

    返回：
        camera_angle_result: DataFrame，字段 col, tan_psi_x, tan_psi_y
    """
    result = look_angle_table.copy()
    result['tan_psi_x'] = np.tan(result['psi_x'])
    result['tan_psi_y'] = np.tan(result['psi_y'])

    camera_angle_result = result[['col', 'tan_psi_x', 'tan_psi_y']].copy()
    return camera_angle_result


def build_rotation_matrix(quaternion, camera_angle_result=None):
    """
    根据四元数生成旋转矩阵。

    参数：
        quaternion: DataFrame，字段 time, q0, q1, q2, q3
        camera_angle_result: 可选，本函数未使用（保持接口一致）

    返回：
        rotation_matrix: DataFrame，字段 time, r11, r12, r13, r21, r22, r23, r31, r32, r33
    """
    results = []

    for _, row in quaternion.iterrows():
        t = row['time']
        q = np.array([row['q0'], row['q1'], row['q2'], row['q3']])
        R = quaternion_to_rotation_matrix(q)

        results.append([
            t,
            R[0, 0], R[0, 1], R[0, 2],
            R[1, 0], R[1, 1], R[1, 2],
            R[2, 0], R[2, 1], R[2, 2]
        ])

    columns = ['time', 'r11', 'r12', 'r13', 'r21', 'r22', 'r23', 'r31', 'r32', 'r33']
    rotation_matrix = pd.DataFrame(results, columns=columns)
    return rotation_matrix


if __name__ == "__main__":
    print("模块 03：attitude_interp.py 单独测试入口")

    # 使用test_data中的测试数据
    attitude_data = pd.read_csv("../test_data/input_sample/input_attitude.csv")
    imaging_time_data = pd.read_csv("../test_data/input_sample/input_imaging_time.csv")
    look_angle_table = pd.read_csv("../test_data/input_sample/input_look_angle.csv")

    # 测试插值
    attitude_result = interpolate_attitude(attitude_data, imaging_time_data)
    attitude_result.to_csv("../test_data/output_sample/output_attitude.csv", index=False)

    # 测试指向角处理
    camera_result = process_camera_look_angle(look_angle_table)
    camera_result.to_csv("../test_data/output_sample/output_camera_angle.csv", index=False)

    # 测试旋转矩阵
    rotation_result = build_rotation_matrix(attitude_result)
    rotation_result.to_csv("../test_data/output_sample/output_rotation.csv", index=False)

    print("所有函数测试完成！")