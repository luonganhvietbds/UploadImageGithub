import unicodedata
import re
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# ======================================
# 1) SEO-FRIENDLY FILENAME
# ======================================
def remove_accents(text: str) -> str:
    """
    Chuyển tiếng Việt có dấu → không dấu + định dạng SEO.
    Ví dụ: 'Ảnh Bán Hàng' → 'anh-ban-hang'
    """
    text = unicodedata.normalize('NFKD', text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\-]+", "-", text).lower()
    text = re.sub(r"-+", "-", text).strip("-")
    return text


# ======================================
# 2) FIX ORIENTATION (EXIF) – ảnh điện thoại hay bị xoay
# ======================================
def fix_orientation(img: Image.Image) -> Image.Image:
    try:
        return ImageOps.exif_transpose(img)
    except:
        return img


# ======================================
# 3) RESIZE PRO
# ======================================
def resize_image(img: Image.Image, max_width: int) -> Image.Image:
    """Resize ảnh giữ nguyên tỉ lệ."""
    img = fix_orientation(img)

    w, h = img.size
    if w <= max_width:
        return img

    ratio = max_width / w
    new_size = (int(max_width), int(h * ratio))
    return img.resize(new_size, Image.LANCZOS)


# ======================================
# 4) COMPRESS JPG PRO
# ======================================
def compress_image(img: Image.Image, quality: int = 85) -> bytes:
    """Nén ảnh JPG thành bytes để upload GitHub."""
    buffer = io.BytesIO()
    rgb = img.convert("RGB")
    rgb.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


# ======================================
# 5) EXPORT WEBP – siêu nhẹ, chuẩn SEO
# ======================================
def export_webp(img: Image.Image, quality: int = 85) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=quality)
    return buffer.getvalue()


# ======================================
# 6) THUMBNAIL PRO
# ======================================
def create_thumbnail(img: Image.Image, width: int = 300) -> Image.Image:
    """Tạo thumbnail chiều rộng = width px."""
    img = fix_orientation(img)
    w, h = img.size
    ratio = width / w
    new_size = (width, int(h * ratio))
    return img.resize(new_size, Image.LANCZOS)


# ======================================
# 7) WATERMARK TEXT PRO
# ======================================
def add_watermark_text(
    img: Image.Image,
    text: str = "© MyBrand",
    opacity: int = 180,
    font_size: int = None,
    position: str = "bottom-right"
) -> Image.Image:
    """
    Thêm watermark chữ vào ảnh:
    - Vị trí: top-left, top-right, bottom-left, bottom-right
    - Tự scale font theo kích thước ảnh
    - Độ mờ tùy chỉnh
    """
    img = fix_orientation(img).copy()
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # Auto scale font size
    if font_size is None:
        font_size = max(20, int(width / 40))

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(text, font)
    margin = int(width * 0.02)

    # Vị trí text
    positions = {
        "top-left": (margin, margin),
        "top-right": (width - text_w - margin, margin),
        "bottom-left": (margin, height - text_h - margin),
        "bottom-right": (width - text_w - margin, height - text_h - margin),
    }

    pos = positions.get(position, positions["bottom-right"])

    draw.text(pos, text, fill=(255, 255, 255, opacity), font=font)

    return img


# ======================================
# 8) WATERMARK LOGO PRO
# ======================================
def add_watermark_logo(
    img: Image.Image,
    logo_img: Image.Image,
    scale: float = 0.18,
    position: str = "bottom-right"
) -> Image.Image:
    """
    Thêm watermark logo PNG (có alpha).
    - Scale theo chiều rộng ảnh
    - Vị trí tùy chọn
    - Hỗ trợ logo không có alpha
    """

    img = fix_orientation(img).copy()
    width, height = img.size

    # Resize logo
    logo_w = int(width * scale)
    ratio = logo_w / logo_img.width
    logo = logo_img.resize((logo_w, int(logo_img.height * ratio)), Image.LANCZOS)
    logo = logo.convert("RGBA")

    lw, lh = logo.size
    margin = int(width * 0.02)

    positions = {
        "top-left": (margin, margin),
        "top-right": (width - lw - margin, margin),
        "bottom-left": (margin, height - lh - margin),
        "bottom-right": (width - lw - margin, height - lh - margin),
    }

    pos = positions.get(position, positions["bottom-right"])

    img.paste(logo, pos, logo)

    return img


# ======================================
# 9) VALIDATE IMAGE
# ======================================
def is_image_valid(file) -> bool:
    """Kiểm tra xem file có phải ảnh hợp lệ không."""
    try:
        Image.open(file)
        return True
    except:
        return False


# ======================================
# 10) DEBUG LOG
# ======================================
def debug_log(msg: str):
    """Log dùng để debug (Streamlit Cloud console)."""
    print(f"[DEBUG] {msg}")
