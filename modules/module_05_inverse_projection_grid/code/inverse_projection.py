"""
inverse_projection.py

严格成像模型反投影模块。
"""


def inverse_projection(image_points, orbit_interp_result, rotation_matrix_result, camera_angle_result):
    """
    实现像点到物方点的反投影或迭代求解。

    参数：
        image_points: 像方点集合，字段建议为 point_id, row, col

    返回：
        inverse_projection_result: 反投影结果，字段建议为 point_id, lon, lat, height
    """
    print("inverse_projection() 待实现")
    inverse_projection_result = None
    return inverse_projection_result


if __name__ == "__main__":
    print("模块 05：inverse_projection.py 单独测试入口")
