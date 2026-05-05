"""
accuracy_eval.py

RPC 精度评定模块。
提供内符合精度检查（训练样本回代）和外符合精度检查（DEM 独立检查点），
以及综合精度报告输出。
"""

import numpy as np

from rpc_solver import rpc_forward


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

def _compute_statistics(errors):
    """计算误差统计指标

    返回:
        stats: dict，含 rmse, mae, max, mean, std
    """
    abs_errors = np.abs(errors)
    return {
        'rmse': np.sqrt(np.mean(errors ** 2)),
        'mae': np.mean(abs_errors),
        'max': np.max(abs_errors),
        'mean': np.mean(errors),
        'std': np.std(errors),
    }


# ---------------------------------------------------------------------------
# 内符合精度检查
# ---------------------------------------------------------------------------

def evaluate_accuracy(rpc_params, check_points):
    """利用检查点进行精度评定（内符合 / 外符合通用）

    对每个检查点 (lon, lat, height, row, col):
      1. 用 RPC 正变换由地面坐标计算像方坐标 (row_rpc, col_rpc)
      2. 与参考像方坐标 (row_ref, col_ref) 求差得到误差
      3. 计算平面误差 plane_error = sqrt(row_error^2 + col_error^2)

    参数:
        rpc_params:   dict，含归一化参数和多项式系数
        check_points: DataFrame 或 ndarray
            列: point_id, lon, lat, height, row, col

    返回:
        accuracy_result: ndarray, shape (N, 4)
            列: point_id, row_error, col_error, plane_error
    """
    data = np.array(check_points)
    if data.ndim == 2 and data.shape[1] >= 6:
        point_ids = data[:, 0].astype(float)
        lon_arr = data[:, 1].astype(float)
        lat_arr = data[:, 2].astype(float)
        height_arr = data[:, 3].astype(float)
        row_ref = data[:, 4].astype(float)
        col_ref = data[:, 5].astype(float)
    else:
        raise ValueError(
            "check_points 需为 (N, 6) 数组，列为 "
            "point_id, lon, lat, height, row, col"
        )

    n_points = len(lon_arr)
    row_errors = np.zeros(n_points)
    col_errors = np.zeros(n_points)

    for i in range(n_points):
        row_rpc, col_rpc = rpc_forward(
            lat_arr[i], lon_arr[i], height_arr[i], rpc_params
        )
        row_errors[i] = row_rpc - row_ref[i]
        col_errors[i] = col_rpc - col_ref[i]

    plane_errors = np.sqrt(row_errors ** 2 + col_errors ** 2)

    accuracy_result = np.column_stack([
        point_ids, row_errors, col_errors, plane_errors
    ])

    # 打印统计指标
    stats_row = _compute_statistics(row_errors)
    stats_col = _compute_statistics(col_errors)
    stats_plane = _compute_statistics(plane_errors)

    print(f"  检查点数量: {n_points}")
    print(f"  精度评定结果:")
    print(f"    行方向: RMSE = {stats_row['rmse']:.6f} 像素, "
          f"MAX = {stats_row['max']:.6f} 像素")
    print(f"    列方向: RMSE = {stats_col['rmse']:.6f} 像素, "
          f"MAX = {stats_col['max']:.6f} 像素")
    print(f"    平面  : RMSE = {stats_plane['rmse']:.6f} 像素, "
          f"MAX = {stats_plane['max']:.6f} 像素")

    return accuracy_result


# ---------------------------------------------------------------------------
# 外符合精度检查（DEM + 严格成像模型）
# ---------------------------------------------------------------------------

