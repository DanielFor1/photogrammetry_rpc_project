"""
forward_projection.py

Strict imaging model forward projection module.

This file exposes the project-standard interface:
    forward_projection(ground_points, orbit_interp_result, rotation_matrix_result, camera_angle_result)

It incorporates the implementation idea from forward_projectionyxc.py and wraps it
so upstream and downstream modules can call module 04 directly.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_CAMERA_PARAMS = {
    "f": 50000.0,
    "pixel_size": 5.0,
    "row0": 10000.0,
    "col0": 10000.0,
}


def geodetic_to_ecef(lon: float, lat: float, height: float) -> np.ndarray:
    """Convert WGS84 geodetic coordinates to ECEF coordinates."""
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


def calculate_forward_projection(ground_point, orbit_result, attitude_result, camera_params):
    """
    Project one ground point to image coordinates with the collinearity equation.

    Parameters
    ----------
    ground_point : dict
        ECEF ground point with keys X, Y, Z.
    orbit_result : dict
        Satellite ECEF position with keys X, Y, Z.
    attitude_result : ndarray
        3x3 rotation matrix from ECEF/object vector to camera coordinates.
    camera_params : dict
        f, pixel_size, row0, col0.

    Returns
    -------
    dict
        row, col.
    """
    vector_obj = np.array(
        [
            ground_point["X"] - orbit_result["X"],
            ground_point["Y"] - orbit_result["Y"],
            ground_point["Z"] - orbit_result["Z"],
        ],
        dtype=float,
    )

    rotation_matrix = np.asarray(attitude_result, dtype=float)
    vector_cam = rotation_matrix @ vector_obj
    if np.isclose(vector_cam[2], 0.0):
        return {"row": np.nan, "col": np.nan}

    focal_length = float(camera_params["f"])
    pixel_size = float(camera_params["pixel_size"])
    row0 = float(camera_params["row0"])
    col0 = float(camera_params["col0"])

    image_x = -focal_length * (vector_cam[0] / vector_cam[2])
    image_y = -focal_length * (vector_cam[1] / vector_cam[2])

    col = col0 + image_x / pixel_size
    row = row0 - image_y / pixel_size
    return {"row": row, "col": col}


def _require_columns(df: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _normalize_ground_points(ground_points: pd.DataFrame) -> pd.DataFrame:
    points = ground_points.copy()
    if "point_id" not in points.columns:
        points.insert(0, "point_id", np.arange(len(points), dtype=int))

    if {"X", "Y", "Z"}.issubset(points.columns):
        return points

    _require_columns(points, ["lon", "lat", "height"], "ground_points")
    ecef = np.vstack(
        [
            geodetic_to_ecef(float(row.lon), float(row.lat), float(row.height))
            for row in points.itertuples(index=False)
        ]
    )
    points["X"] = ecef[:, 0]
    points["Y"] = ecef[:, 1]
    points["Z"] = ecef[:, 2]
    return points


def _extract_satellite_positions(orbit_interp_result: pd.DataFrame) -> pd.DataFrame:
    orbit_df = orbit_interp_result.copy()
    if {"sat_X", "sat_Y", "sat_Z"}.issubset(orbit_df.columns):
        orbit_df = orbit_df.rename(columns={"sat_X": "X", "sat_Y": "Y", "sat_Z": "Z"})

    _require_columns(orbit_df, ["X", "Y", "Z"], "orbit_interp_result")
    return orbit_df.reset_index(drop=True)


def _extract_rotation_matrix(row: pd.Series) -> np.ndarray:
    if {"r11", "r12", "r13", "r21", "r22", "r23", "r31", "r32", "r33"}.issubset(row.index):
        prefix = "r"
    elif {"R11", "R12", "R13", "R21", "R22", "R23", "R31", "R32", "R33"}.issubset(row.index):
        prefix = "R"
    elif {"m11", "m12", "m13", "m21", "m22", "m23", "m31", "m32", "m33"}.issubset(row.index):
        prefix = "m"
    else:
        raise ValueError("rotation_matrix_result missing r11..r33/R11..R33/m11..m33 columns")

    return np.array(
        [
            [row[f"{prefix}11"], row[f"{prefix}12"], row[f"{prefix}13"]],
            [row[f"{prefix}21"], row[f"{prefix}22"], row[f"{prefix}23"]],
            [row[f"{prefix}31"], row[f"{prefix}32"], row[f"{prefix}33"]],
        ],
        dtype=float,
    )


def _get_camera_params(camera_angle_result: pd.DataFrame | None) -> dict[str, float]:
    camera_params = DEFAULT_CAMERA_PARAMS.copy()
    if camera_angle_result is None:
        return camera_params

    attr_params = getattr(camera_angle_result, "attrs", {}).get("camera_params")
    if isinstance(attr_params, dict):
        camera_params.update({key: float(value) for key, value in attr_params.items() if key in camera_params})

    if isinstance(camera_angle_result, pd.DataFrame) and len(camera_angle_result) > 0:
        first_row = camera_angle_result.iloc[0]
        for key in camera_params:
            if key in camera_angle_result.columns:
                camera_params[key] = float(first_row[key])

    return camera_params


def _extract_camera_angle_table(camera_angle_result: pd.DataFrame | None) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    if camera_angle_result is None or not isinstance(camera_angle_result, pd.DataFrame):
        return None
    if "col" not in camera_angle_result.columns:
        return None

    camera_df = camera_angle_result.copy()
    if "tan_psi_x" not in camera_df.columns and "psi_x" in camera_df.columns:
        camera_df["tan_psi_x"] = np.tan(camera_df["psi_x"].astype(float))
    if "tan_psi_y" not in camera_df.columns and "psi_y" in camera_df.columns:
        camera_df["tan_psi_y"] = np.tan(camera_df["psi_y"].astype(float))
    if "tan_psi_x" not in camera_df.columns:
        return None
    if "tan_psi_y" not in camera_df.columns:
        camera_df["tan_psi_y"] = 0.0

    return (
        camera_df["col"].to_numpy(dtype=float),
        camera_df["tan_psi_x"].to_numpy(dtype=float),
        camera_df["tan_psi_y"].to_numpy(dtype=float),
    )


def _build_velocity_camera_frames(orbit_df: pd.DataFrame) -> np.ndarray:
    _require_columns(orbit_df, ["X", "Y", "Z", "Vx", "Vy", "Vz"], "orbit_interp_result")
    positions = orbit_df[["X", "Y", "Z"]].to_numpy(dtype=float)
    velocities = orbit_df[["Vx", "Vy", "Vz"]].to_numpy(dtype=float)

    frames = []
    for satellite_position, satellite_velocity in zip(positions, velocities):
        z_axis = -satellite_position / np.linalg.norm(satellite_position)
        along_axis = satellite_velocity - np.dot(satellite_velocity, z_axis) * z_axis
        along_axis = along_axis / np.linalg.norm(along_axis)

        cross_track_axis = np.cross(along_axis, z_axis)
        cross_track_axis = cross_track_axis / np.linalg.norm(cross_track_axis)

        # ZY-3 NAD CBR psi_x increases toward the negative cross-track direction.
        x_axis = -cross_track_axis
        y_axis = along_axis
        frames.append(np.column_stack([x_axis, y_axis, z_axis]))

    return np.asarray(frames)


def _project_pushbroom_point(
    ground_ecef: np.ndarray,
    positions: np.ndarray,
    camera_to_ecef_frames: np.ndarray,
    col_values: np.ndarray,
    tan_psi_x: np.ndarray,
    tan_psi_y: np.ndarray,
) -> tuple[float, float]:
    sort_index = np.argsort(tan_psi_x)
    tan_x_sorted = tan_psi_x[sort_index]
    col_sorted = col_values[sort_index]

    object_vectors = ground_ecef - positions
    unit_vectors = object_vectors / np.linalg.norm(object_vectors, axis=1)[:, None]
    camera_vectors = np.einsum(
        "nij,nj->ni",
        np.transpose(camera_to_ecef_frames, (0, 2, 1)),
        unit_vectors,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio_x = camera_vectors[:, 0] / camera_vectors[:, 2]
        ratio_y = camera_vectors[:, 1] / camera_vectors[:, 2]

    valid = (
        (camera_vectors[:, 2] > 0.0)
        & (ratio_x >= tan_x_sorted[0])
        & (ratio_x <= tan_x_sorted[-1])
    )
    if not np.any(valid):
        return np.nan, np.nan

    valid_indexes = np.flatnonzero(valid)
    valid_cols = np.interp(ratio_x[valid], tan_x_sorted, col_sorted)
    valid_tan_y = np.interp(valid_cols, col_values, tan_psi_y)
    residual = ratio_y[valid] - valid_tan_y

    zero_crossings = np.where(np.sign(residual[:-1]) * np.sign(residual[1:]) <= 0)[0]
    if len(zero_crossings) == 0:
        return np.nan, np.nan

    crossing_index = zero_crossings[
        np.argmin(np.abs(residual[zero_crossings]) + np.abs(residual[zero_crossings + 1]))
    ]
    row0 = valid_indexes[crossing_index]
    row1 = valid_indexes[crossing_index + 1]
    denom = abs(residual[crossing_index]) + abs(residual[crossing_index + 1])
    weight = 0.0 if denom == 0.0 else abs(residual[crossing_index]) / denom

    image_row = (1.0 - weight) * row0 + weight * row1
    image_col = (1.0 - weight) * valid_cols[crossing_index] + weight * valid_cols[crossing_index + 1]
    return float(image_row), float(image_col)


def _forward_projection_pushbroom(
    points: pd.DataFrame,
    orbit_df: pd.DataFrame,
    camera_angle_result: pd.DataFrame | None,
) -> pd.DataFrame | None:
    camera_table = _extract_camera_angle_table(camera_angle_result)
    if camera_table is None or not {"Vx", "Vy", "Vz"}.issubset(orbit_df.columns):
        return None

    col_values, tan_psi_x, tan_psi_y = camera_table
    positions = orbit_df[["X", "Y", "Z"]].to_numpy(dtype=float)
    camera_to_ecef_frames = _build_velocity_camera_frames(orbit_df)

    records = []
    for point in points.itertuples(index=False):
        point_id = getattr(point, "point_id")
        ground_ecef = np.array([point.X, point.Y, point.Z], dtype=float)
        image_row, image_col = _project_pushbroom_point(
            ground_ecef,
            positions,
            camera_to_ecef_frames,
            col_values,
            tan_psi_x,
            tan_psi_y,
        )
        records.append([point_id, image_row, image_col])

    return pd.DataFrame(records, columns=["point_id", "row", "col"])


def _select_orbit_index(point: pd.Series, orbit_df: pd.DataFrame, orbit_positions: np.ndarray) -> int:
    if "row" in point.index and pd.notna(point["row"]):
        return int(np.clip(round(float(point["row"])), 0, len(orbit_df) - 1))

    ground_ecef = point[["X", "Y", "Z"]].to_numpy(dtype=float)
    distances = np.linalg.norm(orbit_positions - ground_ecef, axis=1)
    return int(np.argmin(distances))


def forward_projection(ground_points, orbit_interp_result, rotation_matrix_result, camera_angle_result=None):
    """
    Project object-space ground points to image-space row/col.

    Parameters
    ----------
    ground_points : pandas.DataFrame
        Required columns: point_id, lon, lat, height or point_id, X, Y, Z.
    orbit_interp_result : pandas.DataFrame
        Required columns: X, Y, Z. If ground_points has row, that row is used as
        scan-line index; otherwise the nearest satellite position is used.
    rotation_matrix_result : pandas.DataFrame
        Required columns: r11..r33, R11..R33, or m11..m33.
    camera_angle_result : pandas.DataFrame, optional
        This yxc-based implementation does not use look angles directly. The
        DataFrame may carry camera parameters in attrs["camera_params"] or
        columns f, pixel_size, row0, col0.

    Returns
    -------
    pandas.DataFrame
        Columns: point_id, row, col.
    """
    points = _normalize_ground_points(pd.DataFrame(ground_points))
    orbit_df = _extract_satellite_positions(pd.DataFrame(orbit_interp_result))
    rotation_df = pd.DataFrame(rotation_matrix_result).reset_index(drop=True)
    if len(rotation_df) == 0:
        raise ValueError("rotation_matrix_result is empty")

    pushbroom_result = _forward_projection_pushbroom(points, orbit_df, camera_angle_result)
    if pushbroom_result is not None:
        return pushbroom_result

    orbit_positions = orbit_df[["X", "Y", "Z"]].to_numpy(dtype=float)
    camera_params = _get_camera_params(camera_angle_result)

    records = []
    for point in points.itertuples(index=False):
        point_series = pd.Series(point._asdict())
        orbit_index = _select_orbit_index(point_series, orbit_df, orbit_positions)
        rotation_index = min(orbit_index, len(rotation_df) - 1)

        orbit_row = orbit_df.iloc[orbit_index]
        rotation_matrix = _extract_rotation_matrix(rotation_df.iloc[rotation_index])
        image_point = calculate_forward_projection(
            {"X": point_series["X"], "Y": point_series["Y"], "Z": point_series["Z"]},
            {"X": orbit_row["X"], "Y": orbit_row["Y"], "Z": orbit_row["Z"]},
            rotation_matrix,
            camera_params,
        )

        records.append(
            [
                point_series["point_id"],
                image_point["row"],
                image_point["col"],
            ]
        )

    forward_projection_result = pd.DataFrame(records, columns=["point_id", "row", "col"])
    return forward_projection_result


def batch_forward_projection(input_path, output_path, camera_params=None):
    """
    Batch helper compatible with the yxc submission's merged CSV format.
    """
    data_df = pd.read_csv(input_path)
    camera_params = DEFAULT_CAMERA_PARAMS.copy() if camera_params is None else {**DEFAULT_CAMERA_PARAMS, **camera_params}

    ground_points = data_df[["X", "Y", "Z"]].copy()
    ground_points.insert(0, "point_id", np.arange(len(ground_points), dtype=int))
    orbit_df = pd.DataFrame(
        {
            "X": data_df["sat_X"],
            "Y": data_df["sat_Y"],
            "Z": data_df["sat_Z"],
        }
    )
    matrix_columns = ["m11", "m12", "m13", "m21", "m22", "m23", "m31", "m32", "m33"]
    if set(matrix_columns).issubset(data_df.columns):
        rotation_df = data_df[matrix_columns]
    else:
        rotation_df = pd.DataFrame(
            np.tile(np.eye(3).reshape(1, 9), (len(data_df), 1)),
            columns=matrix_columns,
        )
    camera_df = pd.DataFrame([camera_params])

    projection_result = forward_projection(ground_points, orbit_df, rotation_df, camera_df)
    output_df = pd.concat([data_df.reset_index(drop=True), projection_result[["row", "col"]]], axis=1)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)
    print(f"Forward projection completed. Saved to {output_path}")
    return output_df


if __name__ == "__main__":
    print("模块 04：forward_projection.py 单独测试入口")
    base_dir = Path(__file__).resolve().parents[1]
    input_path = base_dir / "test_data" / "input_sample" / "input.csv"
    output_path = base_dir / "test_data" / "output_sample" / "output.csv"
    if input_path.exists():
        batch_forward_projection(input_path, output_path)
    else:
        print(f"测试输入不存在：{input_path}")
