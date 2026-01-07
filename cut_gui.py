import sys
import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, QMessageBox)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QSize

class PDFCutter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 试卷精准切分工具 - 锁定增强版")
        self.resize(1100, 850)

        self.doc = None
        self.temp_png = "temp_preview.png"
        self.split_ratio = 0.5 
        self.original_pixmap = None  
        self.fixed_display_size = None 
        self.is_locked = False  # 是否锁定切割线

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_open = QPushButton("1. 选择 PDF 文件")
        self.btn_open.setFixedHeight(50)
        self.btn_open.clicked.connect(self.open_pdf)
        
        self.btn_save = QPushButton("2. 导出为 A4 纵向 PDF")
        self.btn_save.setFixedHeight(50)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_pdf)
        
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        # 状态信息显示区 (增强可见度)
        self.info_label = QLabel("操作指引：请先加载 PDF 试卷")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFixedHeight(40)
        # 黑色背景，白色粗体，非常醒目
        self.info_label.setStyleSheet("""
            background-color: #333; 
            color: #FFFFFF; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 5px;
        """)
        layout.addWidget(self.info_label)

        # 预览区域
        self.preview_label = QLabel("等待加载预览...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px solid #555; background: #222; margin: 5px;")
        
        self.preview_label.setMouseTracking(True)
        self.preview_label.mousePressEvent = self.on_mouse_press
        self.preview_label.mouseMoveEvent = self.on_mouse_move
        layout.addWidget(self.preview_label, stretch=1)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 PDF", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                self.doc = fitz.open(file_path)
                page = self.doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                pix.save(self.temp_png)
                
                self.original_pixmap = QPixmap(self.temp_png)
                
                # 锁定显示尺寸，防止抖动
                available_size = self.preview_label.size() - QSize(40, 40)
                temp_scaled = self.original_pixmap.scaled(
                    available_size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.fixed_display_size = temp_scaled.size()
                
                self.is_locked = False
                self.btn_save.setEnabled(True)
                self.update_display()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开 PDF: {e}")

    def on_mouse_press(self, event):
        """点击切换锁定状态"""
        if self.original_pixmap is None: return
        
        # 切换锁定开关
        self.is_locked = not self.is_locked
        
        if not self.is_locked:
            # 如果是解锁，则立即跟随当前点击位置
            self.on_mouse_move(event)
        else:
            self.update_display()

    def on_mouse_move(self, event):
        """只有在未锁定时才跟随鼠标移动"""
        if self.original_pixmap is None or self.fixed_display_size is None or self.is_locked:
            return
        
        lbl_w = self.preview_label.width()
        pix_w = self.fixed_display_size.width()
        offset_x = (lbl_w - pix_w) / 2
        
        rel_x = event.position().x() - offset_x
        if 0 <= rel_x <= pix_w:
            self.split_ratio = rel_x / pix_w
            self.update_display()

    def update_display(self):
        if self.original_pixmap is None or self.fixed_display_size is None:
            return

        canvas = self.original_pixmap.scaled(
            self.fixed_display_size, 
            Qt.AspectRatioMode.IgnoreAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        painter = QPainter(canvas)
        
        # 锁定状态下线变绿色，未锁定为红色
        line_color = QColor(0, 255, 0, 220) if self.is_locked else QColor(255, 0, 0, 220)
        painter.setPen(QPen(line_color, 4))
        
        x = int(canvas.width() * self.split_ratio)
        painter.drawLine(x, 0, x, canvas.height())
        
        # 在线上方写状态
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_text = "已固定(点击解锁)" if self.is_locked else "调整中(点击锁定)"
        painter.drawText(x + 5, 30, status_text)
        painter.end()

        self.preview_label.setPixmap(canvas)
        
        # 更新顶部文字信息
        lock_status = "【已锁定】" if self.is_locked else "【调整中】"
        self.info_label.setText(f"{lock_status} 当前切割比例: {self.split_ratio*100:.1f}% | 再次点击图片可重新选择")

    def save_pdf(self):
        if not self.doc: return
        if not self.is_locked:
            QMessageBox.warning(self, "提示", "请先在图片上点击以确定切割位置（线变绿表示确定）")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "保存 PDF", "切分试卷.pdf", "PDF Files (*.pdf)")
        if not out_path: return

        try:
            a4_w, a4_h = fitz.paper_size("a4")
            new_doc = fitz.open()
            for page in self.doc:
                r = page.rect
                mid_x = r.width * self.split_ratio
                clips = [fitz.Rect(0, 0, mid_x, r.height), fitz.Rect(mid_x, 0, r.width, r.height)]
                for clip in clips:
                    new_page = new_doc.new_page(width=a4_w, height=a4_h)
                    new_page.show_pdf_page(new_page.rect, self.doc, page.number, clip=clip)
            
            new_doc.save(out_path)
            new_doc.close()
            QMessageBox.information(self, "成功", "PDF 切分并保存成功！")
        except Exception as e:
            QMessageBox.critical(self, "失败", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFCutter()
    window.show()
    sys.exit(app.exec())