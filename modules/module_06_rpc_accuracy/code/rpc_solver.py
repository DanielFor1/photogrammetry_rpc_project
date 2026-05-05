"""
rpc_solver.py

RPC 参数解算模块。
根据模块 05 生成的 RPC 样本点 (lon, lat, height, row, col)，
建立有理多项式系数(RPC)最小二乘解算方程，求解归一化参数和 78 个多项式系数。
"""

import re
import numpy as np


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

def _compute_basis_matrix(norm_lon, norm_lat, norm_height):
    """计算 20 个三次齐次多项式基函数值

    RPC 模型使用归一化坐标 (P, L, H) 的三次齐次多项式展开，
    共 20 项（1 个常数 + 3 个一次 + 6 个二次 + 10 个三次）。

    参数:
        norm_lon:    归一化经度 (lon - LONG_OFF) / LONG_SCALE
        norm_lat:    归一化纬度 (lat - LAT_OFF)  / LAT_SCALE
        norm_height: 归一化高程 (height - HEIGHT_OFF) / HEIGHT_SCALE

    返回:
        basis_matrix: (N, 20) 基函数矩阵
    """
    n = len(norm_lon)
    basis_matrix = np.zeros((n, 20))

    L = norm_lon
    P = norm_lat
    H = norm_height

    # 常数项
    basis_matrix[:, 0]  = 1.0
    # 一次项: L, P, H
    basis_matrix[:, 1]  = L
    basis_matrix[:, 2]  = P
    basis_matrix[:, 3]  = H
    # 二次项: LP, LH, PH, L^2, P^2, H^2
    basis_matrix[:, 4]  = L * P
    basis_matrix[:, 5]  = L * H
    basis_matrix[:, 6]  = P * H
    basis_matrix[:, 7]  = L ** 2
    basis_matrix[:, 8]  = P ** 2
    basis_matrix[:, 9]  = H ** 2
    # 三次项: LPH, L^3, LP^2, LH^2, L^2P, P^3, PH^2, L^2H, P^2H, H^3
    basis_matrix[:, 10] = P * L * H
    basis_matrix[:, 11] = L ** 3
    basis_matrix[:, 12] = L * P ** 2
    basis_matrix[:, 13] = L * H ** 2
    basis_matrix[:, 14] = L ** 2 * P
    basis_matrix[:, 15] = P ** 3
    basis_matrix[:, 16] = P * H ** 2
    basis_matrix[:, 17] = L ** 2 * H
    basis_matrix[:, 18] = P ** 2 * H
    basis_matrix[:, 19] = H ** 3

    return basis_matrix


def _compute_normalization_params(lon_arr, lat_arr, height_arr, row_arr, col_arr):
    """从样本点分布计算 RPC 归一化参数

    使用均值作为 OFF，最大偏差作为 SCALE，
    确保归一化后坐标以零为中心、[-1, 1] 范围内，
    改善最小二乘法方程的数值条件。

    返回:
        rpc_params: dict，含 10 个归一化参数
    """
    lon_off = np.mean(lon_arr)
    lat_off = np.mean(lat_arr)
    height_off = np.mean(height_arr)
    row_off = np.mean(row_arr)
    col_off = np.mean(col_arr)

    return {
        'LONG_OFF': lon_off,
        'LONG_SCALE': np.max(np.abs(lon_arr - lon_off)),
        'LAT_OFF': lat_off,
        'LAT_SCALE': np.max(np.abs(lat_arr - lat_off)),
        'HEIGHT_OFF': height_off,
        'HEIGHT_SCALE': np.max(np.abs(height_arr - height_off)),
        'LINE_OFF': row_off,
        'LINE_SCALE': np.max(np.abs(row_arr - row_off)),
        'SAMP_OFF': col_off,
        'SAMP_SCALE': np.max(np.abs(col_arr - col_off)),
    }


