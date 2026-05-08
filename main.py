"""
Main entry for the satellite photogrammetry assignment.

This file only coordinates the workflow. Detailed data parsing, schema
adaptation, and report writing live in modules/pipeline_runner.py so the main
program reads like the assignment module chain.
"""

from modules.pipeline_runner import (
    PROCESSED_DIR,
    RESULT_DIR,
    ensure_import_paths,
    evaluate_projection_against_reference_rpc,
    load_input_data,
    load_reference_rpc_params,
    parse_args,
    run_attitude_processing,
    run_inverse_projection,
    run_orbit_interpolation,
    run_rpc_sampling,
    run_rpc_solution_and_accuracy,
    write_run_report,
)


def main() -> None:
    args = parse_args()
    ensure_import_paths()

    if args.grid_size < 2:
        raise ValueError("--grid-size must be at least 2")
    if args.height_layers < 2:
        raise ValueError("--height-layers must be at least 2")

    notes: list[str] = []
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    # Module 01: raw data preprocessing and coordinate-related normalization.
    input_mode, orbit_df, attitude_df, imaging_time_df, look_angle_table = load_input_data(
        args.mode,
        PROCESSED_DIR,
    )
    source_rpc_params = load_reference_rpc_params()

    # Module 02: orbit interpolation at each imaging time.
    orbit_interp_df = run_orbit_interpolation(
        orbit_df,
        imaging_time_df,
        PROCESSED_DIR,
        window_size=args.window_size,
    )

    # Module 03: attitude interpolation, camera look angle table, rotation matrix.
    _, camera_angle_df, rotation_matrix_df = run_attitude_processing(
        attitude_df,
        imaging_time_df,
        look_angle_table,
        PROCESSED_DIR,
    )

    # Module 05: inverse projection demo output for image points.
    run_inverse_projection(
        orbit_interp_df,
        rotation_matrix_df,
        camera_angle_df,
        PROCESSED_DIR,
        notes,
    )

    # Module 04 + Module 05: forward projection, control grid, RPC samples.
    projection_source, control_grid_df, forward_projection_df, rpc_sample_points_df = run_rpc_sampling(
        args.projection,
        orbit_interp_df,
        rotation_matrix_df,
        camera_angle_df,
        source_rpc_params,
        PROCESSED_DIR,
        grid_size=args.grid_size,
        height_layers=args.height_layers,
        warnings=notes,
    )

    # Module 06: RPC solving and accuracy evaluation.
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
        notes,
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
    if notes:
        print("Notes:")
        for note in notes:
            print(f"  - {note}")
    print("=" * 72)


if __name__ == "__main__":
    main()
