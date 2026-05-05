"""
Module 02: orbit interpolation.

Core function input follows the project README:
orbit_data: time, X, Y, Z, Vx, Vy, Vz
imaging_time_data: time
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ORBIT_COLUMNS = ["time", "X", "Y", "Z", "Vx", "Vy", "Vz"]
IMAGING_TIME_COLUMNS = ["time"]
INTERP_COLUMNS = ["X", "Y", "Z", "Vx", "Vy", "Vz"]


def lagrange_interpolate(time_values, data_values, target_time):
    """
    Interpolate one scalar value with Lagrange interpolation.
    """
    result = 0.0

    for i in range(len(time_values)):
        basis = 1.0
        for j in range(len(time_values)):
            if i == j:
                continue
            basis *= (target_time - time_values[j]) / (time_values[i] - time_values[j])
        result += data_values[i] * basis

    return result


def select_local_window(orbit_times, target_time, window_size):
    """
    Select local orbit sample indexes around the target imaging time.
    """
    insert_index = np.searchsorted(orbit_times, target_time)
    start_index = insert_index - window_size // 2
    start_index = max(0, start_index)
    start_index = min(start_index, len(orbit_times) - window_size)
    end_index = start_index + window_size

    return start_index, end_index


def check_input_data(orbit_data, imaging_time_data, window_size):
    """
    Fail fast if input data does not match the module 02 contract.
    """
    missing_orbit_columns = [col for col in ORBIT_COLUMNS if col not in orbit_data.columns]
    if missing_orbit_columns:
        raise ValueError(f"Missing orbit columns: {missing_orbit_columns}")

    missing_imaging_columns = [
        col for col in IMAGING_TIME_COLUMNS if col not in imaging_time_data.columns
    ]
    if missing_imaging_columns:
        raise ValueError(f"Missing imaging time columns: {missing_imaging_columns}")

    if len(orbit_data) < window_size:
        raise ValueError("Orbit data rows must be greater than or equal to window_size")

    if len(imaging_time_data) == 0:
        raise ValueError("Imaging time data is empty")

    orbit_times = orbit_data["time"].to_numpy(dtype=float)
    imaging_times = imaging_time_data["time"].to_numpy(dtype=float)

    if np.any(np.diff(orbit_times) <= 0):
        raise ValueError("Orbit time column must be strictly increasing")

    if imaging_times.min() < orbit_times[0] or imaging_times.max() > orbit_times[-1]:
        raise ValueError("Imaging time is outside the orbit time range")


def interpolate_orbit(orbit_data, imaging_time_data, window_size=4):
    """
    Interpolate satellite position and velocity at each imaging time.

    Parameters
    ----------
    orbit_data : pandas.DataFrame
        Columns: time, X, Y, Z, Vx, Vy, Vz.
    imaging_time_data : pandas.DataFrame
        Columns: time.
    window_size : int
        Local Lagrange interpolation point count.

    Returns
    -------
    orbit_interp_result : pandas.DataFrame
        Columns: time, X, Y, Z, Vx, Vy, Vz.
    """
    check_input_data(orbit_data, imaging_time_data, window_size)

    orbit_times = orbit_data["time"].to_numpy(dtype=float)
    imaging_times = imaging_time_data["time"].to_numpy(dtype=float)

    rows = []
    for imaging_time in imaging_times:
        start_index, end_index = select_local_window(
            orbit_times,
            imaging_time,
            window_size,
        )
        local_times = orbit_times[start_index:end_index]
        output_row = [imaging_time]

        for column in INTERP_COLUMNS:
            local_values = orbit_data[column].to_numpy(dtype=float)[start_index:end_index]
            interpolated_value = lagrange_interpolate(
                local_times,
                local_values,
                imaging_time,
            )
            output_row.append(interpolated_value)

        rows.append(output_row)

    orbit_interp_result = pd.DataFrame(rows, columns=ORBIT_COLUMNS)
    return orbit_interp_result


def save_orbit_result(orbit_interp_result, output_path):
    """
    Save orbit interpolation result as CSV.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    orbit_interp_result.to_csv(output_path, index=False)


def get_mode_paths(mode):
    """
    Return input and output paths for the selected running mode.
    """
    module_dir = Path(__file__).resolve().parents[1]
    project_root = Path(__file__).resolve().parents[3]

    if mode == "sample":
        input_dir = module_dir / "test_data" / "input_sample"
        output_dir = module_dir / "test_data" / "output_sample"
        return {
            "orbit_path": input_dir / "preprocessed_orbit_sample.csv",
            "imaging_time_path": input_dir / "preprocessed_imaging_time_sample.csv",
            "output_path": output_dir / "orbit_interp_result_sample.csv",
        }

    if mode == "formal":
        processed_dir = project_root / "data" / "processed"
        return {
            "orbit_path": processed_dir / "preprocessed_orbit_sample.csv",
            "imaging_time_path": processed_dir / "preprocessed_imaging_time_sample.csv",
            "output_path": processed_dir / "orbit_interp_result_sample.csv",
        }

    raise ValueError(f"Unknown mode: {mode}")


def main():
    parser = argparse.ArgumentParser(description="Run module 02 orbit interpolation.")
    parser.add_argument(
        "--mode",
        choices=["sample", "formal"],
        default="sample",
        help="sample uses module test_data; formal uses data/processed from module 01.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=4,
        help="Local Lagrange interpolation point count.",
    )
    args = parser.parse_args()

    paths = get_mode_paths(args.mode)

    orbit_data = pd.read_csv(paths["orbit_path"])
    imaging_time_data = pd.read_csv(paths["imaging_time_path"])

    orbit_interp_result = interpolate_orbit(
        orbit_data,
        imaging_time_data,
        window_size=args.window_size,
    )
    save_orbit_result(orbit_interp_result, paths["output_path"])

    print(f"mode: {args.mode}")
    print(f"orbit rows: {len(orbit_data)}")
    print(f"imaging time rows: {len(imaging_time_data)}")
    print(f"output rows: {len(orbit_interp_result)}")
    print(f"output path: {paths['output_path']}")


if __name__ == "__main__":
    main()
