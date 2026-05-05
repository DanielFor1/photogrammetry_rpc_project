"""
模块03：姿态内插与指向角处理模块
"""

from .attitude_interp import (
    slerp,
    quaternion_to_rotation_matrix,
    interpolate_attitude,
    process_camera_look_angle,
    build_rotation_matrix
)

__all__ = [
    'slerp',
    'quaternion_to_rotation_matrix',
    'interpolate_attitude',
    'process_camera_look_angle',
    'build_rotation_matrix'
]