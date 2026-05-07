import numpy as np
import pandas as pd
import os

def calculate_forward_projection(ground_point, orbit_result, attitude_result, camera_params):
    """
    建立严格成像模型，实现地面物方点到像方点的正投影计算
    
    Args:
        ground_point: dict, {'lon': , 'lat': , 'height': } 地面点坐标
        orbit_result: dict, {'X': , 'Y': , 'Z': } 卫星在 ECEF 下的位置
        attitude_result: matrix, 3x3 姿态旋转矩阵 (从 ECEF 到相机坐标系)
        camera_params: dict, 包含焦距 f, 主点 row0, col0, 像元尺寸 pixel_size
    
    Returns:
        image_point_result: dict, {'row': , 'col': }
    """
    
    # 1. 坐标系转换：WGS84 经纬高转 ECEF (由于 1 号已处理转换逻辑，此处简化演示)
    # 假设 ground_point 已由 1 号或 5 号模块转为 ECEF 直角坐标 (Xg, Yg, Zg)
    # 如果输入是 lon, lat, height，需要调用 1 号模块的转换函数
    xg = ground_point['X']
    yg = ground_point['Y']
    zg = ground_point['Z']
    
    # 2. 计算地面点相对于卫星的位置向量 (物方矢量)
    vector_obj_x = xg - orbit_result['X']
    vector_obj_y = yg - orbit_result['Y']
    vector_obj_z = zg - orbit_result['Z']
    vector_obj = np.array([vector_obj_x, vector_obj_y, vector_obj_z])
    
    # 3. 将物方矢量旋转至相机坐标系
    # rotation_matrix 由 3 号模块提供
    rotation_matrix = attitude_result
    vector_cam = np.dot(rotation_matrix, vector_obj)
    
    # 4. 根据共线方程计算像平面坐标 (x, y)
    # 相机系：Z轴指向镜头前方，x, y 对应像面
    f = camera_params['f']
    if vector_cam[2] == 0:
        return {'row': None, 'col': None}
    
    x = -f * (vector_cam[0] / vector_cam[2])
    y = -f * (vector_cam[1] / vector_cam[2])
    
    # 5. 像平面坐标转像元行列号 (Row, Col)
    pixel_size = camera_params['pixel_size']
    row0 = camera_params['row0']
    col0 = camera_params['col0']
    
    # 注意：行列号方向需根据相机坐标系定义调整，此处为标准映射
    col = col0 + x / pixel_size
    row = row0 - y / pixel_size
    
    return {'row': row, 'col': col}

def batch_forward_projection(input_path, output_path, camera_params):
    """
    批量处理正投影计算
    """
    # 读取合并后的中间数据（含轨道、姿态、待投影地面点）
    data_df = pd.read_csv(input_path)
    
    results = []
    for index, row in data_df.iterrows():
        ground_point = {'X': row['X'], 'Y': row['Y'], 'Z': row['Z']}
        orbit_result = {'X': row['sat_X'], 'Y': row['sat_Y'], 'Z': row['sat_Z']}
        
        # 模拟 3x3 姿态矩阵（实际应用中需从 3 号模块读取的四元数转换）
        attitude_matrix = np.array([
            [row['m11'], row['m12'], row['m13']],
            [row['m21'], row['m22'], row['m23']],
            [row['m31'], row['m32'], row['m33']]
        ])
        
        image_point = calculate_forward_projection(
            ground_point, orbit_result, attitude_matrix, camera_params
        )
        results.append(image_point)
    
    # 保存结果
    projection_result_df = pd.DataFrame(results)
    output_df = pd.concat([data_df, projection_result_df], axis=1)
    output_df.to_csv(output_path, index=False)
    print(f"Forward projection completed. Saved to {output_path}")

if __name__ == "__main__":
    # 测试参数配置
    test_camera_params = {
        'f': 50000.0,      # 焦距 (um)
        'pixel_size': 5.0, # 像元大小 (um)
        'row0': 10000.0,   # 中心行号
        'col0': 10000.0    # 中心列号
    }
    
    # 构造测试输入路径
    input_csv_path = "../test_data/input_ground_points.csv"
    output_csv_path = "../test_data/output_projection_results.csv"
    
    # 如果测试目录不存在则创建
    os.makedirs("../test_data", exist_ok=True)
    
    # 运行
    if os.path.exists(input_csv_path):
        batch_forward_projection(input_csv_path, output_csv_path, test_camera_params)
    else:
        print("Waiting for test data from modules 1, 2, and 3.")
