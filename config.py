from pathlib import Path

project_root = Path(__file__).resolve().parent

raw_data_dir = project_root / "data" / "raw"
sample_data_dir = project_root / "data" / "sample"
processed_data_dir = project_root / "data" / "processed"
result_dir = project_root / "data" / "result"

orbit_path = sample_data_dir / "orbit_sample.csv"
attitude_path = sample_data_dir / "attitude_sample.csv"
imaging_time_path = sample_data_dir / "imaging_time_sample.csv"
look_angle_table_path = sample_data_dir / "look_angle_table_sample.csv"

output_path = processed_data_dir
