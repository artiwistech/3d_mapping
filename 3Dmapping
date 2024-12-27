import os
import numpy as np
import pyvista as pv
from scipy.interpolate import griddata

def inpaint_nan_griddata(height_map):
    """
    用 SciPy 的 griddata 對 2D 高度圖的 NaN 區域做插值。
    先用 'linear'，若仍有 NaN 則用 'nearest' 再補。
    """
    H, W = height_map.shape
    y_coord, x_coord = np.mgrid[0:H, 0:W]
    valid_mask = ~np.isnan(height_map)

    pts = np.column_stack((y_coord[valid_mask], x_coord[valid_mask]))
    vals = height_map[valid_mask]
    all_pts = np.column_stack((y_coord.ravel(), x_coord.ravel()))

    # 1) linear interpolation
    filled_vals = griddata(pts, vals, all_pts, method='linear')

    # 2) nearest interpolation for leftover NaNs
    missing_mask = np.isnan(filled_vals)
    if np.any(missing_mask):
        nearest_vals = griddata(pts, vals, all_pts[missing_mask], method='nearest')
        filled_vals[missing_mask] = nearest_vals

    return filled_vals.reshape(H, W)

def main():
    # 假設你要讀取的檔案
    filename = "LAYER_0.raw"   # 請改成實際檔案路徑/名稱
    WIDTH, HEIGHT = 1224, 1024

    # --- 第 1 步：讀取檔案 (小端序 float32) ---
    file_size = os.path.getsize(filename)
    print(f"File size: {file_size} bytes")

    with open(filename, "rb") as f:
        raw_data = f.read()

    needed_size = HEIGHT * WIDTH * 4
    if len(raw_data) < needed_size:
        print(f"Warning: 檔案長度不足預期 ({needed_size}), 可能有破損或需要 offset!")
    raw_data = raw_data[:needed_size]

    arr = np.frombuffer(raw_data, dtype='<f4')
    arr = arr.reshape((HEIGHT, WIDTH))

    # --- 第 2 步：插值 (inpaint) NaN ---
    nan_count = np.isnan(arr).sum()
    print("NaN 數量:", nan_count)
    if nan_count > 0:
        arr_filled = inpaint_nan_griddata(arr)
    else:
        arr_filled = arr  # 沒有 NaN 就不需要補

    # --- 第 3 步：構造 PyVista 的網格 ---
    x = np.arange(WIDTH)
    y = np.arange(HEIGHT)
    X, Y = np.meshgrid(x, y)
    Z = arr_filled

    points = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    grid = pv.StructuredGrid()
    grid.points = points
    grid.dimensions = [WIDTH, HEIGHT, 1]

    # 若在無頭 (headless) 環境，可用 start_xvfb()
    # pv.start_xvfb()

    # --- 第 4 步：在本機端顯示 ---
    plotter = pv.Plotter()
    plotter.add_mesh(grid, cmap='terrain', show_edges=False)
    plotter.add_axes()
    plotter.show_bounds()
    plotter.view_isometric()
    plotter.show()  # 本機端互動式視窗

if __name__ == "__main__":
    main()