def _solve_coefficients(norm_lon, norm_lat, norm_height,
                        norm_row, norm_col):
    """最小二乘求解 RPC 多项式系数

    RPC 正变换形式:
        r = NUM(P,L,H) / DEN(P,L,H)  -> 归一化行号
        c = NUM(P,L,H) / DEN(P,L,H)  -> 归一化列号

    线性化方法:
        NUM - r * DEN = 0
        展开后: [B | -r*B_{1:19}] * [num; den_{1:19}] = r * B_0
        其中 B_0=1 固定为分母首项，求解 39 个未知系数（20 个分子 + 19 个分母）。

    返回:
        rpc_coeffs: dict，含 LINE_NUM/DEN_COEFF 和 SAMP_NUM/DEN_COEFF
    """
    n = len(norm_lon)
    basis_matrix = _compute_basis_matrix(norm_lon, norm_lat, norm_height)

    # 行方向: 构建 design_matrix * x = observation_vector
    design_matrix_line = np.zeros((n, 39))
    design_matrix_line[:, :20] = basis_matrix
    design_matrix_line[:, 20:] = -norm_row[:, np.newaxis] * basis_matrix[:, 1:]
    observation_vector_line = norm_row * basis_matrix[:, 0]
    x_line, _, _, _ = np.linalg.lstsq(
        design_matrix_line, observation_vector_line, rcond=None
    )
    line_num_coeff = x_line[:20]
    line_den_coeff = np.concatenate([[1.0], x_line[20:]])

    # 列方向: 同理
    design_matrix_samp = np.zeros((n, 39))
    design_matrix_samp[:, :20] = basis_matrix
    design_matrix_samp[:, 20:] = -norm_col[:, np.newaxis] * basis_matrix[:, 1:]
    observation_vector_samp = norm_col * basis_matrix[:, 0]
    x_samp, _, _, _ = np.linalg.lstsq(
        design_matrix_samp, observation_vector_samp, rcond=None
    )
    samp_num_coeff = x_samp[:20]
    samp_den_coeff = np.concatenate([[1.0], x_samp[20:]])

    return {
        'LINE_NUM_COEFF': line_num_coeff,
        'LINE_DEN_COEFF': line_den_coeff,
        'SAMP_NUM_COEFF': samp_num_coeff,
        'SAMP_DEN_COEFF': samp_den_coeff,
    }


# ---------------------------------------------------------------------------
# 对外接口函数
# ---------------------------------------------------------------------------

def solve_rpc(rpc_sample_points):
    """根据 RPC 样本点建立解算方程并求解 RPC 参数

    流程:
      1. 从样本点数据中提取 lon, lat, height, row, col
      2. 计算归一化参数 (OFF / SCALE)
      3. 归一化地面坐标和像方坐标
      4. 构建线性化最小二乘方程，分别求解行、列方向系数
      5. 打印内符合精度 (RMSE)

    参数:
        rpc_sample_points: DataFrame 或 ndarray
            列: point_id, lon, lat, height, row, col

    返回:
        rpc_params: dict
            包含归一化参数 (LONG_OFF, LAT_OFF, HEIGHT_OFF, LINE_OFF, SAMP_OFF
            及对应 SCALE) 和多项式系数 (LINE_NUM_COEFF, LINE_DEN_COEFF,
            SAMP_NUM_COEFF, SAMP_DEN_COEFF)
    """
    # 解析输入数据
    data = np.array(rpc_sample_points)
    if data.ndim == 2 and data.shape[1] >= 6:
        lon_arr = data[:, 1].astype(float)
        lat_arr = data[:, 2].astype(float)
        height_arr = data[:, 3].astype(float)
        row_arr = data[:, 4].astype(float)
        col_arr = data[:, 5].astype(float)
    else:
        raise ValueError(
            "rpc_sample_points 需为 (N, 6) 数组，列为 "
            "point_id, lon, lat, height, row, col"
        )

    n_points = len(lon_arr)
    print(f"  样本点数量: {n_points}")

    # 计算归一化参数
    rpc_params = _compute_normalization_params(
        lon_arr, lat_arr, height_arr, row_arr, col_arr
    )
    print(f"  归一化参数: LINE_OFF={rpc_params['LINE_OFF']:.1f}, "
          f"LINE_SCALE={rpc_params['LINE_SCALE']:.1f}")
    print(f"              SAMP_OFF={rpc_params['SAMP_OFF']:.1f}, "
          f"SAMP_SCALE={rpc_params['SAMP_SCALE']:.1f}")

    # 归一化
    norm_lon = (lon_arr - rpc_params['LONG_OFF']) / rpc_params['LONG_SCALE']
    norm_lat = (lat_arr - rpc_params['LAT_OFF']) / rpc_params['LAT_SCALE']
    norm_height = (height_arr - rpc_params['HEIGHT_OFF']) / rpc_params['HEIGHT_SCALE']
    norm_row = (row_arr - rpc_params['LINE_OFF']) / rpc_params['LINE_SCALE']
    norm_col = (col_arr - rpc_params['SAMP_OFF']) / rpc_params['SAMP_SCALE']

    # 求解系数
    rpc_coeffs = _solve_coefficients(
        norm_lon, norm_lat, norm_height, norm_row, norm_col
    )
    rpc_params.update(rpc_coeffs)

    print(f"  LINE_NUM_COEFF 前 3 项: {rpc_coeffs['LINE_NUM_COEFF'][:3]}")
    print(f"  SAMP_NUM_COEFF 前 3 项: {rpc_coeffs['SAMP_NUM_COEFF'][:3]}")

    # 内符合精度快速检验
    residuals_row = []
    residuals_col = []
    for i in range(n_points):
        row_rpc, col_rpc = rpc_forward(
            lat_arr[i], lon_arr[i], height_arr[i], rpc_params
        )
        residuals_row.append(row_rpc - row_arr[i])
        residuals_col.append(col_rpc - col_arr[i])

    residuals_row = np.array(residuals_row)
    residuals_col = np.array(residuals_col)
    rmse_row = np.sqrt(np.mean(residuals_row ** 2))
    rmse_col = np.sqrt(np.mean(residuals_col ** 2))

    print(f"  内符合精度: RMSE_row = {rmse_row:.6f} 像素, "
          f"RMSE_col = {rmse_col:.6f} 像素")

    return rpc_params


