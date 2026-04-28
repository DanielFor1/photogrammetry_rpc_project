"""
forward_projection.py

严格成像模型正投影模块。
"""


def forward_projection(ground_points, orbit_interp_result, rotation_matrix_result, camera_angle_result):
    """
    实现物方点到像方点的正投影计算。

    参数：
        ground_points: 物方点集合，字段建议为 point_id, lon, lat, height
        orbit_interp_result: 轨道内插结果
        rotation_matrix_result: 旋转矩阵结果
        camera_angle_result: 相机指向角处理结果

    返回：
        forward_projection_result: 正投影结果，字段建议为 point_id, row, col
    """
    print("forward_projection() 待实现")
    forward_projection_result = None
    return forward_projection_result


if __name__ == "__main__":
    print("模块 04：forward_projection.py 单独测试入口")