def sample_dem_points(dem_path, gcps_arr, n_lat=20, n_lon=20):
    """在影像覆盖范围内均匀采样地面点，从 DEM 内插高程

    流程 (参考根目录 rpc_solver.py):
      1. 从 GCP 数据确定影像覆盖的经纬度范围（保留 5% 边距）
      2. 在该范围内生成 n_lat x n_lon 均匀格网
      3. 使用 rasterio 读取 DEM + scipy 双线性插值获取各点高程
      4. 过滤无效点

    依赖: rasterio, scipy（仅本函数需要，不影响其他函数的独立运行）

    参数:
        dem_path: DEM GeoTIFF 文件路径
        gcps_arr: (N, 3+) 数组，用于确定影像覆盖范围（列 0=lat, 列 1=lon）
        n_lat:    纬度方向采样点数 (默认 20)
        n_lon:    经度方向采样点数 (默认 20)

    返回:
        ground_points: list of (lat, lon, h) 地面检查点
    """
    import rasterio
    from rasterio.warp import transform as rasterio_transform
    from scipy.interpolate import RegularGridInterpolator

    gcps = np.array(gcps_arr)

    # 从 GCP 确定影像覆盖的经纬度范围，保留 5% 边距
    lat_min, lat_max = gcps[:, 0].min(), gcps[:, 0].max()
    lon_min, lon_max = gcps[:, 1].min(), gcps[:, 1].max()
    lat_margin = (lat_max - lat_min) * 0.05
    lon_margin = (lon_max - lon_min) * 0.05
    lat_min += lat_margin
    lat_max -= lat_margin
    lon_min += lon_margin
    lon_max -= lon_margin

    # 生成均匀经纬度格网
    lats = np.linspace(lat_min, lat_max, n_lat)
    lons = np.linspace(lon_min, lon_max, n_lon)

    # 打开 DEM 并内插高程
    with rasterio.open(dem_path) as ds:
        lat_grid, lon_grid = np.meshgrid(lats, lons, indexing='ij')
        flat_lats = lat_grid.ravel()
        flat_lons = lon_grid.ravel()

        # 经纬度 -> DEM 投影坐标 (rasterio 用 x=lon, y=lat 顺序)
        xs, ys = rasterio_transform('EPSG:4326', ds.crs, flat_lons, flat_lats)
        xs = np.array(xs)
        ys = np.array(ys)

        # 投影坐标 -> 像素行列号
        col_f, row_f = ~ds.transform * (xs, ys)

        # 确定读取窗口（加边距确保插值有效）
        row_min_idx = max(0, int(np.floor(np.min(row_f))) - 2)
        row_max_idx = min(ds.height - 1, int(np.ceil(np.max(row_f))) + 2)
        col_min_idx = max(0, int(np.floor(np.min(col_f))) - 2)
        col_max_idx = min(ds.width - 1, int(np.ceil(np.max(col_f))) + 2)

        window = rasterio.windows.Window(
            col_off=col_min_idx, row_off=row_min_idx,
            width=col_max_idx - col_min_idx + 1,
            height=row_max_idx - row_min_idx + 1
        )
        data = ds.read(1, window=window).astype(float)
        nodata = ds.nodata
        if nodata is not None:
            data[data == nodata] = np.nan

    # 构建插值器
    block_row_coords = np.arange(row_min_idx, row_min_idx + data.shape[0])
    block_col_coords = np.arange(col_min_idx, col_min_idx + data.shape[1])
    interpolator = RegularGridInterpolator(
        (block_row_coords, block_col_coords), data,
        method='linear', bounds_error=False, fill_value=np.nan
    )

    # 插值获取各点高程
    query_points = np.column_stack([row_f, col_f])
    elevations = interpolator(query_points)

    # 过滤无效点
    valid_mask = ~np.isnan(elevations) & (elevations > -1000)
    ground_points = []
    for i in range(len(flat_lats)):
        if valid_mask[i]:
            ground_points.append((flat_lats[i], flat_lons[i], float(elevations[i])))

    print(f"  DEM 采样: {n_lat}x{n_lon} = {len(flat_lats)} 个格网点, "
          f"有效点 {len(ground_points)} 个")

    return ground_points