def rpc_forward(lat, lon, height, rpc_params):
    """RPC 正变换: 大地坐标 -> 像方坐标 (row, col)

    将输入坐标归一化后，代入有理多项式计算归一化像坐标，再还原为像素坐标。

    参数:
        lat:        纬度 (度)
        lon:        经度 (度)
        height:     高程 (米)
        rpc_params: dict，含归一化参数和多项式系数

    返回:
        row: 像方行坐标
        col: 像方列坐标
    """
    # 归一化输入坐标
    norm_lat = (lat - rpc_params['LAT_OFF']) / rpc_params['LAT_SCALE']
    norm_lon = (lon - rpc_params['LONG_OFF']) / rpc_params['LONG_SCALE']
    norm_height = (height - rpc_params['HEIGHT_OFF']) / rpc_params['HEIGHT_SCALE']

    # 计算 20 项基函数值
    b = np.array([
        1.0,
        norm_lon, norm_lat, norm_height,
        norm_lon * norm_lat, norm_lon * norm_height, norm_lat * norm_height,
        norm_lon ** 2, norm_lat ** 2, norm_height ** 2,
        norm_lat * norm_lon * norm_height,
        norm_lon ** 3, norm_lon * norm_lat ** 2, norm_lon * norm_height ** 2,
        norm_lon ** 2 * norm_lat, norm_lat ** 3, norm_lat * norm_height ** 2,
        norm_lon ** 2 * norm_height, norm_lat ** 2 * norm_height,
        norm_height ** 3
    ])

    # r = NUM / DEN (归一化行号), c = NUM / DEN (归一化列号)
    r = (np.dot(rpc_params['LINE_NUM_COEFF'], b) /
         np.dot(rpc_params['LINE_DEN_COEFF'], b))
    c = (np.dot(rpc_params['SAMP_NUM_COEFF'], b) /
         np.dot(rpc_params['SAMP_DEN_COEFF'], b))

    # 还原为像素坐标
    row = r * rpc_params['LINE_SCALE'] + rpc_params['LINE_OFF']
    col = c * rpc_params['SAMP_SCALE'] + rpc_params['SAMP_OFF']

    return row, col


