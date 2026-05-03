# -*- coding: utf-8 -*-
"""
模块 05 —— 物方控制格网与 RPC 样本点生成

包含两个对外函数：
    generate_control_grid : 在测区范围内生成三维分层控制格网
    generate_rpc_sample   : 将控制格网与正投影结果合并为 RPC 样本点

另外提供一个仅供本模块独立测试用的占位正投影函数
_placeholder_forward_projection。正式流程中应使用模块 04
forward_projection 的输出来替换它。
"""

import os
import numpy as np
import pandas as pd


def generate_control_grid(
    lon_range,
    lat_range,
    height_range,
    lon_step,
    lat_step,
    height_step,
):
    """
    根据测区经纬度范围与高程分层，生成物方控制格网。

    Parameters
    ----------
    lon_range : tuple of float
        (lon_min, lon_max)，单位：度
    lat_range : tuple of float
        (lat_min, lat_max)，单位：度
    height_range : tuple of float
        (height_min, height_max)，单位：米
    lon_step : float
        经度方向格网间距，单位：度
    lat_step : float
        纬度方向格网间距,单位：度
    height_step : float
        高程方向分层间距，单位：米

    Returns
    -------
    control_grid_df : pandas.DataFrame
        控制格网，字段：point_id, lon, lat, height
    """
    lon_array = np.arange(lon_range[0], lon_range[1] + 1e-9, lon_step)
    lat_array = np.arange(lat_range[0], lat_range[1] + 1e-9, lat_step)
    height_array = np.arange(height_range[0], height_range[1] + 1e-9, height_step)

    grid_records = []
    point_id = 0
    for h_value in height_array:
        for lat_value in lat_array:
            for lon_value in lon_array:
                grid_records.append([point_id, lon_value, lat_value, h_value])
                point_id += 1

    control_grid_df = pd.DataFrame(
        grid_records,
        columns=['point_id', 'lon', 'lat', 'height'],
    )
    return control_grid_df


def generate_rpc_sample(control_grid_df, forward_projection_result_df):
    """
    将控制格网（物方）与正投影结果（像方）合并为 RPC 样本点。

    Parameters
    ----------
    control_grid_df : pandas.DataFrame
        控制格网，字段：point_id, lon, lat, height
    forward_projection_result_df : pandas.DataFrame
        正投影结果（来自模块 04 或占位投影），字段：point_id, row, col

    Returns
    -------
    rpc_sample_points_df : pandas.DataFrame
        RPC 样本点，字段：point_id, lon, lat, height, row, col
    """
    rpc_sample_points_df = pd.merge(
        control_grid_df,
        forward_projection_result_df,
        on='point_id',
        how='inner',
    )
    rpc_sample_points_df = rpc_sample_points_df[
        ['point_id', 'lon', 'lat', 'height', 'row', 'col']
    ].reset_index(drop=True)
    return rpc_sample_points_df


def _placeholder_forward_projection(
    control_grid_df,
    lon_center,
    lat_center,
    lon_pixel_scale=1e5,
    lat_pixel_scale=1e5,
    row_offset=0,
    col_offset=0,
):
    """
    占位的正投影实现（仅用于本模块独立测试）。
    使用经纬度相对中心点的线性映射近似得到像点 (row, col)。
    正式流程请用模块 04 的 forward_projection 输出替换。
    """
    rows = ((control_grid_df['lat'] - lat_center) * lat_pixel_scale + row_offset).round().astype(int)
    cols = ((control_grid_df['lon'] - lon_center) * lon_pixel_scale + col_offset).round().astype(int)
    forward_projection_result_df = pd.DataFrame({
        'point_id': control_grid_df['point_id'].values,
        'row': rows.values,
        'col': cols.values,
    })
    return forward_projection_result_df


def main():
    """
    模块独立测试入口。
    在本文件所在目录执行：
        python control_grid.py
    会生成控制格网和 RPC 样本点示例文件到 ../test_data/output_sample/
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_dir = os.path.join(base_dir, '..', 'test_data', 'output_sample')
    os.makedirs(test_output_dir, exist_ok=True)

    # 1. 生成控制格网（与真实数据 RPC 测区一致：河南安阳附近）
    # 测区中心 (114.749°E, 35.879°N)，高程基准 4000 m
    lon_range = (114.65, 114.85)
    lat_range = (35.83, 35.93)
    height_range = (0.0, 8000.0)
    lon_step = 0.05
    lat_step = 0.05
    height_step = 2000.0

    control_grid_df = generate_control_grid(
        lon_range, lat_range, height_range,
        lon_step, lat_step, height_step,
    )
    grid_output_path = os.path.join(test_output_dir, 'control_grid_sample.csv')
    control_grid_df.to_csv(grid_output_path, index=False)
    print(f'控制格网已写入：{grid_output_path}')
    print(control_grid_df.head())

    # 2. 占位正投影（仅用于独立测试，正式流程由模块 04 提供）
    # 用真实参考 RPC 测区中心和 LINE_OFF/SAMP_OFF 作为线性映射基点
    forward_projection_result_df = _placeholder_forward_projection(
        control_grid_df,
        lon_center=114.749,
        lat_center=35.879,
        lon_pixel_scale=3.12e4,   # 经度方向像素/度（粗略估计）
        lat_pixel_scale=3.27e4,   # 纬度方向像素/度（粗略估计）
        row_offset=2421,
        col_offset=3690,
    )

    # 3. 合并生成 RPC 样本点
    rpc_sample_points_df = generate_rpc_sample(
        control_grid_df,
        forward_projection_result_df,
    )
    rpc_output_path = os.path.join(test_output_dir, 'rpc_sample_points_sample.csv')
    rpc_sample_points_df.to_csv(rpc_output_path, index=False)
    print(f'RPC 样本点已写入：{rpc_output_path}')
    print(rpc_sample_points_df.head())


if __name__ == '__main__':
    main()
