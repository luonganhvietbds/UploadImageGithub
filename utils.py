import unicodedata
import re
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import numpy as np

# ======================================
# 👑 1) Remove accents – SEO filename format
# ======================================
def remove_accents(text: str) -> str:
    """
    Chuyển tiếng Việt có dấu → không dấu + SEO friendly.
    Ví dụ: "Ảnh Bán Hàng" → "anh-ban-hang"
    """
    text = unicodedata.normalize('NFKD', text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\-]+", "-", text).lower()
    text = re.sub(r"-+", "-", text).strip("-")
    return text


# ======================================
# 👑 2) Auto-fix EXIF orientation
# ======================================
def fix_orientation(img: Image.Image) -> Image.Image:
    try:
        return ImageOps.exif_transpose(img)
    except:
        return img


# ======================================
# 👑 3) Resize ảnh – giữ nguyên tỷ lệ
# ======================================
def resize_image(img: Image.Image, max_width: int) -> Image.Image:
    """Resize ảnh theo max_width, tự động tính tỷ lệ."""
    img = fix_orientation(img)

    w, h = img.size
    if w <= max_width:
        return img

    ratio = max_width / w
    new_size = (int(w * ratio), int(h * ratio))
    return img.resize(new_size, Image.LANCZOS)


# ======================================
# 👑 4) Compress ảnh – JPG format PRO
# ======================================
def compress_image(img: Image.Image, quality: int = 80) -> bytes:
    """
    Nén ảnh JPG theo quality. Tự convert sang RGB để tránh lỗi.
    """
    buffer = io.BytesIO()
    rgb = img.convert("RGB")
    rgb.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


# ======================================
# 👑 5) Save ảnh thành WebP (để SEO tốt hơn)
# ======================================
def export_webp(img: Image.Image, quality: int = 80) -> bytes:
    """Xuất WebP – nhẹ hơn JPG"""
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality)
    return buffer.getvalue()


# ======================================
# 👑 6) Tạo thumbnail
# ======================================
def create_thumbnail(img: Image.Image, width: int = 300) -> Image.Image:
    """
    Tạo thumbnail chiều rộng = width px.
    """
    img = fix_orientation(img)

    w, h = img.size
    ratio = width / w
    new_size = (width, int(h * ratio))
    return img.copy().resize(new_size, Image.LANCZOS)


# ======================================
# 👑 7) Watermark text PRO
# ======================================
def add_watermark_text(
    img: Image.Image,
    text: str = "© MyBrand",
    opacity: int = 180,
    font_size: int = None,
    position: str = "bottom-right"
) -> Image.Image:
    """
    Thêm watermark với vị trí tùy chọn:
    - top-left
    - top-right
    - bottom-left
    - bottom-right (mặc định)
    """

    img = img.copy()
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # Auto scale font theo kích thước ảnh
    if font_size is None:
        font_size = int(width / 40)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(text, font)

    margin = int(width * 0.02)

    # Vị trí watermark
    positions = {
        "top-left": (margin, margin),
        "top-right": (width - text_w - margin, margin),
        "bottom-left": (margin, height - text_h - margin),
        "bottom-right": (width - text_w - margin, height - text_h - margin),
    }

    pos = positions.get(position, positions["bottom-right"])

    # Vẽ text mờ
    draw.text(pos, text, font=font, fill=(255, 255, 255, opacity))

    return img


# ======================================
# 👑 8) Watermark Logo PRO
# ======================================
def add_watermark_logo(
    img: Image.Image,
    logo_img: Image.Image,
    scale: float = 0.18,
    position="bottom-right"
) -> Image.Image:
    """
    Thêm watermark logo PNG (có alpha).
    - scale = chiều rộng logo so với ảnh chính
    """

    img = img.copy()
    img = fix_orientation(img)

    w, h = img.size

    # Resize logo
    logo_w = int(w * scale)
    ratio = logo_w / logo_img.width
    logo = logo_img.resize((logo_w, int(logo_img.height * ratio)), Image.LANCZOS)

    logo = logo.convert("RGBA")

    lw, lh = logo.size
    margin = int(w * 0.02)

    # Vị trí
    positions = {
        "top-left": (margin, margin),
        "top-right": (w - lw - margin, margin),
        "bottom-left": (margin, h - lh - margin),
        "bottom-right": (w - lw - margin, h - lh - margin),
    }

    pos = positions.get(position, positions["bottom-right"])

    # Paste logo với alpha
    img.paste(logo, pos, logo)

    return img


# ======================================
# 👑 9) Check nếu ảnh bị hỏng
# ======================================
def is_image_valid(file) -> bool:
    try:
        Image.open(file)
        return True
    except:
        return False


# ======================================
# 👑 10) Export công cụ log
# ======================================
def debug_log(msg):
    """Log hiển thị trong streamlit console hoặc debug"""
    print(f"[DEBUG] {msg}")
