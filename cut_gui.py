import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os

class PDFCutterTK:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 试卷精准切分工具 (Tkinter 稳定版)")
        self.root.geometry("1100x850")

        self.doc = None
        self.original_image = None
        self.display_image = None
        self.tk_image = None
        self.split_ratio = 0.5
        self.is_locked = False

        self.init_ui()

    def init_ui(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_open = tk.Button(btn_frame, text="1. 选择 PDF 文件", command=self.open_pdf, 
                                 width=20, height=2, bg="#4CAF50", fg="black", font=("Arial", 10, "bold"))
        self.btn_open.pack(side=tk.LEFT, padx=10)

        self.btn_save = tk.Button(btn_frame, text="2. 导出为 A4 PDF", command=self.save_pdf, 
                                 width=20, height=2, state=tk.DISABLED, bg="#2196F3", fg="black", font=("Arial", 10, "bold"))
        self.btn_save.pack(side=tk.LEFT, padx=10)

        self.info_label = tk.Label(self.root, text="请先加载 PDF 试卷", font=("Arial", 12, "bold"), 
                                  bg="#333", fg="white", height=2)
        self.info_label.pack(fill=tk.X, padx=20)

        self.canvas = tk.Canvas(self.root, bg="#222", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        # 使用 lambda 延迟处理 resize，防止初始化时报错
        self.root.bind("<Configure>", lambda e: self.refresh_view() if self.original_image else None)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            try:
                self.doc = fitz.open(file_path)
                page = self.doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                self.original_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                self.is_locked = False
                self.btn_save.config(state=tk.NORMAL)
                self.root.after(100, self.refresh_view) # 延迟刷新确保画布尺寸已计算
            except Exception as e:
                messagebox.showerror("错误", f"无法打开 PDF: {e}")

    def on_mouse_click(self, event):
        if self.original_image:
            self.is_locked = not self.is_locked
            self.refresh_view()

    def on_mouse_move(self, event):
        if self.original_image and self.display_image and not self.is_locked:
            canvas_w = self.canvas.winfo_width()
            img_w = self.display_image.width # 修正此处
            offset_x = (canvas_w - img_w) / 2
            
            rel_x = event.x - offset_x
            if 0 <= rel_x <= img_w:
                self.split_ratio = rel_x / img_w
                self.refresh_view()

    def refresh_view(self):
        if not self.original_image:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 50 or canvas_h < 50: return

        img_w, img_h = self.original_image.size
        # 留出边距
        ratio = min((canvas_w-40)/img_w, (canvas_h-40)/img_h)
        new_size = (max(1, int(img_w * ratio)), max(1, int(img_h * ratio)))
        
        self.display_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.delete("all")
        x_pos = canvas_w / 2
        y_pos = canvas_h / 2
        self.canvas.create_image(x_pos, y_pos, image=self.tk_image)

        line_color = "#00FF00" if self.is_locked else "#FF0000"
        img_x_start = x_pos - new_size[0]/2
        line_x = img_x_start + new_size[0] * self.split_ratio
        
        self.canvas.create_line(line_x, y_pos - new_size[1]/2, line_x, y_pos + new_size[1]/2, 
                                fill=line_color, width=3)

        status = "【已锁定】" if self.is_locked else "【调整中】"
        self.info_label.config(text=f"{status} 比例: {self.split_ratio*100:.1f}% | 点击图片锁定/解锁")

    def save_pdf(self):
        if not self.doc: return
        if not self.is_locked:
            messagebox.showwarning("提示", "拖动红色分割线请先点击预览图锁定切割位置（线变绿）")
            return

        out_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
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
            messagebox.showinfo("成功", "PDF 已切分保存成功！")
        except Exception as e:
            messagebox.showerror("失败", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCutterTK(root)
    root.mainloop()