# -*- coding: utf-8 -*-
"""PDF 核心操作封装"""
import os
from pathlib import Path
from typing import List, Optional


class PdfOps:
    """PDF 基础操作"""

    @staticmethod
    def get_page_count(filepath: str) -> int:
        """获取 PDF 页数"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        return len(reader.pages)

    @staticmethod
    def get_info(filepath: str) -> dict:
        """获取 PDF 元信息"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        info = {
            "页数": len(reader.pages),
            "文件名": Path(filepath).name,
            "文件大小": f"{os.path.getsize(filepath) / 1024:.1f} KB",
        }
        meta = reader.metadata
        if meta:
            if meta.title:
                info["标题"] = meta.title
            if meta.author:
                info["作者"] = meta.author
        return info

    @staticmethod
    def merge(filepaths: List[str], output: str) -> str:
        """合并多个 PDF"""
        from pypdf import PdfWriter
        writer = PdfWriter()
        for fp in filepaths:
            reader = pypdf.PdfReader(fp)
            for page in reader.pages:
                writer.add_page(page)
        writer.write(output)
        writer.close()
        return output

    @staticmethod
    def split(filepath: str, output_dir: str, range_str: str = "") -> List[str]:
        """拆分 PDF
        range_str: 空=每页一个, "1-3"=提取范围, "5"=按页数(每组5页)
        """
        reader = pypdf.PdfReader(filepath)
        total = len(reader.pages)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        results = []
        basename = Path(filepath).stem

        if not range_str:
            # 每页一个
            for i in range(total):
                writer = pypdf.PdfWriter()
                writer.add_page(reader.pages[i])
                out = str(out_dir / f"{basename}_第{i+1}页.pdf")
                writer.write(out)
                writer.close()
                results.append(out)
        elif "-" in range_str:
            # 页码范围: "1-3" 或 "3-5"
            start, end = range_str.split("-")
            start_idx = int(start.strip()) - 1
            end_idx = int(end.strip())
            writer = pypdf.PdfWriter()
            for i in range(start_idx, min(end_idx, total)):
                writer.add_page(reader.pages[i])
            out = str(out_dir / f"{basename}_第{start}-{end}页.pdf")
            writer.write(out)
            writer.close()
            results.append(out)
        else:
            # 按每组页数拆分
            per_group = int(range_str)
            for group_start in range(0, total, per_group):
                writer = pypdf.PdfWriter()
                for i in range(group_start, min(group_start + per_group, total)):
                    writer.add_page(reader.pages[i])
                p_start = group_start + 1
                p_end = min(group_start + per_group, total)
                out = str(out_dir / f"{basename}_第{p_start}-{p_end}页.pdf")
                writer.write(out)
                writer.close()
                results.append(out)
        return results

    @staticmethod
    def extract_text(filepath: str, output: str = "") -> str:
        """提取 PDF 文本"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages, 1):
            t = page.extract_text()
            if t:
                text += f"\n--- 第{i}页 ---\n{t}"
        if output:
            Path(output).write_text(text, encoding="utf-8")
        return text

    @staticmethod
    def extract_images(filepath: str, output_dir: str) -> List[str]:
        """提取 PDF 中的图片"""
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images()
            for img_idx, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                out = str(out_dir / f"第{page_num+1}页_图{img_idx+1}.{ext}")
                Path(out).write_bytes(image_bytes)
                results.append(out)
        doc.close()
        return results

    @staticmethod
    def to_images(filepath: str, output_dir: str, dpi: int = 200) -> List[str]:
        """PDF 每页转图片"""
        import fitz
        doc = fitz.open(filepath)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        results = []
        basename = Path(filepath).stem
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            out = str(out_dir / f"{basename}_第{page_num+1}页.png")
            pix.save(out)
            results.append(out)
        doc.close()
        return results

    @staticmethod
    def to_word(filepath: str, output: str = "") -> str:
        """PDF 转 Word"""
        from pdf2docx import Converter
        output = output or str(Path(filepath).with_suffix(".docx"))
        cv = Converter(filepath)
        cv.convert(output, start=0, end=None)
        cv.close()
        return output

    @staticmethod
    def add_watermark(filepath: str, text: str, output: str = "") -> str:
        """添加文字水印"""
        import pypdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        # 创建水印 PDF
        watermark_path = str(Path(filepath).parent / "_watermark_temp.pdf")
        c = canvas.Canvas(watermark_path)
        page = pypdf.PdfReader(filepath).pages[0]
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        c.setPageSize((w, h))
        c.setFont("Helvetica", 40)
        c.setFillColorRGB(0.5, 0.5, 0.5, 0.3)
        c.saveState()
        c.translate(w / 2, h / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()

        # 给每一页加水印
        reader = pypdf.PdfReader(filepath)
        watermark = pypdf.PdfReader(watermark_path)
        wm_page = watermark.pages[0]
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            page.merge_page(wm_page)
            writer.add_page(page)
        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_带水印"))
        writer.write(output)
        writer.close()

        # 清理临时文件
        Path(watermark_path).unlink(missing_ok=True)
        return output

    @staticmethod
    def add_page_numbers(filepath: str, output: str = "") -> str:
        """添加页码"""
        import pypdf
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        reader = pypdf.PdfReader(filepath)
        total = len(reader.pages)
        watermark_paths = []

        for i in range(total):
            page = reader.pages[i]
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            wm_path = str(Path(filepath).parent / f"_pagenum_{i}.pdf")
            c = canvas.Canvas(wm_path)
            c.setPageSize((w, h))
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.4, 0.4, 0.4)
            c.drawCentredString(w / 2, 20, f"— {i+1} / {total} —")
            c.save()
            watermark_paths.append(wm_path)

        writer = pypdf.PdfWriter()
        for i, page in enumerate(reader.pages):
            wm = pypdf.PdfReader(watermark_paths[i])
            page.merge_page(wm.pages[0])
            writer.add_page(page)

        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_带页码"))
        writer.write(output)
        writer.close()

        for p in watermark_paths:
            Path(p).unlink(missing_ok=True)
        return output

    @staticmethod
    def encrypt(filepath: str, password: str, output: str = "") -> str:
        """加密 PDF"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(password)
        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_加密"))
        writer.write(output)
        writer.close()
        return output

    @staticmethod
    def decrypt(filepath: str, password: str, output: str = "") -> str:
        """解密 PDF"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_解密"))
        writer.write(output)
        writer.close()
        return output

    @staticmethod
    def rotate(filepath: str, degrees: int = 90, output: str = "") -> str:
        """旋转 PDF 页面"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            page.rotate(degrees)
            writer.add_page(page)
        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_旋转"))
        writer.write(output)
        writer.close()
        return output

    @staticmethod
    def compress(filepath: str, output: str = "") -> str:
        """压缩 PDF（去除冗余数据）"""
        import pypdf
        reader = pypdf.PdfReader(filepath)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata(reader.metadata)
        # 压缩
        for page in writer.pages:
            page.compress_content_streams()
        output = output or str(Path(filepath).with_stem(Path(filepath).stem + "_压缩"))
        writer.write(output)
        writer.close()
        return output
