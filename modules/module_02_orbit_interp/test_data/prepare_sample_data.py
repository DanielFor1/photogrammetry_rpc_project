"""
Prepare module 02 sample input data from raw ZY3 text files.

This script is only used before module 01 is ready. The formal module 02
workflow should consume module 01 preprocessed CSV outputs directly.
"""

import csv
import re
from pathlib import Path


GPS_KEYS = ("timeCode", "PX", "PY", "PZ", "VX", "VY", "VZ")


def parse_gps_file(gps_path):
    text = gps_path.read_text(encoding="utf-8")
    blocks = re.findall(r"gpsData_\d+\s*=\s*\{(.*?)\}", text, flags=re.S)

    if not blocks:
        raise ValueError(f"No gpsData block found in {gps_path}")

    rows = []
    for block in blocks:
        values = {}
        for key in GPS_KEYS:
            match = re.search(rf"{key}\s*=\s*([-+]?\d+(?:\.\d+)?)\s*;", block)
            if match is None:
                raise ValueError(f"Missing {key} in gpsData block")
            values[key] = float(match.group(1))

        rows.append([
            values["timeCode"],
            values["PX"],
            values["PY"],
            values["PZ"],
            values["VX"],
            values["VY"],
            values["VZ"],
        ])

    return rows


def parse_imaging_time_file(imaging_time_path):
    lines = imaging_time_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"Empty imaging time file: {imaging_time_path}")

    header = lines[0].split()
    if header != ["RelLine", "Time", "deltaTime"]:
        raise ValueError(f"Unexpected imaging time header: {header}")

    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"Unexpected imaging time row: {line}")
        rows.append([float(parts[1])])

    if not rows:
        raise ValueError(f"No imaging time rows found in {imaging_time_path}")

    return rows


def write_csv(output_path, header, rows):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    module_dir = Path(__file__).resolve().parents[1]
    project_root = Path(__file__).resolve().parents[3]

    gps_path = project_root / "data" / "raw" / "DX_ZY3_NAD_gps.txt"
    imaging_time_path = project_root / "data" / "raw" / "DX_ZY3_NAD_imagingTime.txt"
    output_dir = module_dir / "test_data" / "input_sample"

    orbit_rows = parse_gps_file(gps_path)
    imaging_time_rows = parse_imaging_time_file(imaging_time_path)

    write_csv(
        output_dir / "preprocessed_orbit_sample.csv",
        ["time", "X", "Y", "Z", "Vx", "Vy", "Vz"],
        orbit_rows,
    )
    write_csv(
        output_dir / "preprocessed_imaging_time_sample.csv",
        ["time"],
        imaging_time_rows,
    )

    print(f"orbit rows: {len(orbit_rows)}")
    print(f"imaging time rows: {len(imaging_time_rows)}")
    print(f"output directory: {output_dir}")


if __name__ == "__main__":
    main()
