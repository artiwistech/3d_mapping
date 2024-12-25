import os
import numpy as np
import panel as pn
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

    # 已知點 (非 NaN) 的 (y, x) 與數值
    pts = np.column_stack((y_coord[valid_mask], x_coord[valid_mask]))
    vals = height_map[valid_mask]

    # 要插值的所有點
    all_pts = np.column_stack((y_coord.ravel(), x_coord.ravel()))

    # 1) linear interpolation
    filled_vals = griddata(pts, vals, all_pts, method='linear')

    # 2) 對插值後仍是 NaN 的再用 nearest
    missing_mask = np.isnan(filled_vals)
    if np.any(missing_mask):
        nearest_vals = griddata(pts, vals, all_pts[missing_mask], method='nearest')
        filled_vals[missing_mask] = nearest_vals

    return filled_vals.reshape(H, W)

def main():
    # 假設檔案規格
    filename = "LAYER_0.raw"
    WIDTH, HEIGHT = 1224, 1024

    # --- 第 1 步：讀取檔案 (小端序 float32) ---
    file_size = os.path.getsize(filename)
    print(f"File size: {file_size} bytes")

    with open(filename, "rb") as f:
        raw_data = f.read()

    # 嘗試只取 (HEIGHT*WIDTH)*4 bytes，避免尾端雜訊
    needed_size = HEIGHT * WIDTH * 4
    if len(raw_data) < needed_size:
        print(f"Warning: 檔案長度不足預期 ({needed_size}), 可能有破損或需要 offset!")
        # 也可以嘗試退出程式、或只讀可用部分
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
    # (x, y) 為平面座標, arr_filled[y, x] 為 Z
    x = np.arange(WIDTH)
    y = np.arange(HEIGHT)
    X, Y = np.meshgrid(x, y)
    Z = arr_filled

    points = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    grid = pv.StructuredGrid()
    grid.points = points
    # dimension: (nx, ny, nz) => (WIDTH, HEIGHT, 1)
    grid.dimensions = [WIDTH, HEIGHT, 1]

    # --- 第 4 步：啟動 headless X (若無桌面環境) ---
    # 若你在無頭環境，可使用:
    pv.start_xvfb()

    # 建立 Plotter(off_screen=True)
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(grid, cmap='terrain', show_edges=False)
    plotter.add_axes()
    plotter.show_bounds()
    plotter.view_isometric()
    plotter.screenshot('test.png')

    # 取得 viewer 供 Panel 用
    viewer = plotter.show(
        return_viewer=True,     # 回傳可嵌入於 Panel 的 viewer
        jupyter_backend='panel',
        window_size=(1000, 800)
    )

    # --- 第 5 步：用 Panel 啟動網頁服務 ---
    # 指定 port, address, 以及 allow_websocket_origin 等
    # 若你要外網存取，請在雲主機防火牆開放相應 port。
    # 如果你的伺服器 IP 是 123.45.67.89，就可以在瀏覽器上
    # 打 http://123.45.67.89:5006 即可看到 3D 介面。
    pn.serve(
        viewer,
        port=5006,
        address="0.0.0.0",
        allow_websocket_origin=["*"],  # 或 ["123.45.67.89:5006"] 比較安全
        show=False
    )

if __name__ == "__main__":
    main()