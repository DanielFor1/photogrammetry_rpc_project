"""
coord_transform.py

坐标转换模块。
"""

import re
import numpy as np
import os
import pandas as pd
from data_preprocess import timecode_to_datetime_str

def Rx(theta):
    """
    绕 X 轴旋转矩阵（右手定则）
    
    参数：
        theta: 旋转角度

    返回：
        3x3 旋转矩阵
    """

    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [1,  0,  0],
        [0,  c,  s],
        [0, -s,  c]
    ])


def Rz(theta):
    """
    绕 Z 轴旋转矩阵（右手定则）

    参数：
        theta: 旋转角度

    返回：
        3x3 旋转矩阵
    """

    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [ c, s, 0],
        [-s, c, 0],
        [ 0, 0, 1]
    ])

def datetime_to_jd(datetime_str):
    """
    由 UTC 时间字符串计算儒略日

    参数：
        datetime_str: UTC 时间字符串

    返回：
        JD: 儒略日
    """

    normalized = " ".join(datetime_str.strip().split())
    m = re.match(
        r"(\d{4})\s+(\d{2})\s+(\d{2})\s+(\d{1,2})\s*:\s*(\d{2})\s*:\s*(\d{1,2})\.(\d+)",
        normalized,
    )
    if not m:
        raise ValueError(f"无法解析时间: {datetime_str!r}")
    year, month, day, hour, minute, second, microsec = m.groups()
    y, mo, d = int(year), int(month), int(day)
    frac_day = (int(hour) + int(minute) / 60.0
                + (int(second) + int(microsec[:6].ljust(6, "0")) / 1e6) / 3600.0) / 24.0

    if mo <= 2:
        y -= 1
        mo += 12
    A = int(y / 100)
    B = 2 - A + int(A / 4)
    JD = int(365.25 * (y + 4716)) + int(30.6001 * (mo + 1)) + d + frac_day + B - 1524.5
    return JD

def j2000_to_ecef(position_j2000, imaging_time):
    """
    将 J2000 坐标转换为地心地固坐标。

    参数：
        position_j2000: J2000 坐标向量 [x_j2000, y_j2000, z_j2000]
        imaging_time: 成像时刻

    返回：
        position_ecef: 地心地固坐标向量 [x_ecef, y_ecef, z_ecef]
    """

    reference_timecode = 131862356.0000000000
    reference_datetime_str = "2013 03 07 04:25:56.000000"
    imaging_datetime_str = timecode_to_datetime_str(imaging_time, reference_timecode, reference_datetime_str)

    # 将 UTC 时间字符串转换为儒略日
    JD = datetime_to_jd(imaging_datetime_str)

    T = (JD - 2451545.0) / 36525.0

    # 章动参数
    L = np.radians(134.96340251 + (1717915923.2178 * T + 31.8792 * T**2 + 0.051635 * T**3 - 0.00024470 * T**4) / 3600.0)

    Lp = np.radians(357.52910918 + (129596581.0481 * T - 0.5532 * T**2 + 0.000136 * T**3 - 0.00001149 * T**4) / 3600.0)
    
    Omega = np.radians(125.04455501 + (6962890.2665 * T - 7.4722 * T**2 + 0.007702 * T**3 - 0.00005939 * T**4) / 3600.0)
    
    F = np.radians(93.27209062 + (1739527262.8478 * T - 12.7512 * T**2 - 0.001037 * T**3 + 0.00000417 * T**4) / 3600.0)
    
    eps_mean = np.radians(23.439291 - 0.0130042 * T - 1.64e-7 * T**2 + 5.04e-7 * T**3)
    
    # 黄经章动 Δψ 和交角章动 Δε
    delta_psi = np.radians((-17.200 * np.sin(Omega)
         - 1.319 * np.sin(-2*F + 2*Omega + 2*L)
         - 0.227 * np.sin(2*L)
         + 0.206 * np.sin(2*Omega)
         + 0.143 * np.sin(Lp)) / 3600.0
    )
    
    delta_eps = np.radians(
        (9.203 * np.cos(Omega)
         + 0.574 * np.cos(-2*F + 2*Omega + 2*L)
         + 0.098 * np.cos(2*L)
         - 0.090 * np.cos(2*Omega)) / 3600.0
    )

    eps_true = eps_mean + delta_eps

    # GMST 计算
    gmst_seconds = (67310.54841 + (876600.0 * 3600.0 + 8640184.812866) * T + 0.093104 * T**2 - 6.2e-6 * T**3)
    
    # 将 GMST 转换为弧度
    W = np.radians((gmst_seconds / 240.0) % 360.0)

    # 计算从 J2000 到 ECEF 的旋转矩阵
    rotation_matrix = Rz(W) @ Rx(-eps_true) @ Rz(-delta_psi) @ Rx(eps_mean)

    position_ecef = rotation_matrix @ position_j2000
    return position_ecef


if __name__ == "__main__":
    print("模块 01：coord_transform.py 单独测试入口")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_input_dir = os.path.join(base_dir, '..', 'test_data', 'output_sample')
    test_output_dir = os.path.join(base_dir, '..', 'test_data', 'output_sample')
    os.makedirs(test_output_dir, exist_ok=True)

    df = pd.read_csv(os.path.join(test_input_dir, "preprocessed_orbit_sample.csv"))
    imaging_time = df['time'].values
    position_j2000 = df[['X', 'Y', 'Z']].values
    ecef_list = []
    for pos, t in zip(position_j2000, imaging_time):
        position_ecef = j2000_to_ecef(pos, t)
        ecef_list.append(position_ecef)
    position_ecef = np.array(ecef_list)
    x_ecef = position_ecef[:, 0]
    y_ecef = position_ecef[:, 1]
    z_ecef = position_ecef[:, 2]
    ecef_result_matrix = np.column_stack((imaging_time, x_ecef, y_ecef, z_ecef))
    ecef_header = "time,x_ecef,y_ecef,z_ecef"
    np.savetxt(os.path.join(test_output_dir, "ecef_result_sample.csv"), ecef_result_matrix, header=ecef_header, delimiter=",", comments="", fmt="%s")
    print("模块 01：coord_transform.py 单独测试完成，ECEF 坐标转换结果已保存到 output_sample 目录")