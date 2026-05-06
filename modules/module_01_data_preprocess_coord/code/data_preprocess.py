"""
data_preprocess.py

数据读取与预处理模块。
"""

import re
import os
from datetime import datetime, timedelta
import numpy as np

def timecode_to_datetime_str(timecode, reference_timecode, reference_datetime_str):
    """
    将时间代码转换为 UTC 时间字符串。
    
    参数：
        timecode: 待转换的时间代码
        reference_timecode: 参考时间代码
        reference_datetime_str: 参考 UTC 时间字符串

    返回：
        datetime_str: 转换后的 UTC 时间字符串
    """
    
    reference_datetime = datetime.strptime(reference_datetime_str.strip(), "%Y %m %d %H:%M:%S.%f")
    delta_seconds = timecode - reference_timecode
    datetime_str = (reference_datetime + timedelta(seconds=delta_seconds)).strftime("%Y %m %d %H:%M:%S.%f")
    return datetime_str

def load_raw_data(orbit_path, attitude_path, imaging_time_path):
    """
    读取轨道、姿态、成像时刻等原始数据。

    参数：
        orbit_path: 离散轨道数据路径
        attitude_path: 离散姿态数据路径
        imaging_time_path: 扫描行成像时刻文件路径

    返回：
        orbit_data, attitude_data, imaging_time_data
    """
    
    # 读取离散轨道数据
    with open(orbit_path, 'r') as f:
        content = f.read()

    pattern = re.compile(
        r'timeCode\s*=\s*([\d.]+)\s*;'
        r'.*?dateTime\s*=\s*"([^"]+)"\s*;'
        r'.*?PX\s*=\s*([-\d.]+)\s*;'
        r'.*?PY\s*=\s*([-\d.]+)\s*;'
        r'.*?PZ\s*=\s*([-\d.]+)\s*;'
        r'.*?VX\s*=\s*([-\d.]+)\s*;'
        r'.*?VY\s*=\s*([-\d.]+)\s*;'
        r'.*?VZ\s*=\s*([-\d.]+)\s*;',
        re.DOTALL
    )

    records = []

    for match in pattern.finditer(content):
        t = float(match.group(1))
        dt_str = match.group(2).strip()
        pos = [float(match.group(i)) for i in (3, 4, 5)]
        vel = [float(match.group(i)) for i in (6, 7, 8)]
        records.append((t, dt_str, pos, vel))

    orbit_data = np.array(records, dtype=[('orbit_time', 'f8'), ('orbit_datetime_str', 'U32'), ('satellite_position', 'f8', (3,)), ('satellite_velocity', 'f8', (3,))])

    # 读取离散姿态数据
    with open(attitude_path, 'r') as f:
        content = f.read()
    
    pattern = re.compile(
        r'timeCode\s*=\s*([\d.]+)\s*;'
        r'.*?dateTime\s*=\s*"([^"]+)"\s*;'
        r'.*?eulor1\s*=\s*([-\d.]+)\s*;'
        r'.*?eulor2\s*=\s*([-\d.]+)\s*;'
        r'.*?eulor3\s*=\s*([-\d.]+)\s*;'
        r'.*?q1\s*=\s*([-\d.]+)\s*;'
        r'.*?q2\s*=\s*([-\d.]+)\s*;'
        r'.*?q3\s*=\s*([-\d.]+)\s*;'
        r'.*?q4\s*=\s*([-\d.]+)\s*;',
        re.DOTALL
    )

    records = []

    for match in pattern.finditer(content):
        t = float(match.group(1))
        dt_str = match.group(2).strip()
        euler = [float(match.group(i)) for i in (3, 4, 5)]
        quat = [float(match.group(i)) for i in (6, 7, 8, 9)]
        records.append((t, dt_str, euler, quat))

    attitude_data = np.array(records, dtype=[('attitude_time', 'f8'), ('attitude_datetime_str', 'U32'), ('euler', 'f8', (3,)), ('quaternion', 'f8', (4,))])

    # 读取扫描行成像时刻数据
    records = []

    with open(imaging_time_path, 'r') as f:
        next(f)  # 跳过表头
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                rel_line = int(parts[0])
                t = float(parts[1])
                records.append((rel_line, t))

    # 将成像时刻的 timeCode 转换为 UTC 时间字符串
    reference_timecode = orbit_data[0]['orbit_time']
    reference_datetime_str = orbit_data[0]['orbit_datetime_str']
    for i in range(len(records)):
        rel_line, t = records[i]
        dt_str = timecode_to_datetime_str(t, reference_timecode, reference_datetime_str)
        records[i] = (rel_line, t, dt_str)

    imaging_time_data = np.array(records, dtype=[('rel_line', 'i4'), ('imaging_time', 'f8'), ('imaging_datetime_str', 'U32')])

    return orbit_data, attitude_data, imaging_time_data

def save_preprocessed_data(preprocessed_data, output_path):
    """
    保存预处理结果。

    参数：
        preprocessed_data: 预处理后的数据
        output_path: 输出路径
    """
    
    orbit_data, attitude_data, imaging_time_data = preprocessed_data

    time = orbit_data['orbit_time']
    X = orbit_data['satellite_position'][:, 0]
    Y = orbit_data['satellite_position'][:, 1]
    Z = orbit_data['satellite_position'][:, 2]
    Vx = orbit_data['satellite_velocity'][:, 0]
    Vy = orbit_data['satellite_velocity'][:, 1]
    Vz = orbit_data['satellite_velocity'][:, 2]
    orbit_matrix = np.column_stack((time, X, Y, Z, Vx, Vy, Vz))
    orbit_header = "time,X,Y,Z,Vx,Vy,Vz"
    np.savetxt(os.path.join(output_path, "preprocessed_orbit_sample.csv"), orbit_matrix, header=orbit_header, delimiter=",", comments="", fmt="%s")

    time = attitude_data['attitude_time']
    q0 = attitude_data['quaternion'][:, 0]
    q1 = attitude_data['quaternion'][:, 1]
    q2 = attitude_data['quaternion'][:, 2]
    q3 = attitude_data['quaternion'][:, 3]
    attitude_matrix = np.column_stack((time, q0, q1, q2, q3))
    attitude_header = "time,q0,q1,q2,q3"
    np.savetxt(os.path.join(output_path, "preprocessed_attitude_sample.csv"), attitude_matrix, header=attitude_header, delimiter=",", comments="", fmt="%s")

    time = imaging_time_data['imaging_time']
    np.savetxt(os.path.join(output_path, "preprocessed_imaging_time_sample.csv"), time, header="time", delimiter=",", comments="", fmt="%s")


if __name__ == "__main__":
    print("模块 01：data_preprocess.py 单独测试入口")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_input_dir = os.path.join(base_dir, '..', 'test_data', 'input_sample')
    test_output_dir = os.path.join(base_dir, '..', 'test_data', 'output_sample')
    os.makedirs(test_output_dir, exist_ok=True)
    
    orbit_path = os.path.join(test_input_dir, "orbit_sample.txt")
    attitude_path = os.path.join(test_input_dir, "attitude_sample.txt")
    imaging_time_path = os.path.join(test_input_dir, "imaging_time_sample.txt")
    preprocessed_data = load_raw_data(orbit_path, attitude_path, imaging_time_path)
    save_preprocessed_data(preprocessed_data, test_output_dir)

    print("模块 01：data_preprocess.py 单独测试完成，预处理结果已保存到 output_sample 目录")