def external_accuracy_check(dem_path, gcps_arr, rpc_params,
                            strict_image_coords,
                            n_lat=20, n_lon=20):
    """外符合精度检验：使用 DEM 参考数据，比较严格模型与 RFM 的像点精度

    流程 (参考根目录 rpc_solver.py 的 external_accuracy_check):
      1. 在影像覆盖范围内从 DEM 采样地面点 (lat, lon, h_dem)
      2. 对每个地面点，用严格模型反投影得到参考像方坐标
      3. 用 RPC 正变换计算 RFM 像方坐标
      4. 计算像方残差 (row_rfm - row_strict, col_rfm - col_strict)
      5. 过滤影像范围外的点，统计 RMS / MAE / MAX 精度指标

    参数:
        dem_path:            DEM GeoTIFF 文件路径
        gcps_arr:            (N, 3+) GCP 数组，用于确定影像覆盖范围
        rpc_params:          dict，RPC 参数（含归一化参数和多项式系数）
        strict_image_coords: list of (row, col)
            严格模型反投影得到的像方坐标，与 ground_points 一一对应
        n_lat:               纬度方向采样点数 (默认 20)
        n_lon:               经度方向采样点数 (默认 20)

    返回:
        accuracy_result: ndarray, shape (N_valid, 4)
            列: point_id, row_error, col_error, plane_error
        或 None（无有效检查点时）
    """
    print("\n  [外符合精度检验] DEM + 严格模型")

    # 第 1 步：从 DEM 采样地面检查点
    print("  从 DEM 采样地面检查点...")
    ground_points = sample_dem_points(dem_path, gcps_arr, n_lat, n_lon)
    n = len(ground_points)

    if n == 0:
        print("  错误：未能从 DEM 获取有效检查点")
        return None

    # 第 2 步：验证严格模型像方坐标数量
    n_strict = len(strict_image_coords)
    if n_strict < n:
        print(f"  警告: DEM 采样 {n} 点, 严格模型坐标 {n_strict} 点, "
              f"取前 {n_strict} 点比较")
        n = n_strict

    # 第 3 步：RFM 正变换计算像方坐标
    print("  RFM 正变换计算像方坐标...")
    rfm_coords = []
    for lat, lon, h in ground_points[:n]:
        row_rfm, col_rfm = rpc_forward(lat, lon, h, rpc_params)
        rfm_coords.append((row_rfm, col_rfm))

    # 第 4 步：计算残差（过滤影像范围外的点）
    residuals_row = []
    residuals_col = []
    point_ids = []
    for i, ((row_strict, col_strict), (row_rfm, col_rfm)) in enumerate(
            zip(strict_image_coords[:n], rfm_coords)):
        # 跳过严格模型投影到影像边缘的点
        if col_strict <= 0 or col_strict >= 10000:
            continue
        # 跳过 RFM 投影结果为异常值的点
        if np.isnan(row_rfm) or np.isnan(col_rfm):
            continue
        residuals_row.append(row_rfm - row_strict)
        residuals_col.append(col_rfm - col_strict)
        point_ids.append(i)

    if len(residuals_row) == 0:
        print("  错误：无有效检查点")
        return None

    residuals_row = np.array(residuals_row)
    residuals_col = np.array(residuals_col)
    point_ids = np.array(point_ids, dtype=float)

    # 第 5 步：统计指标
    n_valid = len(residuals_row)
    rms_row = np.sqrt(np.mean(residuals_row ** 2))
    rms_col = np.sqrt(np.mean(residuals_col ** 2))
    mae_row = np.mean(np.abs(residuals_row))
    mae_col = np.mean(np.abs(residuals_col))
    max_row = np.max(np.abs(residuals_row))
    max_col = np.max(np.abs(residuals_col))
    total_2d = np.sqrt(residuals_row ** 2 + residuals_col ** 2)
    rms_2d = np.sqrt(np.mean(total_2d ** 2))

    print(f"\n  外符合精度检验结果（{n_valid}/{n} 个有效 DEM 参考点）")
    print(f"  {'─' * 50}")
    print(f"  像方行方向: RMS = {rms_row:.6f} 像素, "
          f"MAE = {mae_row:.6f}, MAX = {max_row:.6f}")
    print(f"  像方列方向: RMS = {rms_col:.6f} 像素, "
          f"MAE = {mae_col:.6f}, MAX = {max_col:.6f}")
    print(f"  像方 2D  : RMS = {rms_2d:.6f} 像素")

    accuracy_result = np.column_stack([
        point_ids, residuals_row, residuals_col, total_2d
    ])

    return accuracy_result


# ---------------------------------------------------------------------------
# 综合精度报告
# ---------------------------------------------------------------------------