def save_rpc_result(rpc_params, output_path):
    """保存 RPC 参数结果到文本文件

    格式与标准 RPC 参数文件一致:
      - 10 个归一化参数 (OFF / SCALE)
      - 4 组各 20 个有理多项式系数

    参数:
        rpc_params:  dict，solve_rpc() 的返回值
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # 归一化参数
        f.write(f"LINE_OFF: {rpc_params['LINE_OFF']:+012.2f} pixels\n")
        f.write(f"SAMP_OFF: {rpc_params['SAMP_OFF']:+012.2f} pixels\n")
        f.write(f"LAT_OFF: {rpc_params['LAT_OFF']:+014.8f} degrees\n")
        f.write(f"LONG_OFF: {rpc_params['LONG_OFF']:+014.8f} degrees\n")
        f.write(f"HEIGHT_OFF: {rpc_params['HEIGHT_OFF']:+010.3f} meters\n")
        f.write(f"LINE_SCALE: {rpc_params['LINE_SCALE']:+012.2f} pixels\n")
        f.write(f"SAMP_SCALE: {rpc_params['SAMP_SCALE']:+012.2f} pixels\n")
        f.write(f"LAT_SCALE: {rpc_params['LAT_SCALE']:+012.8f} degrees\n")
        f.write(f"LONG_SCALE: {rpc_params['LONG_SCALE']:+012.8f} degrees\n")
        f.write(f"HEIGHT_SCALE: {rpc_params['HEIGHT_SCALE']:+010.3f} meters\n")

        # 四组系数
        coeff_names = [
            'LINE_NUM_COEFF', 'LINE_DEN_COEFF',
            'SAMP_NUM_COEFF', 'SAMP_DEN_COEFF'
        ]
        for name in coeff_names:
            coeffs = rpc_params[name]
            for i, c in enumerate(coeffs):
                f.write(f"{name}_{i+1}: {c:+042.38e}\n")

    print(f"  RPC 参数已保存: {output_path}")


def parse_rpc_file(rpc_path):
    """解析 RPC 参数文件

    从文本文件中提取 10 个归一化参数和 4 组各 20 个有理多项式系数。

    参数:
        rpc_path: RPC 参数文件路径

    返回:
        rpc_params: dict，含归一化参数和多项式系数
    """
    rpc_params = {}

    with open(rpc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析归一化参数
    for key in ['LINE_OFF', 'SAMP_OFF', 'LAT_OFF', 'LONG_OFF', 'HEIGHT_OFF',
                'LINE_SCALE', 'SAMP_SCALE', 'LAT_SCALE', 'LONG_SCALE', 'HEIGHT_SCALE']:
        match = re.search(rf'{key}:\s*([+\-\d.]+)', content)
        if match:
            rpc_params[key] = float(match.group(1))

    # 解析四组多项式系数（每组 20 项）
    for prefix in ['LINE_NUM', 'LINE_DEN', 'SAMP_NUM', 'SAMP_DEN']:
        coeffs = []
        for i in range(1, 21):
            match = re.search(rf'{prefix}_COEFF_{i}:\s*([+\-\de.]+)', content)
            if match:
                coeffs.append(float(match.group(1)))
        rpc_params[prefix + '_COEFF'] = np.array(coeffs)

    return rpc_params


# ---------------------------------------------------------------------------
# 单独测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys

    print("=" * 60)
    print("模块 06: rpc_solver.py 单独测试")
    print("=" * 60)

    # 查找测试数据
    test_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'test_data'
    )
    input_path = os.path.join(test_data_dir, 'input_sample',
                              'rpc_sample_points_sample.csv')

    if not os.path.exists(input_path):
        print(f"错误: 测试数据不存在 -> {input_path}")
        sys.exit(1)

    # 读取样本点
    data = np.loadtxt(input_path, delimiter=',', skiprows=1)
    print(f"读取样本点: {data.shape[0]} 个")

    # 求解 RPC
    print("\n--- solve_rpc() ---")
    rpc_params = solve_rpc(data)

    # 保存结果
    output_dir = os.path.join(test_data_dir, 'output_sample')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'rpc_params_sample.txt')

    print("\n--- save_rpc_result() ---")
    save_rpc_result(rpc_params, output_path)

    print("\n测试完成。")
