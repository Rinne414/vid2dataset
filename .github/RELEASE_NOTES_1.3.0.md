# vid2dataset 1.3.0

## 小白怎么用（不用会写代码）

1. 下载下面的 **`vid2dataset.exe`**
2. **双击**它
3. 选视频文件夹 → 选输出文件夹 → 点「提取」

如果 Windows 弹出「已保护你的电脑」：点 **更多信息** → **仍要运行**。

第一次请先 **关掉「GPU 加速」** 和 **「自动打标」**，确认能出图后再开。

---

## How to start (no Python, no install)

1. Download **`vid2dataset.exe`** below
2. **Double-click** it
3. Pick a video folder → pick an output folder → click Extract

SmartScreen? **More info** → **Run anyway**.

Leave **GPU acceleration** and **Auto-tag** off on the first run.

---

## Also in this release

- Clear start files in the source tree: `START.bat` / `双击启动.bat` / `HOW_TO_START.txt`
- GPU missing PyTorch no longer blocks extract (falls back to CPU)
- Optional new Tauri desktop UI for developers (`scripts/run_tauri.py dev`)
