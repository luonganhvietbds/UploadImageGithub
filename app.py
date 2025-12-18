import streamlit as st
import requests
import base64
import os
from datetime import datetime
from PIL import Image
import io

# Import các hàm xử lý ảnh PRO
from utils import (
    remove_accents,
    resize_image,
    compress_image,
    create_thumbnail,
    add_watermark_text,
    add_watermark_logo
)

# ==============================
# Thiết lập trang Streamlit
# ==============================
st.set_page_config(
    page_title="GitHub Image Uploader PRO",
    page_icon="🖼",
    layout="wide"
)

st.title("🚀 GitHub Image Uploader – PRO Edition")
st.markdown("""
Công cụ PRO cho phép bạn **Upload – Tối ưu – Nén – Rename SEO – Watermark – Tạo thư mục – Generate RAW/CDN link**  
Tất cả trong một giao diện trực quan, chạy trực tiếp trên Streamlit Cloud.
""")

# ==============================
# SIDEBAR: Cấu hình GitHub
# ==============================
st.sidebar.header("🔧 Cấu hình GitHub")

token = st.sidebar.text_input("GitHub Token (PAT)", type="password")
repo = st.sidebar.text_input("Repository (username/repo)", value="")
branch = st.sidebar.text_input("Branch", value="main")

folder_mode = st.sidebar.selectbox(
    "Thư mục GitHub:",
    ["images/", "images/{year}/{month}/", "images/{custom}/"]
)

custom_folder = ""
if "{custom}" in folder_mode:
    custom_folder = st.sidebar.text_input("Tên thư mục tùy chọn")

st.sidebar.divider()

# ==============================
# Sidebar xử lý ảnh PRO
# ==============================
st.sidebar.header("🖼 Tùy chọn xử lý ảnh (PRO)")

resize_width = st.sidebar.slider("Resize chiều rộng tối đa (px)", 400, 2000, 1200)
quality = st.sidebar.slider("Chất lượng nén (%)", 30, 100, 85)

create_thumb = st.sidebar.checkbox("Tạo thumbnail 300px")
use_watermark = st.sidebar.checkbox("Thêm watermark text")
watermark_text = ""

if use_watermark:
    watermark_text = st.sidebar.text_input("Nội dung watermark", "© MyBrand")

st.sidebar.divider()

# ==============================
# Upload Section
# ==============================
uploaded_files = st.file_uploader(
    "📁 Chọn nhiều ảnh để upload:",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("👀 Preview ảnh đã chọn")
    cols = st.columns(4)
    idx = 0
    for file in uploaded_files:
        img = Image.open(file)
        with cols[idx % 4]:
            st.image(img, caption=file.name, use_column_width=True)
        idx += 1

# ==============================
# Hàm upload ảnh lên GitHub
# ==============================
def github_upload(file_bytes, filename):

    folder = folder_mode.replace("{year}", str(datetime.now().year))
    folder = folder.replace("{month}", str(datetime.now().month))
    folder = folder.replace("{custom}", remove_accents(custom_folder))

    github_path = folder + filename

    encoded = base64.b64encode(file_bytes).decode()

    url = f"https://api.github.com/repos/{repo}/contents/{github_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"Upload {filename}",
        "content": encoded,
        "branch": branch
    }

    res = requests.put(url, json=data, headers=headers)

    if res.status_code in [200, 201]:
        raw_url = res.json()["content"]["download_url"]\
            .replace("https://github.com", "https://raw.githubusercontent.com")\
            .replace("/blob/", "/")

        cdn_url = f"https://cdn.jsdelivr.net/gh/{repo}/{github_path}"

        return raw_url, cdn_url

    return None, None


# ==============================
# BUTTON – Bắt đầu upload
# ==============================
if st.button("🚀 Upload tất cả ảnh"):
    if not token or not repo:
        st.error("⚠ Vui lòng nhập GitHub Token và Repo!")
        st.stop()

    if not uploaded_files:
        st.error("⚠ Chưa chọn ảnh!")
        st.stop()

    st.info("⏳ Đang xử lý và upload...")

    results = []

    for file in uploaded_files:
        img = Image.open(file)

        # SEO rename
        new_name = remove_accents(os.path.splitext(file.name)[0]) + ".jpg"

        # Resize
        img = resize_image(img, resize_width)

        # Watermark
        if use_watermark:
            img = add_watermark_text(img, watermark_text)

        # Compress
        img_bytes = compress_image(img, quality)

        # Upload ảnh chính
        raw_url, cdn_url = github_upload(img_bytes, new_name)

        results.append({
            "name": new_name,
            "raw": raw_url,
            "cdn": cdn_url
        })

        # Thumbnail nếu bật
        if create_thumb:
            thumb = create_thumbnail(img)
            buf = io.BytesIO()
            thumb.save(buf, format="JPEG", quality=quality)
            github_upload(buf.getvalue(), f"thumb_{new_name}")

    st.success("🎉 Upload thành công!")

    st.subheader("🔗 Link ảnh đã upload")

    for r in results:
        st.markdown(f"""
        **📌 {r['name']}**  
        RAW: `{r['raw']}`  
        CDN: `{r['cdn']}`
        """)

    st.balloons()
