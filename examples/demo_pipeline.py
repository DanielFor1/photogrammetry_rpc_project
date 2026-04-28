"""
demo_pipeline.py

本文件仅用于说明后续主流程可能的调用顺序。
当前阶段各模块先单独完成和测试，最终由组长统一整合。
"""


def demo_pipeline():
    print("示例流程：")
    print("1. load_raw_data()")
    print("2. j2000_to_ecef()")
    print("3. interpolate_orbit()")
    print("4. interpolate_attitude()")
    print("5. build_rotation_matrix()")
    print("6. forward_projection()")
    print("7. inverse_projection()")
    print("8. generate_control_grid()")
    print("9. generate_rpc_sample()")
    print("10. solve_rpc()")
    print("11. evaluate_accuracy()")


if __name__ == "__main__":
    demo_pipeline()
