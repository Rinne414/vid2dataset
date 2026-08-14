# vid2dataset 1.3.1

## 小白怎么用

1. 下载 **`vid2dataset.exe`**（Windows）
2. **双击**
3. 选视频文件夹 → 选输出文件夹 → 点提取

Linux：解压源码后运行 `chmod +x start.sh && ./start.sh`

## GPU（Windows 和 Linux 都能用）

- **Windows .exe**：勾选「GPU 加速」。第一次会下载 CUDA 版 PyTorch（约 2.5 GB），之后用缓存。
- **Linux**：先 `./venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu126`，再勾选 GPU。
- **没装 CUDA 也能提取**，不会再报 `No module named 'torch'` 然后中止。

第一次请先关掉「自动打标」，确认出图后再开。

## How to start

Windows: download **vid2dataset.exe** → double-click.  
Linux: `./start.sh` (install venv once if prompted).

GPU works on both OS (NVIDIA). Missing torch no longer blocks extract.
