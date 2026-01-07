
# PDF 试卷精准切分工具 (PDF Paper Cutter)

一个基于 Python 和 PyQt6 开发的轻量级桌面工具，专门用于将**横向排版的 PDF 试卷**（常见于扫描版、练习册）精准对半切分为**纵向 A4 格式**，方便打印和阅读。

## ✨ 功能特点

* **可视化调整**：实时预览 PDF 内容，通过鼠标左右拖动红线即可精准确定切分位置。
* **点击锁定状态**：
* **红色虚线**：调整模式，随鼠标实时移动。
* **绿色实线**：锁定模式，点击预览图即可固定切割点，防止误触。


* **智能缩放**：自动将切分后的页面适配为标准 A4 纵向比例。
* **高清晰度**：采用 PyMuPDF 高性能渲染引擎，确保预览图与输出文件清晰。
* **醒目交互**：黑色高对比度状态栏，实时反馈切割比例和操作指引。

---

## 🚀 快速开始

### 方案 A：直接使用 (Windows)

1. 进入仓库的 `Actions` 页面。
2. 下载最新的 `windows-exe` 产出物。
3. 解压并运行 `PDF试卷切分工具.exe`。

### 方案 B：开发者运行 (Python)

如果你想在本地运行或二次开发：

1. **克隆仓库**
```bash
git clone https://github.com/blueflylabor/pdf_cuter.git
cd 你的仓库名

```


2. **安装依赖**
```bash
pip install PyQt6 PyMuPDF

```


3. **启动程序**
```bash
python cut_gui.py

```



---

## 📖 操作指南

1. **加载文件**：点击 **“1. 选择 PDF 文件”** 按钮。
2. **调整位置**：在预览图上移动鼠标，红线会指示切割位置。
3. **锁定切割点**：在满意的位置**点击鼠标左键**，线变为绿色，此时切割点已固定。
4. **保存导出**：点击 **“2. 导出为 A4 纵向 PDF”**，选择保存路径。
5. **重新调整**：如需修改，再次点击预览图解锁，线变回红色即可重新移动。

---

## 🛠 技术栈

* **GUI 框架**: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
* **PDF 处理**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
* **打包工具**: [PyInstaller](https://pyinstaller.org/)
* **自动化编译**: GitHub Actions (Windows-latest)

---
