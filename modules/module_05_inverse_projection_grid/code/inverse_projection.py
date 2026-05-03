# -*- coding: utf-8 -*-
"""
模块 05 —— 严格成像模型反投影模块
功能：将像点 (row, col) 反投影到地面点 (lon, lat, height)。

说明（学生作业版）：
    本版本是一个简化的占位实现，目的是让 RPC 解算的整体流程能够在
    模块 01–04 尚未全部完成的情况下先跑通，主要简化点如下：
        1. 地球用球面近似（半径 6378137 m），未使用 WGS84 椭球；
        2. 用 row 作为扫描时刻索引（最近邻），未做精确时间插值；
        3. 用 col 在指向角查找表中最近邻取值，未做线性插值；
        4. 视线与给定参考高程的等高球面相交（解一元二次方程），
           未做基于真实 DEM 或迭代逼近真实高程。
    后续如果要接入严格成像模型或迭代反投影，只需替换函数体，
    保持 inverse_projection 的输入输出接口与字段名不变即可。
"""

import os
import numpy as np
import pandas as pd

# 简化球面近似使用的地球半径（米）
EARTH_RADIUS_M = 6378137.0


def inverse_projection(
    image_points_df,
    orbit_df,
    rotation_df,
    camera_angle_df,
    reference_height=0.0,
):
    """
    像点反投影到地面点。

    Parameters
    ----------
    image_points_df : pandas.DataFrame
        像点数据，字段：point_id, row, col
    orbit_df : pandas.DataFrame
        各扫描时刻轨道参数，字段至少包含：
        scan_time, X, Y, Z（地心地固系，米）
    rotation_df : pandas.DataFrame
        各扫描时刻姿态旋转矩阵（相机系 -> ECEF），字段：
        scan_time, R11, R12, R13, R21, R22, R23, R31, R32, R33
    camera_angle_df : pandas.DataFrame
        相机指向角查找表，字段：col, psi_x, psi_y（弧度）
    reference_height : float, optional
        反投影时使用的参考高程（米），默认 0.0。

    Returns
    -------
    inverse_projection_result_df : pandas.DataFrame
        反投影结果，字段：point_id, lon, lat, height
    """
    n_orbit = len(orbit_df)
    n_camera = len(camera_angle_df)

    result_records = []
    for _, point in image_points_df.iterrows():
        point_id = point['point_id']
        row = float(point['row'])
        col = float(point['col'])

        # 1. 用 row 作为扫描时刻索引（最近邻）
        idx_orbit = int(np.clip(round(row), 0, n_orbit - 1))
        sat_position = np.array([
            orbit_df.iloc[idx_orbit]['X'],
            orbit_df.iloc[idx_orbit]['Y'],
            orbit_df.iloc[idx_orbit]['Z'],
        ])
        rotation_matrix = np.array([
            [rotation_df.iloc[idx_orbit]['R11'],
             rotation_df.iloc[idx_orbit]['R12'],
             rotation_df.iloc[idx_orbit]['R13']],
            [rotation_df.iloc[idx_orbit]['R21'],
             rotation_df.iloc[idx_orbit]['R22'],
             rotation_df.iloc[idx_orbit]['R23']],
            [rotation_df.iloc[idx_orbit]['R31'],
             rotation_df.iloc[idx_orbit]['R32'],
             rotation_df.iloc[idx_orbit]['R33']],
        ])

        # 2. 用 col 在指向角表中最近邻取值
        idx_camera = int(np.clip(round(col), 0, n_camera - 1))
        psi_x = float(camera_angle_df.iloc[idx_camera]['psi_x'])
        psi_y = float(camera_angle_df.iloc[idx_camera]['psi_y'])

        # 3. 相机系内的视线方向（沿 z 轴指向地面，由指向角决定 x、y 偏移）
        view_vector_camera = np.array([np.tan(psi_x), np.tan(psi_y), 1.0])
        view_vector_camera = view_vector_camera / np.linalg.norm(view_vector_camera)

        # 4. 用姿态矩阵把视线从相机系转到地心地固系
        view_vector_ecef = rotation_matrix @ view_vector_camera

        # 5. 视线与给定高程的球面相交：
        #    || sat_position + t * view_vector_ecef ||^2 = (R + h)^2
        target_radius = EARTH_RADIUS_M + reference_height
        a_coef = np.dot(view_vector_ecef, view_vector_ecef)
        b_coef = 2.0 * np.dot(sat_position, view_vector_ecef)
        c_coef = np.dot(sat_position, sat_position) - target_radius ** 2
        discriminant = b_coef * b_coef - 4.0 * a_coef * c_coef

        if discriminant < 0:
            # 视线与目标球面无交点，结果置空
            result_records.append([point_id, np.nan, np.nan, np.nan])
            continue

        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b_coef - sqrt_disc) / (2.0 * a_coef)
        t2 = (-b_coef + sqrt_disc) / (2.0 * a_coef)
        positive_t = [t for t in (t1, t2) if t > 0]
        if not positive_t:
            result_records.append([point_id, np.nan, np.nan, np.nan])
            continue
        # 取离卫星最近的正解（迎面相交点）
        t_min = min(positive_t)

        ground_point = sat_position + t_min * view_vector_ecef
        x_g, y_g, z_g = ground_point

        # 6. 球面近似：ECEF -> (lon, lat, height)
        radius = np.linalg.norm(ground_point)
        height = radius - EARTH_RADIUS_M
        lat = np.degrees(np.arcsin(z_g / radius))
        lon = np.degrees(np.arctan2(y_g, x_g))

        result_records.append([point_id, lon, lat, height])

    inverse_projection_result_df = pd.DataFrame(
        result_records,
        columns=['point_id', 'lon', 'lat', 'height'],
    )
    return inverse_projection_result_df


def main():
    """
    模块独立测试入口。
    在仓库根目录或本文件所在目录执行：
        python inverse_projection.py
    会自动从 ../test_data/input_sample/ 读小样本，
    把结果写到 ../test_data/output_sample/inverse_projection_result_sample.csv
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_input_dir = os.path.join(base_dir, '..', 'test_data', 'input_sample')
    test_output_dir = os.path.join(base_dir, '..', 'test_data', 'output_sample')
    os.makedirs(test_output_dir, exist_ok=True)

    image_points_path = os.path.join(test_input_dir, 'image_points_sample.csv')
    orbit_path = os.path.join(test_input_dir, 'orbit_interp_result_sample.csv')
    rotation_path = os.path.join(test_input_dir, 'rotation_matrix_result_sample.csv')
    camera_angle_path = os.path.join(test_input_dir, 'camera_angle_result_sample.csv')
    output_path = os.path.join(test_output_dir, 'inverse_projection_result_sample.csv')

    image_points_df = pd.read_csv(image_points_path)
    orbit_df = pd.read_csv(orbit_path)
    rotation_df = pd.read_csv(rotation_path)
    camera_angle_df = pd.read_csv(camera_angle_path)

    inverse_projection_result_df = inverse_projection(
        image_points_df,
        orbit_df,
        rotation_df,
        camera_angle_df,
        reference_height=0.0,
    )
    inverse_projection_result_df.to_csv(output_path, index=False)
    print(f'反投影结果已写入：{output_path}')
    print(inverse_projection_result_df)


if __name__ == '__main__':
    main()
