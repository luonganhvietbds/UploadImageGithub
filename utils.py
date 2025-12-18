import unicodedata
import re
from PIL import Image, ImageDraw, ImageFont
import io

# ======================================
# 1) Remove accents – SEO filename format
# ======================================
def remove_accents(text: str) -> str:
    """
    Chuyển tiếng Việt có dấu → không dấu, SEO-friendly
    Ví dụ: "Ảnh Bán Hàng" → "anh-ban-hang"
    """
    text = unicodedata.normalize('NFKD', text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\-]+", "-", text).lower()
    text = re.sub(r"-+", "-", text).strip("-")
    return text


# ======================================
# 2) Resize ảnh – giữ nguyên tỷ lệ
# ======================================
def resize_image(img: Image.Image, max_width: int) -> Image.Image:
    """Resize ảnh theo max_width, tự động tính chiều cao."""
    w, h = img.size
    if w <= max_width:
        return img

    ratio = max_width / w
    new_size = (int(w * ratio), int(h * ratio))
    return img.resize(new_size, Image.LANCZOS)


# ======================================
# 3) Compress ảnh – JPG format
# ======================================
def compress_image(img: Image.Image, quality: int = 80) -> bytes:
    """
    Nén ảnh JPG theo quality. Trả về bytes để upload GitHub.
    """
    buffer = io.BytesIO()
    rgb_img = img.convert("RGB")  # JPG không hỗ trợ RGBA
    rgb_img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


# ======================================
# 4) Tạo thumbnail
# ======================================
def create_thumbnail(img: Image.Image, size: int = 300) -> Image.Image:
    """Tạo thumbnail chiều rộng = size px."""
    w, h = img.size
    ratio = size / w
    new_size = (size, int(h * ratio))
    return img.copy().resize(new_size, Image.LANCZOS)


# ======================================
# 5) Watermark text
# ======================================
def add_watermark_text(
    img: Image.Image,
    text: str = "© MyBrand",
    opacity: int = 150,
    font_size: int = 24
) -> Image.Image:
    """
    Thêm watermark text góc dưới phải.
    """
    watermark = img.copy()
    draw = ImageDraw.Draw(watermark)

    # Load font mặc định
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    width, height = img.size
    text_w, text_h = draw.textsize(text, font)

    position = (width - text_w - 20, height - text_h - 20)

    draw.text(position, text, fill=(255, 255, 255, opacity), font=font)

    return watermark


# ======================================
# 6) Watermark Logo
# ======================================
def add_watermark_logo(
    img: Image.Image,
    logo_img: Image.Image,
    scale: float = 0.2
) -> Image.Image:
    """
    Thêm watermark logo PNG (có alpha) góc dưới phải.
    scale = tỷ lệ chiều rộng logo so với ảnh.
    """
    base = img.copy()
    w, h = base.size

    # Resize logo
    logo_w = int(w * scale)
    ratio = logo_w / logo_img.width
    resized_logo = logo_img.resize(
        (logo_w, int(logo_img.height * ratio)), Image.LANCZOS
    )

    pos = (w - resized_logo.width - 20, h - resized_logo.height - 20)

    if resized_logo.mode == "RGBA":
        base.paste(resized_logo, pos, resized_logo)
    else:
        base.paste(resized_logo, pos)

    return base
