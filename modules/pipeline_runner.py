"""
Project integration entry point for the satellite photogrammetry assignment.

The module code in this repository was written independently by different
teammates, so this main file intentionally acts as a thin integration layer:
it normalizes file paths, adapts small schema differences, runs each stage, and
records the places where a fallback had to be used.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULT_DIR = PROJECT_ROOT / "data" / "result"

RAW_ORBIT_PATH = RAW_DIR / "DX_ZY3_NAD_gps.txt"
RAW_ATTITUDE_PATH = RAW_DIR / "DX_ZY3_NAD_att.txt"
RAW_IMAGING_TIME_PATH = RAW_DIR / "DX_ZY3_NAD_imagingTime.txt"
RAW_LOOK_ANGLE_PATH = RAW_DIR / "NAD.cbr"
RAW_REFERENCE_RPC_PATH = RAW_DIR / "zy3_rpc.txt"


def ensure_import_paths() -> None:
    """Allow sibling-style imports used inside several module files."""
    code_dirs = [
        PROJECT_ROOT / "modules" / "module_01_data_preprocess_coord" / "code",
        PROJECT_ROOT / "modules" / "module_02_orbit_interp" / "code",
        PROJECT_ROOT / "modules" / "module_03_attitude_interp" / "code",
        PROJECT_ROOT / "modules" / "module_04_forward_projection" / "code",
        PROJECT_ROOT / "modules" / "module_05_inverse_projection_grid" / "code",
        PROJECT_ROOT / "modules" / "module_06_rpc_accuracy" / "code",
    ]
    for code_dir in code_dirs:
        path_str = str(code_dir)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def require_columns(df: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_look_angle_table(path: Path) -> pd.DataFrame:
    """Read the raw CBR look-angle table into col, psi_x, psi_y."""
    records: list[tuple[int, float, float]] = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            try:
                col = int(parts[0])
                psi_x = float(parts[1])
                psi_y = float(parts[2])
            except ValueError:
                continue
            records.append((col, psi_x, psi_y))

    if not records:
        raise ValueError(f"No look-angle records parsed from {path}")
    return pd.DataFrame(records, columns=["col", "psi_x", "psi_y"])


def normalize_quaternion_table(attitude_data) -> pd.DataFrame:
    """
    Module 01 reads raw q1, q2, q3, q4 in file order. The raw sample and module
    03 convention use q0 as the scalar part, which is q4 in the raw file.
    """
    raw_quaternion = attitude_data["quaternion"]
    quaternion = np.column_stack(
        [
            raw_quaternion[:, 3],
            raw_quaternion[:, 0],
            raw_quaternion[:, 1],
            raw_quaternion[:, 2],
        ]
    ).astype(float)
    norms = np.linalg.norm(quaternion, axis=1)
    valid = norms > 0
    quaternion[valid] = quaternion[valid] / norms[valid, None]

    return pd.DataFrame(
        {
            "time": attitude_data["attitude_time"].astype(float),
            "q0": quaternion[:, 0],
            "q1": quaternion[:, 1],
            "q2": quaternion[:, 2],
            "q3": quaternion[:, 3],
        }
    )


def preprocess_from_raw(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from data_preprocess import load_raw_data

    orbit_data, attitude_data, imaging_time_data = load_raw_data(
        RAW_ORBIT_PATH,
        RAW_ATTITUDE_PATH,
        RAW_IMAGING_TIME_PATH,
    )

    orbit_df = pd.DataFrame(
        {
            "time": orbit_data["orbit_time"].astype(float),
            "X": orbit_data["satellite_position"][:, 0],
            "Y": orbit_data["satellite_position"][:, 1],
            "Z": orbit_data["satellite_position"][:, 2],
            "Vx": orbit_data["satellite_velocity"][:, 0],
            "Vy": orbit_data["satellite_velocity"][:, 1],
            "Vz": orbit_data["satellite_velocity"][:, 2],
        }
    )
    attitude_df = normalize_quaternion_table(attitude_data)
    imaging_time_df = pd.DataFrame({"time": imaging_time_data["imaging_time"].astype(float)})
    look_angle_table = load_look_angle_table(RAW_LOOK_ANGLE_PATH)

    save_csv(orbit_df, processed_dir / "preprocessed_orbit_sample.csv")
    save_csv(attitude_df, processed_dir / "preprocessed_attitude_sample.csv")
    save_csv(imaging_time_df, processed_dir / "preprocessed_imaging_time_sample.csv")
    save_csv(look_angle_table, processed_dir / "look_angle_table_sample.csv")
    save_csv(
        orbit_df.rename(columns={"X": "x_ecef", "Y": "y_ecef", "Z": "z_ecef"})[
            ["time", "x_ecef", "y_ecef", "z_ecef"]
        ],
        processed_dir / "ecef_result_sample.csv",
    )

    return orbit_df, attitude_df, imaging_time_df, look_angle_table


def load_module_sample_inputs(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    module2_input = PROJECT_ROOT / "modules" / "module_02_orbit_interp" / "test_data" / "input_sample"
    module3_input = PROJECT_ROOT / "modules" / "module_03_attitude_interp" / "test_data" / "input_sample"

    orbit_df = pd.read_csv(module2_input / "preprocessed_orbit_sample.csv")
    imaging_time_df = pd.read_csv(module2_input / "preprocessed_imaging_time_sample.csv")
    attitude_df = pd.read_csv(module3_input / "input_attitude.csv")
    look_angle_table = pd.read_csv(module3_input / "input_look_angle.csv")

    save_csv(orbit_df, processed_dir / "preprocessed_orbit_sample.csv")
    save_csv(attitude_df, processed_dir / "preprocessed_attitude_sample.csv")
    save_csv(imaging_time_df, processed_dir / "preprocessed_imaging_time_sample.csv")
    save_csv(look_angle_table, processed_dir / "look_angle_table_sample.csv")
    return orbit_df, attitude_df, imaging_time_df, look_angle_table


def load_input_data(mode: str, processed_dir: Path) -> tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_files_exist = all(
        path.exists()
        for path in [
            RAW_ORBIT_PATH,
            RAW_ATTITUDE_PATH,
            RAW_IMAGING_TIME_PATH,
            RAW_LOOK_ANGLE_PATH,
        ]
    )

    if mode == "raw" or (mode == "auto" and raw_files_exist):
        return ("raw", *preprocess_from_raw(processed_dir))

    if mode == "raw":
        raise FileNotFoundError("Raw mode requested, but one or more raw input files are missing.")

    return ("module-sample", *load_module_sample_inputs(processed_dir))


def run_orbit_interpolation(
    orbit_df: pd.DataFrame,
    imaging_time_df: pd.DataFrame,
    processed_dir: Path,
    window_size: int,
) -> pd.DataFrame:
    from orbit_interp import interpolate_orbit

    require_columns(orbit_df, ["time", "X", "Y", "Z", "Vx", "Vy", "Vz"], "orbit data")
    require_columns(imaging_time_df, ["time"], "imaging time data")
    orbit_interp_df = interpolate_orbit(orbit_df, imaging_time_df, window_size=window_size)
    save_csv(orbit_interp_df, processed_dir / "orbit_interp_result_sample.csv")
    return orbit_interp_df


def run_attitude_processing(
    attitude_df: pd.DataFrame,
    imaging_time_df: pd.DataFrame,
    look_angle_table: pd.DataFrame,
    processed_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from attitude_interp import (
        build_rotation_matrix,
        interpolate_attitude,
        process_camera_look_angle,
    )

    require_columns(attitude_df, ["time", "q0", "q1", "q2", "q3"], "attitude data")
    require_columns(imaging_time_df, ["time"], "imaging time data")
    require_columns(look_angle_table, ["col", "psi_x", "psi_y"], "look-angle table")

    attitude_interp_df = interpolate_attitude(attitude_df, imaging_time_df)
    camera_angle_df = process_camera_look_angle(look_angle_table)
    rotation_matrix_df = build_rotation_matrix(attitude_interp_df)

    save_csv(attitude_interp_df, processed_dir / "attitude_interp_result_sample.csv")
    save_csv(camera_angle_df, processed_dir / "camera_angle_result_sample.csv")
    save_csv(rotation_matrix_df, processed_dir / "rotation_matrix_result_sample.csv")
    return attitude_interp_df, camera_angle_df, rotation_matrix_df


def adapt_rotation_for_module05(rotation_matrix_df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        f"r{row}{col}": f"R{row}{col}"
        for row in range(1, 4)
        for col in range(1, 4)
    }
    adapted = rotation_matrix_df.rename(columns=rename_map).copy()
    if "time" in adapted.columns and "scan_time" not in adapted.columns:
        adapted.insert(0, "scan_time", adapted["time"])
    return adapted


def adapt_camera_for_module05(camera_angle_df: pd.DataFrame) -> pd.DataFrame:
    adapted = camera_angle_df.copy()
    if "psi_x" not in adapted.columns and "tan_psi_x" in adapted.columns:
        adapted["psi_x"] = np.arctan(adapted["tan_psi_x"].astype(float))
    if "psi_y" not in adapted.columns and "tan_psi_y" in adapted.columns:
        adapted["psi_y"] = np.arctan(adapted["tan_psi_y"].astype(float))
    require_columns(adapted, ["col", "psi_x", "psi_y"], "module 05 camera angle data")
    return adapted[["col", "psi_x", "psi_y"]]


def make_image_points(orbit_rows: int, camera_rows: int) -> pd.DataFrame:
    row_values = np.linspace(0, max(orbit_rows - 1, 0), 5)
    col_values = np.linspace(max(camera_rows - 1, 1) * 0.25, max(camera_rows - 1, 1) * 0.75, 3)
    records = []
    point_id = 0
    for row in row_values:
        for col in col_values:
            records.append((point_id, float(row), float(col)))
            point_id += 1
    return pd.DataFrame(records, columns=["point_id", "row", "col"])


def build_pushbroom_rotation_for_module05(orbit_interp_df: pd.DataFrame) -> pd.DataFrame:
    """Build the velocity-based pushbroom camera-to-ECEF frame used by module 04."""
    records = []
    for orbit_row in orbit_interp_df.itertuples(index=False):
        satellite_position = np.array([orbit_row.X, orbit_row.Y, orbit_row.Z], dtype=float)
        satellite_velocity = np.array([orbit_row.Vx, orbit_row.Vy, orbit_row.Vz], dtype=float)

        z_axis = -satellite_position / np.linalg.norm(satellite_position)
        along_axis = satellite_velocity - np.dot(satellite_velocity, z_axis) * z_axis
        along_axis = along_axis / np.linalg.norm(along_axis)

        cross_track_axis = np.cross(along_axis, z_axis)
        cross_track_axis = cross_track_axis / np.linalg.norm(cross_track_axis)

        x_axis = -cross_track_axis
        y_axis = along_axis
        rotation_matrix = np.column_stack([x_axis, y_axis, z_axis])

        records.append(
            [
                orbit_row.time,
                rotation_matrix[0, 0],
                rotation_matrix[0, 1],
                rotation_matrix[0, 2],
                rotation_matrix[1, 0],
                rotation_matrix[1, 1],
                rotation_matrix[1, 2],
                rotation_matrix[2, 0],
                rotation_matrix[2, 1],
                rotation_matrix[2, 2],
            ]
        )

    return pd.DataFrame(
        records,
        columns=["scan_time", "R11", "R12", "R13", "R21", "R22", "R23", "R31", "R32", "R33"],
    )


def run_inverse_projection(
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    camera_angle_df: pd.DataFrame,
    processed_dir: Path,
    warnings: list[str],
) -> pd.DataFrame:
    from inverse_projection import inverse_projection

    image_points_df = make_image_points(len(orbit_interp_df), len(camera_angle_df))
    rotation_for_inverse = build_pushbroom_rotation_for_module05(orbit_interp_df)
    camera_for_inverse = adapt_camera_for_module05(camera_angle_df)

    save_csv(image_points_df, processed_dir / "image_points_sample.csv")
    inverse_projection_df = inverse_projection(
        image_points_df,
        orbit_interp_df,
        rotation_for_inverse,
        camera_for_inverse,
        reference_height=0.0,
    )
    if inverse_projection_df[["lon", "lat", "height"]].isna().any().any():
        warnings.append("Module 05 inverse_projection produced NaN values for generated image points.")

    save_csv(inverse_projection_df, processed_dir / "inverse_projection_result_sample.csv")
    return inverse_projection_df


def get_control_grid_ranges(source_rpc_params: dict | None) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    if source_rpc_params is not None:
        lon_range = (
            source_rpc_params["LONG_OFF"] - source_rpc_params["LONG_SCALE"],
            source_rpc_params["LONG_OFF"] + source_rpc_params["LONG_SCALE"],
        )
        lat_range = (
            source_rpc_params["LAT_OFF"] - source_rpc_params["LAT_SCALE"],
            source_rpc_params["LAT_OFF"] + source_rpc_params["LAT_SCALE"],
        )
        height_range = (
            source_rpc_params["HEIGHT_OFF"] - source_rpc_params["HEIGHT_SCALE"],
            source_rpc_params["HEIGHT_OFF"] + source_rpc_params["HEIGHT_SCALE"],
        )
        return lon_range, lat_range, height_range

    return (114.65, 114.85), (35.83, 35.93), (0.0, 8000.0)


def generate_grid_from_ranges(
    source_rpc_params: dict | None,
    grid_size: int,
    height_layers: int,
    processed_dir: Path,
) -> pd.DataFrame:
    from control_grid import generate_control_grid

    lon_range, lat_range, height_range = get_control_grid_ranges(source_rpc_params)
    lon_step = (lon_range[1] - lon_range[0]) / max(grid_size - 1, 1)
    lat_step = (lat_range[1] - lat_range[0]) / max(grid_size - 1, 1)
    height_step = (height_range[1] - height_range[0]) / max(height_layers - 1, 1)

    control_grid_df = generate_control_grid(
        lon_range,
        lat_range,
        height_range,
        lon_step,
        lat_step,
        height_step,
    )
    save_csv(control_grid_df, processed_dir / "control_grid_sample.csv")
    return control_grid_df


def project_with_reference_rpc(control_grid_df: pd.DataFrame, rpc_params: dict) -> pd.DataFrame:
    from rpc_solver import rpc_forward

    records = []
    for point in control_grid_df.itertuples(index=False):
        image_row, image_col = rpc_forward(point.lat, point.lon, point.height, rpc_params)
        records.append((int(point.point_id), float(image_row), float(image_col)))
    return pd.DataFrame(records, columns=["point_id", "row", "col"])


def geodetic_to_ecef(lon: float, lat: float, height: float) -> np.ndarray:
    """Convert WGS84 lon, lat, height to ECEF X, Y, Z."""
    semi_major_axis = 6378137.0
    flattening = 1.0 / 298.257223563
    eccentricity_sq = flattening * (2.0 - flattening)

    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    prime_vertical_radius = semi_major_axis / np.sqrt(1.0 - eccentricity_sq * sin_lat * sin_lat)

    x_ecef = (prime_vertical_radius + height) * cos_lat * np.cos(lon_rad)
    y_ecef = (prime_vertical_radius + height) * cos_lat * np.sin(lon_rad)
    z_ecef = (prime_vertical_radius * (1.0 - eccentricity_sq) + height) * sin_lat
    return np.array([x_ecef, y_ecef, z_ecef], dtype=float)


def rotation_row_to_matrix(rotation_row: pd.Series) -> np.ndarray:
    return np.array(
        [
            [rotation_row["r11"], rotation_row["r12"], rotation_row["r13"]],
            [rotation_row["r21"], rotation_row["r22"], rotation_row["r23"]],
            [rotation_row["r31"], rotation_row["r32"], rotation_row["r33"]],
        ],
        dtype=float,
    )


def build_yxc_camera_params(source_rpc_params: dict | None) -> dict[str, float]:
    return {
        "f": 50000.0,
        "pixel_size": 5.0,
        "row0": float(source_rpc_params["LINE_OFF"]) if source_rpc_params else 2421.0,
        "col0": float(source_rpc_params["SAMP_OFF"]) if source_rpc_params else 3690.0,
    }


def project_with_yxc_module04(
    control_grid_df: pd.DataFrame,
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    source_rpc_params: dict | None,
) -> pd.DataFrame:
    from forward_projectionyxc import calculate_forward_projection

    require_columns(control_grid_df, ["point_id", "lon", "lat", "height"], "control grid")
    require_columns(orbit_interp_df, ["X", "Y", "Z"], "orbit interpolation result")
    require_columns(
        rotation_matrix_df,
        ["r11", "r12", "r13", "r21", "r22", "r23", "r31", "r32", "r33"],
        "rotation matrix result",
    )

    orbit_positions = orbit_interp_df[["X", "Y", "Z"]].to_numpy(dtype=float)
    camera_params = build_yxc_camera_params(source_rpc_params)

    records = []
    for point in control_grid_df.itertuples(index=False):
        ground_ecef = geodetic_to_ecef(point.lon, point.lat, point.height)
        nearest_index = int(np.argmin(np.linalg.norm(orbit_positions - ground_ecef, axis=1)))
        orbit_row = orbit_interp_df.iloc[nearest_index]
        rotation_index = min(nearest_index, len(rotation_matrix_df) - 1)
        rotation_matrix = rotation_row_to_matrix(rotation_matrix_df.iloc[rotation_index])

        image_point = calculate_forward_projection(
            {"X": ground_ecef[0], "Y": ground_ecef[1], "Z": ground_ecef[2]},
            {"X": orbit_row["X"], "Y": orbit_row["Y"], "Z": orbit_row["Z"]},
            rotation_matrix,
            camera_params,
        )
        if image_point["row"] is None or image_point["col"] is None:
            records.append((int(point.point_id), np.nan, np.nan))
        else:
            records.append((int(point.point_id), float(image_point["row"]), float(image_point["col"])))

    return pd.DataFrame(records, columns=["point_id", "row", "col"])


def project_with_linear_placeholder(control_grid_df: pd.DataFrame) -> pd.DataFrame:
    from control_grid import _placeholder_forward_projection

    lon_center = float(control_grid_df["lon"].mean())
    lat_center = float(control_grid_df["lat"].mean())
    return _placeholder_forward_projection(
        control_grid_df,
        lon_center=lon_center,
        lat_center=lat_center,
        lon_pixel_scale=3.12e4,
        lat_pixel_scale=3.27e4,
        row_offset=2421,
        col_offset=3690,
    )


def try_module04_forward_projection(
    control_grid_df: pd.DataFrame,
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    camera_angle_df: pd.DataFrame,
    source_rpc_params: dict | None,
    warnings: list[str],
) -> tuple[str, pd.DataFrame] | None:
    from forward_projection import forward_projection

    camera_for_projection = camera_angle_df.copy()
    if source_rpc_params is not None:
        camera_for_projection.attrs["camera_params"] = build_yxc_camera_params(source_rpc_params)

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            result = forward_projection(
                control_grid_df,
                orbit_interp_df,
                rotation_matrix_df,
                camera_for_projection,
            )
    except Exception as exc:
        warnings.append(f"Module 04 forward_projection raised {type(exc).__name__}: {exc}")
        return None

    if result is None:
        warnings.append("Module 04 forward_projection returned None; it is still a placeholder.")
        return None

    if not isinstance(result, pd.DataFrame):
        warnings.append("Module 04 forward_projection did not return a pandas DataFrame.")
        return None

    try:
        require_columns(result, ["point_id", "row", "col"], "module 04 projection result")
    except ValueError as exc:
        warnings.append(str(exc))
        return None

    result = result[["point_id", "row", "col"]].copy()
    n_before = len(result)
    result = result.dropna(subset=["row", "col"]).reset_index(drop=True)
    n_dropped = n_before - len(result)
    if n_dropped:
        warnings.append(
            f"Module 04 forward_projection skipped {n_dropped} control points outside the imaging range."
        )
    if len(result) < 80:
        warnings.append(
            f"Module 04 forward_projection produced only {len(result)} valid points; RPC needs more samples."
        )
        return None
    return "module04", result


def try_yxc_module04_forward_projection(
    control_grid_df: pd.DataFrame,
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    source_rpc_params: dict | None,
    warnings: list[str],
) -> tuple[str, pd.DataFrame] | None:
    try:
        result = project_with_yxc_module04(
            control_grid_df,
            orbit_interp_df,
            rotation_matrix_df,
            source_rpc_params,
        )
    except Exception as exc:
        warnings.append(f"Module 04 forward_projectionyxc raised {type(exc).__name__}: {exc}")
        return None

    if result[["row", "col"]].isna().any().any():
        warnings.append("Module 04 forward_projectionyxc produced NaN row/col values.")
        return None
    warnings.append(
        "Used module 04 forward_projectionyxc.py through an adapter; its interface differs from the project "
        "forward_projection() contract and it uses nearest orbit state plus fixed camera parameters."
    )
    return "module04-yxc", result


def run_forward_projection_for_rpc_samples(
    projection_mode: str,
    control_grid_df: pd.DataFrame,
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    camera_angle_df: pd.DataFrame,
    source_rpc_params: dict | None,
    processed_dir: Path,
    warnings: list[str],
) -> tuple[str, pd.DataFrame]:
    if projection_mode in {"auto", "module04"}:
        module04_result = try_module04_forward_projection(
            control_grid_df,
            orbit_interp_df,
            rotation_matrix_df,
            camera_angle_df,
            source_rpc_params,
            warnings,
        )
        if module04_result is None:
            module04_result = try_yxc_module04_forward_projection(
                control_grid_df,
                orbit_interp_df,
                rotation_matrix_df,
                source_rpc_params,
                warnings,
            )
        if module04_result is not None:
            projection_source, forward_projection_df = module04_result
            save_csv(forward_projection_df, processed_dir / "forward_projection_result_sample.csv")
            return projection_source, forward_projection_df
        if projection_mode == "module04":
            raise RuntimeError("Module 04 projection was requested, but no valid result was produced.")

    if projection_mode in {"auto", "reference-rpc"} and source_rpc_params is not None:
        forward_projection_df = project_with_reference_rpc(control_grid_df, source_rpc_params)
        save_csv(forward_projection_df, processed_dir / "forward_projection_result_sample.csv")
        warnings.append("Used data/raw/zy3_rpc.txt as the projection source because module 04 is not runnable.")
        return "reference-rpc", forward_projection_df

    if projection_mode == "reference-rpc":
        raise FileNotFoundError("Reference RPC projection requested, but data/raw/zy3_rpc.txt is unavailable.")

    forward_projection_df = project_with_linear_placeholder(control_grid_df)
    save_csv(forward_projection_df, processed_dir / "forward_projection_result_sample.csv")
    warnings.append("Used module 05 linear placeholder projection; this is runnable but not physically strict.")
    return "linear-placeholder", forward_projection_df


def run_rpc_sampling(
    projection_mode: str,
    orbit_interp_df: pd.DataFrame,
    rotation_matrix_df: pd.DataFrame,
    camera_angle_df: pd.DataFrame,
    source_rpc_params: dict | None,
    processed_dir: Path,
    grid_size: int,
    height_layers: int,
    warnings: list[str],
) -> tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from control_grid import generate_rpc_sample

    control_grid_df = generate_grid_from_ranges(
        source_rpc_params,
        grid_size=grid_size,
        height_layers=height_layers,
        processed_dir=processed_dir,
    )
    projection_source, forward_projection_df = run_forward_projection_for_rpc_samples(
        projection_mode,
        control_grid_df,
        orbit_interp_df,
        rotation_matrix_df,
        camera_angle_df,
        source_rpc_params,
        processed_dir,
        warnings,
    )
    rpc_sample_points_df = generate_rpc_sample(control_grid_df, forward_projection_df)
    save_csv(rpc_sample_points_df, processed_dir / "rpc_sample_points_sample.csv")
    return projection_source, control_grid_df, forward_projection_df, rpc_sample_points_df


def make_reference_check_points(
    source_rpc_params: dict,
    grid_size: int,
    height_layers: int,
    processed_dir: Path,
) -> pd.DataFrame:
    lon_range, lat_range, height_range = get_control_grid_ranges(source_rpc_params)
    lon_values = np.linspace(lon_range[0], lon_range[1], max(grid_size - 1, 3))
    lat_values = np.linspace(lat_range[0], lat_range[1], max(grid_size - 1, 3))
    height_values = np.linspace(height_range[0], height_range[1], max(height_layers - 1, 2))

    records = []
    point_id = 0
    for height in height_values:
        for lat in lat_values:
            for lon in lon_values:
                records.append((point_id, lon, lat, height))
                point_id += 1

    ground_df = pd.DataFrame(records, columns=["point_id", "lon", "lat", "height"])
    image_df = project_with_reference_rpc(ground_df, source_rpc_params)
    check_points_df = ground_df.merge(image_df, on="point_id", how="inner")
    save_csv(check_points_df, processed_dir / "check_points_sample.csv")
    return check_points_df


def save_accuracy_result(accuracy_result: np.ndarray, output_path: Path) -> pd.DataFrame:
    accuracy_df = pd.DataFrame(
        accuracy_result,
        columns=["point_id", "row_error", "col_error", "plane_error"],
    )
    accuracy_df["point_id"] = accuracy_df["point_id"].astype(int)
    save_csv(accuracy_df, output_path)
    return accuracy_df


def evaluate_projection_against_reference_rpc(
    rpc_sample_points_df: pd.DataFrame,
    source_rpc_params: dict | None,
) -> dict[str, float] | None:
    if source_rpc_params is None or len(rpc_sample_points_df) == 0:
        return None

    from rpc_solver import rpc_forward

    row_errors = []
    col_errors = []
    for point in rpc_sample_points_df.itertuples(index=False):
        ref_row, ref_col = rpc_forward(point.lat, point.lon, point.height, source_rpc_params)
        row_errors.append(float(point.row - ref_row))
        col_errors.append(float(point.col - ref_col))

    row_errors = np.asarray(row_errors)
    col_errors = np.asarray(col_errors)
    plane_errors = np.sqrt(row_errors * row_errors + col_errors * col_errors)
    return {
        "count": int(len(plane_errors)),
        "rmse_row": float(np.sqrt(np.mean(row_errors * row_errors))),
        "rmse_col": float(np.sqrt(np.mean(col_errors * col_errors))),
        "rmse_plane": float(np.sqrt(np.mean(plane_errors * plane_errors))),
        "max_plane": float(np.max(plane_errors)),
        "median_plane": float(np.median(plane_errors)),
    }


def run_rpc_solution_and_accuracy(
    rpc_sample_points_df: pd.DataFrame,
    source_rpc_params: dict | None,
    projection_source: str,
    processed_dir: Path,
    result_dir: Path,
    grid_size: int,
    height_layers: int,
) -> tuple[dict, pd.DataFrame, pd.DataFrame | None]:
    from accuracy_eval import evaluate_accuracy
    from rpc_solver import save_rpc_result, solve_rpc

    result_dir.mkdir(parents=True, exist_ok=True)
    rpc_params = solve_rpc(rpc_sample_points_df)
    save_rpc_result(rpc_params, result_dir / "rpc_params_sample.txt")

    internal_accuracy = evaluate_accuracy(rpc_params, rpc_sample_points_df)
    internal_accuracy_df = save_accuracy_result(
        internal_accuracy,
        result_dir / "accuracy_result_sample.csv",
    )

    external_accuracy_df = None
    if source_rpc_params is not None and projection_source == "reference-rpc":
        check_points_df = make_reference_check_points(
            source_rpc_params,
            grid_size=grid_size,
            height_layers=height_layers,
            processed_dir=processed_dir,
        )
        external_accuracy = evaluate_accuracy(rpc_params, check_points_df)
        external_accuracy_df = save_accuracy_result(
            external_accuracy,
            result_dir / "accuracy_external_result_sample.csv",
        )

    return rpc_params, internal_accuracy_df, external_accuracy_df


def load_reference_rpc_params() -> dict | None:
    if not RAW_REFERENCE_RPC_PATH.exists():
        return None
    from rpc_solver import parse_rpc_file

    return parse_rpc_file(RAW_REFERENCE_RPC_PATH)


def write_run_report(
    path: Path,
    input_mode: str,
    projection_source: str,
    counts: dict[str, int],
    warnings: list[str],
    internal_accuracy_df: pd.DataFrame,
    external_accuracy_df: pd.DataFrame | None,
    reference_projection_stats: dict[str, float] | None = None,
) -> None:
    internal_rmse = float(np.sqrt(np.mean(internal_accuracy_df["plane_error"] ** 2)))
    lines = [
        "Photogrammetry RPC pipeline run report",
        "",
        f"input_mode: {input_mode}",
        f"projection_source: {projection_source}",
        "",
        "row_counts:",
    ]
    for key, value in counts.items():
        lines.append(f"  {key}: {value}")

    lines.extend(["", f"internal_plane_rmse_pixels: {internal_rmse:.6f}"])
    if external_accuracy_df is not None:
        external_rmse = float(np.sqrt(np.mean(external_accuracy_df["plane_error"] ** 2)))
        lines.append(f"external_plane_rmse_pixels: {external_rmse:.6f}")
    if reference_projection_stats is not None:
        lines.extend(
            [
                "",
                "module04_vs_reference_rpc:",
                f"  count: {int(reference_projection_stats['count'])}",
                f"  rmse_row_pixels: {reference_projection_stats['rmse_row']:.6f}",
                f"  rmse_col_pixels: {reference_projection_stats['rmse_col']:.6f}",
                f"  rmse_plane_pixels: {reference_projection_stats['rmse_plane']:.6f}",
                f"  median_plane_pixels: {reference_projection_stats['median_plane']:.6f}",
                f"  max_plane_pixels: {reference_projection_stats['max_plane']:.6f}",
            ]
        )

    lines.extend(["", "notes:"])
    if warnings:
        lines.extend(f"  - {warning}" for warning in warnings)
    else:
        lines.append("  - none")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the integrated photogrammetry RPC pipeline.")
    parser.add_argument(
        "--mode",
        choices=["auto", "raw", "module-sample"],
        default="auto",
        help="Input source. auto prefers data/raw and falls back to module test samples.",
    )
    parser.add_argument(
        "--projection",
        choices=["auto", "module04", "reference-rpc", "linear-placeholder"],
        default="auto",
        help="Projection source used to make RPC samples.",
    )
    parser.add_argument("--window-size", type=int, default=4, help="Orbit interpolation window size.")
    parser.add_argument("--grid-size", type=int, default=7, help="Control grid count in lon/lat directions.")
    parser.add_argument("--height-layers", type=int, default=5, help="Control grid height layer count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_import_paths()

    if args.grid_size < 2:
        raise ValueError("--grid-size must be at least 2")
    if args.height_layers < 2:
        raise ValueError("--height-layers must be at least 2")

    warnings: list[str] = []
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    input_mode, orbit_df, attitude_df, imaging_time_df, look_angle_table = load_input_data(
        args.mode,
        PROCESSED_DIR,
    )
    source_rpc_params = load_reference_rpc_params()

    orbit_interp_df = run_orbit_interpolation(
        orbit_df,
        imaging_time_df,
        PROCESSED_DIR,
        window_size=args.window_size,
    )
    _, camera_angle_df, rotation_matrix_df = run_attitude_processing(
        attitude_df,
        imaging_time_df,
        look_angle_table,
        PROCESSED_DIR,
    )

    inverse_projection_df = run_inverse_projection(
        orbit_interp_df,
        rotation_matrix_df,
        camera_angle_df,
        PROCESSED_DIR,
        warnings,
    )

    projection_source, control_grid_df, forward_projection_df, rpc_sample_points_df = run_rpc_sampling(
        args.projection,
        orbit_interp_df,
        rotation_matrix_df,
        camera_angle_df,
        source_rpc_params,
        PROCESSED_DIR,
        grid_size=args.grid_size,
        height_layers=args.height_layers,
        warnings=warnings,
    )

    _, internal_accuracy_df, external_accuracy_df = run_rpc_solution_and_accuracy(
        rpc_sample_points_df,
        source_rpc_params,
        projection_source,
        PROCESSED_DIR,
        RESULT_DIR,
        grid_size=args.grid_size,
        height_layers=args.height_layers,
    )
    reference_projection_stats = evaluate_projection_against_reference_rpc(
        rpc_sample_points_df,
        source_rpc_params,
    )

    counts = {
        "preprocessed_orbit": len(orbit_df),
        "preprocessed_attitude": len(attitude_df),
        "imaging_times": len(imaging_time_df),
        "orbit_interp": len(orbit_interp_df),
        "camera_angles": len(camera_angle_df),
        "control_grid": len(control_grid_df),
        "forward_projection": len(forward_projection_df),
        "rpc_samples": len(rpc_sample_points_df),
        "internal_accuracy": len(internal_accuracy_df),
        "external_accuracy": 0 if external_accuracy_df is None else len(external_accuracy_df),
    }
    write_run_report(
        RESULT_DIR / "pipeline_report.txt",
        input_mode,
        projection_source,
        counts,
        warnings,
        internal_accuracy_df,
        external_accuracy_df,
        reference_projection_stats,
    )

    print("=" * 72)
    print("Integrated pipeline finished")
    print(f"Input mode: {input_mode}")
    print(f"Projection source: {projection_source}")
    print(f"Processed outputs: {PROCESSED_DIR}")
    print(f"Result outputs: {RESULT_DIR}")
    if warnings:
        print("Notes:")
        for warning in warnings:
            print(f"  - {warning}")
    print("=" * 72)


if __name__ == "__main__":
    main()
