# -*- coding: utf-8 -*-
"""
真实数据接入演示脚本（仅供模块05对接验证用，非模块05核心代码）。

功能：
  1. 解析老师提供的 ZY-3 NAD 仿真原始数据
       - gps.txt           (轨道，WGS84/ECEF)
       - att.txt           (姿态，J2000 四元数)
       - imagingTime.txt   (扫描行成像时刻)
       - cbr               (相机指向角查找表)
  2. 抽取小样本，生成模块05可直接吃的 CSV，字段与
     test_data/input_sample/ 完全一致；
  3. 跑一遍 inverse_projection 和 control_grid，证明流程通畅。

注意：J2000 -> ECEF 坐标变换属于模块01工作；姿态矩阵的精确解
属于模块03工作。本脚本中 rotation_matrix_real_sample.csv 仅
用基于 GPS 卫星位置构造的"近似星下视"占位矩阵代替，等模块
01 + 03 完成后必须替换。
"""

import os
import re
import sys
import numpy as np
import pandas as pd

# 让本脚本可以 import 上层 code/ 中的模块
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..', 'code'))
sys.path.insert(0, CODE_DIR)
from inverse_projection import inverse_projection
from control_grid import generate_control_grid, generate_rpc_sample

EARTH_RADIUS_M = 6378137.0

