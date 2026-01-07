import fitz  # PyMuPDF
import argparse
import os

def split_pdf(input_path, output_path):
    # 定义标准 A4 尺寸 (单位是点/points, 1 inch = 72 points)
    # A4: 595 x 842
    a4_w, a4_h = fitz.paper_size("a4")

    doc = fitz.open(input_path)
    new_doc = fitz.open()

    for page in doc:
        # 获取原始页面矩形
        rect = page.rect
        width = rect.width
        height = rect.height
        
        # 定义左半部分和右半部分的裁剪框
        # 假设是横向页面，从中线垂直切开
        mid_x = width / 2
        
        # 左右两个区域的定义 [x0, y0, x1, y1]
        regions = [
            fitz.Rect(0, 0, mid_x, height),     # 左半页
            fitz.Rect(mid_x, 0, width, height)  # 右半页
        ]

        for r in regions:
            # 在新文档中创建一页 (A4 纵向)
            new_page = new_doc.new_page(width=a4_w, height=a4_h)
            
            # 计算缩放比例，使裁剪的内容适应 A4 页面
            # 保持长宽比缩放
            zoom_w = a4_w / r.width
            zoom_h = a4_h / r.height
            zoom = min(zoom_w, zoom_h)
            
            # 居中放置的偏移量
            show_rect = fitz.Rect(0, 0, r.width * zoom, r.height * zoom)
            
            # 将原页面的指定区域绘制到新页面的指定位置
            new_page.show_pdf_page(new_page.rect, doc, page.number, clip=r)

    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    print(f"处理完成！已保存至: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将横向PDF试卷对半切分并转为A4纵向")
    parser.add_argument("-i", "--input", required=True, help="输入PDF文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出PDF文件路径")
    
    args = parser.parse_args()
    
    if os.path.exists(args.input):
        split_pdf(args.input, args.output)
    else:
        print(f"错误: 找不到文件 {args.input}")