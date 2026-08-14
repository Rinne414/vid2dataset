# vid2dataset 1.3.1

## 小白怎么用（Windows）

### 方法 1：只下一个 exe（最快）

1. 在本页下方下载 **`vid2dataset.exe`**
2. **双击**它
3. 选视频文件夹 → 选输出文件夹 → 点「提取」

如果弹出「Windows 已保护你的电脑」：点 **更多信息** → **仍要运行**。

### 方法 2：下载 zip 压缩包（推荐给不熟悉 exe 的人）

1. 在本页下方下载 **`vid2dataset-1.3.1-windows.zip`**
2. 右键 zip → **全部解压缩**（Extract All），解到桌面或任意文件夹
3. 打开解压出来的文件夹，你会看到：
   - `vid2dataset.exe`
   - `START.bat` / `双击启动.bat`
   - `HOW_TO_START.txt`
4. **双击 `双击启动.bat`**（或 `START.bat`，或直接双击 exe）
5. 以后都进这个文件夹再双击。不要只把 exe 单独拖走。

打开软件后：选输入 → 选输出 → 点提取。  
窗口右上角有 **「检查更新」**，以后有新版本可以一键更新。

第一次请先关掉「自动打标」，确认出图后再开。

Linux：源码里运行 `chmod +x start.sh && ./start.sh`

## GPU（Windows 和 Linux 都能用）

- **Windows .exe**：勾选「GPU 加速」。第一次会下载 CUDA 版 PyTorch（约 2.5 GB），之后用缓存。
- **Linux**：先 `./venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu126`，再勾选 GPU。
- **没装 CUDA 也能提取**，不会再报 `No module named 'torch'` 然后中止。

第一次请先关掉「自动打标」，确认出图后再开。

## How to start

**Method 1:** download **`vid2dataset.exe`** → double-click.

**Method 2:** download **`vid2dataset-1.3.1-windows.zip`** → Extract All → open the folder → double-click **`START.bat`** or **`双击启动.bat`**.

The app has **Check for Updates** in the top-right.

Linux: `./start.sh` (install venv once if prompted).

GPU works on both OS (NVIDIA). Missing torch no longer blocks extract.
