# vid2dataset 1.3.2

程序内「检查更新 → 安装更新」现在会先校验下载的文件，和发布页对不上就不安装。The in-app updater now checks a downloaded update against the release before installing it.

## 更新内容 / What changed

- **更新先校验 / Updates are verified**: 下载的新版 exe 的大小和 SHA256 必须与发布页一致（GitHub 提供的校验值，或本页的 `SHA256SUMS.txt`）。对不上、或发布页没有校验值时，下载的文件会被删除、什么都不安装，并提示你到发布页手动下载。
  - The downloaded exe must match the release's size and SHA256 (GitHub's published digest, or `SHA256SUMS.txt` on this page). If it does not match, or the release has no checksum, the download is deleted, nothing is installed, and the app points you to this page for a manual download.
- **发布页附校验文件 / Checksum file on every release**: `SHA256SUMS.txt` lists the SHA256 of `vid2dataset.exe` and the zip, so you can also check a manual download yourself.

## 升级注意 / Upgrading

1.3.1 及更早版本的更新按钮还没有校验功能。这次可以照常用「检查更新」升级，也可以从本页手动下载；从 1.3.2 开始，之后的每次更新都会先校验。

Versions 1.3.1 and older do not verify yet. Update to 1.3.2 as usual (Check for Updates, or download from this page); every update after 1.3.2 is verified first.

## 下载哪个 / Which file to download

- **`vid2dataset.exe`**: 下载后双击即可。 / Download and double-click.
- **`vid2dataset-1.3.2-windows.zip`**: 解压后双击 `双击启动.bat` 或 `START.bat`。 / Extract, then double-click `START.bat` or `双击启动.bat`.
- **`SHA256SUMS.txt`**: 校验值，不用下载。 / Checksums; you do not need to download it.

如果弹出「Windows 已保护你的电脑」：点 **更多信息** → **仍要运行**。If Windows SmartScreen appears: **More info** → **Run anyway**.

Linux: `chmod +x start.sh && ./start.sh`