def comprehensive_accuracy_report(rpc_params, rpc_sample_points,
                                  check_points=None, dem_path=None,
                                  gcps_arr=None, strict_image_coords=None,
                                  output_dir=None):
    """综合精度报告：汇总内符合和外符合精度检查结果

    流程:
      1. 内符合精度：将训练样本点代入 RPC 正变换，与参考坐标比较
      2. 外符合精度（可选）：用独立检查点评定
      3. 外符合精度（可选）：用 DEM + 严格模型评定
      4. 汇总输出统计指标表

    参数:
        rpc_params:          dict，RPC 参数
        rpc_sample_points:   ndarray，训练样本点 (N, 6)
        check_points:        ndarray，独立检查点 (M, 6)，可选
        dem_path:            str，DEM 文件路径，可选
        gcps_arr:            ndarray，GCP 数组，用于确定 DEM 采样范围，可选
        strict_image_coords: list of (row, col)，严格模型像方坐标，可选
        output_dir:          str，结果输出目录，可选

    返回:
        report: dict
            internal: 内符合精度结果 (accuracy_result ndarray)
            external: 外符合精度结果 (accuracy_result ndarray 或 None)
            statistics: 综合统计指标 dict
    """
    print("=" * 60)
    print("RPC 综合精度报告")
    print("=" * 60)

    report = {'internal': None, 'external': None, 'statistics': {}}

    # -------------------------------------------------------------------
    # 内符合精度检查
    # -------------------------------------------------------------------
    print("\n[1] 内符合精度检查（训练样本回代）")
    print("-" * 40)

    internal_result = evaluate_accuracy(rpc_params, rpc_sample_points)
    report['internal'] = internal_result

    int_row_stats = _compute_statistics(internal_result[:, 1])
    int_col_stats = _compute_statistics(internal_result[:, 2])
    int_plane_stats = _compute_statistics(internal_result[:, 3])

    report['statistics']['internal'] = {
        'rmse_row': int_row_stats['rmse'],
        'rmse_col': int_col_stats['rmse'],
        'rmse_plane': int_plane_stats['rmse'],
        'max_row': int_row_stats['max'],
        'max_col': int_col_stats['max'],
        'max_plane': int_plane_stats['max'],
    }

    # -------------------------------------------------------------------
    # 外符合精度检查（独立检查点）
    # -------------------------------------------------------------------
    if check_points is not None:
        print(f"\n[2] 外符合精度检查（独立检查点）")
        print("-" * 40)

        external_result = evaluate_accuracy(rpc_params, check_points)
        report['external'] = external_result

        ext_row_stats = _compute_statistics(external_result[:, 1])
        ext_col_stats = _compute_statistics(external_result[:, 2])
        ext_plane_stats = _compute_statistics(external_result[:, 3])

        report['statistics']['external'] = {
            'rmse_row': ext_row_stats['rmse'],
            'rmse_col': ext_col_stats['rmse'],
            'rmse_plane': ext_plane_stats['rmse'],
            'max_row': ext_row_stats['max'],
            'max_col': ext_col_stats['max'],
            'max_plane': ext_plane_stats['max'],
        }

    # -------------------------------------------------------------------
    # 外符合精度检查（DEM + 严格模型）
    # -------------------------------------------------------------------
    if dem_path is not None and gcps_arr is not None and strict_image_coords is not None:
        tag = "[3]" if check_points is not None else "[2]"
        print(f"\n{tag} 外符合精度检查（DEM + 严格模型）")
        print("-" * 40)

        dem_result = external_accuracy_check(
            dem_path, gcps_arr, rpc_params, strict_image_coords
        )
        if dem_result is not None:
            report['external_dem'] = dem_result

    # -------------------------------------------------------------------
    # 汇总
    # -------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("精度汇总")
    print("=" * 60)
    print(f"  {'指标':<20} {'内符合':>12} {'外符合':>12}")
    print(f"  {'─' * 46}")

    int_stats = report['statistics'].get('internal', {})
    ext_stats = report['statistics'].get('external', {})

    for metric_name, metric_key in [
        ('RMSE 行方向 (像素)', 'rmse_row'),
        ('RMSE 列方向 (像素)', 'rmse_col'),
        ('RMSE 平面 (像素)', 'rmse_plane'),
        ('MAX 行方向 (像素)', 'max_row'),
        ('MAX 列方向 (像素)', 'max_col'),
        ('MAX 平面 (像素)', 'max_plane'),
    ]:
        int_val = int_stats.get(metric_key, float('nan'))
        ext_val = ext_stats.get(metric_key, float('nan'))
        ext_str = f"{ext_val:.6f}" if ext_stats else "N/A"
        print(f"  {metric_name:<20} {int_val:>12.6f} {ext_str:>12}")

    # 保存结果文件
    if output_dir is not None:
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 保存内符合结果
        int_path = os.path.join(output_dir, 'accuracy_result_sample.csv')
        _save_accuracy_csv(internal_result, int_path)

        # 保存外符合结果
        if report['external'] is not None:
            ext_path = os.path.join(output_dir, 'accuracy_external_result_sample.csv')
            _save_accuracy_csv(report['external'], ext_path)

    return report


