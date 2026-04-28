# 数据格式规范

## 一、CSV 字段命名

CSV 字段统一使用英文，不使用中文字段名。

## 二、常用字段

| 字段名 | 含义 |
|---|---|
| time | 时间 |
| lon | 经度 |
| lat | 纬度 |
| height | 高程 |
| X, Y, Z | 三维直角坐标分量 |
| Vx, Vy, Vz | 卫星速度分量 |
| q0, q1, q2, q3 | 四元数 |
| row | 像方行坐标 |
| col | 像方列坐标 |
| point_id | 点号 |
| row_error | 行方向误差 |
| col_error | 列方向误差 |
| plane_error | 平面误差 |

## 三、注意事项

1. 像方坐标统一使用 `row, col`。
2. 经纬高顺序统一使用 `lon, lat, height`。
3. 三维直角坐标分量统一使用 `X, Y, Z`。
4. 每个模块如果使用了其他字段，需要在 `module_readme.md` 中说明。