# 默认数据路径——把老师给的原始数据放到 raw_data/ 下，或修改 RAW_DIR
RAW_DIR = os.path.join(THIS_DIR, 'raw_data')
OUTPUT_DIR = os.path.join(THIS_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

GPS_FILE = 'DX_ZY3_NAD_gps.txt'
ATT_FILE = 'DX_ZY3_NAD_att.txt'
IMG_TIME_FILE = 'DX_ZY3_NAD_imagingTime.txt'
CBR_FILE = 'NAD.cbr'


# -------------------- 解析函数 --------------------
def parse_gps(path):
    text = open(path, encoding='utf-8', errors='ignore').read()
    blocks = re.findall(r'gpsData_\d+\s*=\s*\{([^}]*)\}', text)
    rows = []
    for block in blocks:
        d = dict(re.findall(r'(\w+)\s*=\s*([-+0-9.eE]+)\s*;', block))
        rows.append([
            float(d['timeCode']),
            float(d['PX']), float(d['PY']), float(d['PZ']),
            float(d['VX']), float(d['VY']), float(d['VZ']),
        ])
    return pd.DataFrame(rows, columns=['scan_time', 'X', 'Y', 'Z', 'VX', 'VY', 'VZ'])


def parse_att(path):
    text = open(path, encoding='utf-8', errors='ignore').read()
    blocks = re.findall(r'attData_\d+\s*=\s*\{([^}]*)\}', text)
    rows = []
    for block in blocks:
        d = dict(re.findall(r'(\w+)\s*=\s*([-+0-9.eE]+)\s*;', block))
        rows.append([
            float(d['timeCode']),
            float(d['q1']), float(d['q2']), float(d['q3']), float(d['q4']),
        ])
    return pd.DataFrame(rows, columns=['scan_time', 'q1', 'q2', 'q3', 'q4'])


def parse_imaging_time(path):
    df = pd.read_csv(path, sep=r'\s+', engine='python')
    return df.rename(columns={'RelLine': 'row', 'Time': 'scan_time'})


def parse_cbr(path):
    with open(path) as f:
        n_col = int(f.readline().strip())
        rows = []
        for _ in range(n_col):
            parts = f.readline().split()
            rows.append([int(parts[0]), float(parts[1]), float(parts[2])])
    return pd.DataFrame(rows, columns=['col', 'psi_x', 'psi_y'])


# -------------------- 占位旋转矩阵 --------------------
def build_placeholder_rotation_matrix(sat_position, lon_rad):
    """
    用卫星位置构造"星下视"占位旋转矩阵（相机系→ECEF）：
      相机 z 轴 = 卫星到地心方向；
      相机 x 轴 ≈ 东向；y 轴 ≈ 北向。
    仅用于在模块01+03完成前能跑通 inverse_projection。
    """
    nadir = -sat_position / np.linalg.norm(sat_position)
    east = np.array([-np.sin(lon_rad), np.cos(lon_rad), 0.0])
    north = np.cross(nadir, east)
    north = north / np.linalg.norm(north)
    east = np.cross(north, nadir)
    east = east / np.linalg.norm(east)
    return np.column_stack([east, north, nadir])


def main():
    print('=== 1. 解析原始数据 ===')
    gps_df = parse_gps(os.path.join(RAW_DIR, GPS_FILE))
    att_df = parse_att(os.path.join(RAW_DIR, ATT_FILE))
    img_time_df = parse_imaging_time(os.path.join(RAW_DIR, IMG_TIME_FILE))
    cbr_df = parse_cbr(os.path.join(RAW_DIR, CBR_FILE))
    print(f'  GPS: {len(gps_df)} 组 / ATT: {len(att_df)} 组 '
          f'/ imagingTime: {len(img_time_df)} 行 / cbr: {len(cbr_df)} 列')

    # =========== 抽样行号 ===========
    n_image_row = len(img_time_df)
    n_image_col = len(cbr_df)
    sample_rows = np.linspace(0, n_image_row - 1, 5, dtype=int)
    sample_cols = np.linspace(0, n_image_col - 1, 5, dtype=int)

    # =========== 模块02输出占位：把 GPS 线性内插到抽样行的 scan_time ===========
    # 注意：正式版本应由模块02用拉格朗日/三次样条插值
    sample_scan_time = img_time_df.loc[sample_rows, 'scan_time'].values
    orbit_sample_records = []
    for r, t in zip(sample_rows, sample_scan_time):
        x = np.interp(t, gps_df['scan_time'], gps_df['X'])
        y = np.interp(t, gps_df['scan_time'], gps_df['Y'])
        z = np.interp(t, gps_df['scan_time'], gps_df['Z'])
        orbit_sample_records.append([t, x, y, z])
    orbit_real_df = pd.DataFrame(
        orbit_sample_records, columns=['scan_time', 'X', 'Y', 'Z'])
    orbit_real_df.to_csv(
        os.path.join(OUTPUT_DIR, 'orbit_interp_result_sample.csv'),
        index=False)

    # =========== 模块03输出占位：用 GPS 位置构造星下视旋转矩阵 ===========
    # 注意：正式版本应由模块01 J2000->ECEF + 模块03 四元数内插联合输出
    rotation_records = []
    for r, t in zip(sample_rows, sample_scan_time):
        sat = np.array([
            np.interp(t, gps_df['scan_time'], gps_df['X']),
            np.interp(t, gps_df['scan_time'], gps_df['Y']),
            np.interp(t, gps_df['scan_time'], gps_df['Z']),
        ])
        lon_rad = np.arctan2(sat[1], sat[0])
        R = build_placeholder_rotation_matrix(sat, lon_rad)
        rotation_records.append([
            t,
            R[0, 0], R[0, 1], R[0, 2],
            R[1, 0], R[1, 1], R[1, 2],
            R[2, 0], R[2, 1], R[2, 2],
        ])
    rotation_real_df = pd.DataFrame(
        rotation_records,
        columns=['scan_time', 'R11', 'R12', 'R13',
                 'R21', 'R22', 'R23', 'R31', 'R32', 'R33'])
    rotation_real_df.to_csv(
        os.path.join(OUTPUT_DIR, 'rotation_matrix_result_sample.csv'),
        index=False)

    # =========== 指向角直接抽样 ===========
    camera_real_df = cbr_df.iloc[sample_cols].reset_index(drop=True)
    camera_real_df.to_csv(
        os.path.join(OUTPUT_DIR, 'camera_angle_result_sample.csv'),
        index=False)

    # =========== 像点：对抽样行列做笛卡尔积 ===========
    points = []
    pid = 0
    for ridx, r in enumerate(sample_rows):
        for cidx, c in enumerate(sample_cols):
            # 这里 row 在 image_points 中应保持与模块05 inverse_projection
            # 中 orbit_df / rotation_df 的行索引一致（最近邻），所以这里
            # 写的是抽样后的索引 ridx，而不是真实 5378 中的 r
            points.append([pid, ridx, cidx])
            pid += 1
    image_points_df = pd.DataFrame(points, columns=['point_id', 'row', 'col'])
    image_points_df.to_csv(
        os.path.join(OUTPUT_DIR, 'image_points_sample.csv'), index=False)

    # 同时保存"真实行列号"映射，方便对照
    map_df = pd.DataFrame({
        'sample_row': np.arange(len(sample_rows)),
        'real_row': sample_rows,
        'real_scan_time': sample_scan_time,
    })
    map_df.to_csv(os.path.join(OUTPUT_DIR, 'row_index_map.csv'), index=False)
    map_col_df = pd.DataFrame({
        'sample_col': np.arange(len(sample_cols)),
        'real_col': sample_cols,
    })
    map_col_df.to_csv(os.path.join(OUTPUT_DIR, 'col_index_map.csv'), index=False)

    print('\n=== 2. 调用模块05 inverse_projection 验证 ===')
    inv_result = inverse_projection(
        image_points_df, orbit_real_df, rotation_real_df, camera_real_df,
        reference_height=0.0,
    )
    inv_result.to_csv(
        os.path.join(OUTPUT_DIR, 'inverse_projection_result_sample.csv'),
        index=False)
    print(inv_result)

    print('\n=== 3. 调用模块05 generate_control_grid ===')
    # 测区取真实参考 RPC 给定范围内
    grid = generate_control_grid(
        lon_range=(114.65, 114.85),
        lat_range=(35.83, 35.93),
        height_range=(0.0, 8000.0),
        lon_step=0.05,
        lat_step=0.05,
        height_step=2000.0,
    )
    grid.to_csv(os.path.join(OUTPUT_DIR, 'control_grid_sample.csv'), index=False)
    print(f'  生成 {len(grid)} 个控制点')
    print(grid.head())


if __name__ == '__main__':
    main()