def _save_accuracy_csv(accuracy_result, output_path):
    """保存精度评定结果到 CSV 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("point_id,row_error,col_error,plane_error\n")
        for row in accuracy_result:
            f.write(f"{int(row[0])},{row[1]:.6f},{row[2]:.6f},{row[3]:.6f}\n")
    print(f"  结果已保存: {output_path}")


# ---------------------------------------------------------------------------
# 单独测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys
    from rpc_solver import parse_rpc_file

    print("=" * 60)
    print("模块 06: accuracy_eval.py 单独测试")
    print("=" * 60)

    test_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'test_data'
    )

    # ------------------------------------------------------------------
    # 第 1 部分：内符合精度检查
    # ------------------------------------------------------------------
    rpc_path = os.path.join(test_data_dir, 'output_sample', 'rpc_params_sample.txt')
    sample_path = os.path.join(test_data_dir, 'input_sample', 'rpc_sample_points_sample.csv')
    check_path = os.path.join(test_data_dir, 'input_sample', 'check_points_sample.csv')

    if not os.path.exists(rpc_path):
        print(f"错误: RPC 参数文件不存在 -> {rpc_path}")
        print("请先运行 rpc_solver.py 生成 RPC 参数。")
        sys.exit(1)

    # 解析 RPC 参数（使用本模块的 parse_rpc_file）
    rpc_params = parse_rpc_file(rpc_path)
    print(f"读取 RPC 参数成功 (LINE_OFF={rpc_params['LINE_OFF']:.1f})")

    # 读取训练样本点
    sample_data = np.loadtxt(sample_path, delimiter=',', skiprows=1)
    print(f"读取训练样本: {sample_data.shape[0]} 个")

    # 读取检查点
    check_data = None
    if os.path.exists(check_path):
        check_data = np.loadtxt(check_path, delimiter=',', skiprows=1)
        print(f"读取检查点: {check_data.shape[0]} 个")

    # ------------------------------------------------------------------
    # 第 2 部分：综合精度报告
    # ------------------------------------------------------------------
    output_dir = os.path.join(test_data_dir, 'output_sample')

    # 检查是否有 DEM 数据
    dem_path = None
    possible_dem = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
        'data', 'reference_dem.tif'
    )
    if os.path.exists(possible_dem):
        dem_path = possible_dem
        print(f"找到 DEM 数据: {dem_path}")

    # 构造 DEM 外符合检查所需的参数
    # gcps_arr: 取训练样本的 (lat, lon, height) 列
    # sample_data 列: point_id, lon, lat, height, row, col
    gcps_arr = sample_data[:, [2, 1, 3]]  # lat, lon, height — 用于确定 DEM 采样范围
    # strict_image_coords: 单独测试时用 RPC 正变换代替严格模型
    # 实际联调时应由模块 04 的 ground_to_image + 反投影精化提供
    strict_coords = None
    if dem_path is not None:
        print("\n  (单独测试: 用 RPC 正变换代替严格模型，实际联调请使用模块 04 结果)")
        dem_ground = sample_dem_points(dem_path, gcps_arr)
        strict_coords = []
        for lat, lon, h in dem_ground:
            row, col = rpc_forward(lat, lon, h, rpc_params)
            strict_coords.append((row, col))

    report = comprehensive_accuracy_report(
        rpc_params, sample_data,
        check_points=check_data,
        dem_path=dem_path,
        gcps_arr=gcps_arr,
        strict_image_coords=strict_coords,
        output_dir=output_dir
    )

    print("\n测试完成。")
