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
    page_title="GitHub Image Uploader PRO+",
    page_icon="🖼",
    layout="wide"
)

st.title("🚀 GitHub Image Uploader – PRO+ Edition")
st.markdown("""
Công cụ PRO+ với tính năng nâng cao: **Kiểm tra lỗi đầu vào – Check Token – Check Repo – Reset Session – Log chi tiết – Upload an toàn**  
Tối ưu hơn, ổn định hơn, chính xác hơn.
""")

# ==============================
# RESET SESSION
# ==============================
if "results" not in st.session_state:
    st.session_state["results"] = []

if st.sidebar.button("🔄 Reset phiên làm việc"):
    st.session_state.clear()
    st.experimental_rerun()


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


# ==============================
# VALIDATION FUNCTION
# ==============================
def validate_inputs():
    if not token:
        return "❌ Chưa nhập GitHub Token."

    if "/" not in repo:
        return "❌ Repo phải theo dạng: username/repo_name."

    # Kiểm tra tồn tại repo
    repo_url = f"https://api.github.com/repos/{repo}"
    r = requests.get(repo_url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 404:
        return "❌ Repo không tồn tại hoặc bạn không có quyền truy cập."
    if r.status_code == 401:
        return "❌ Token không hợp lệ hoặc không có quyền."

    # Kiểm tra tồn tại branch
    branch_url = f"https://api.github.com/repos/{repo}/branches/{branch}"
    r2 = requests.get(branch_url, headers={"Authorization": f"Bearer {token}"})
    if r2.status_code == 404:
        return f"❌ Branch '{branch}' không tồn tại trong repo."

    return None


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
            st.image(img, caption=file.name)
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

        return raw_url, cdn_url, None  # Không lỗi

    else:
        return None, None, res.json()  # Trả lỗi chi tiết từ GitHub


# ==============================
# BUTTON – Bắt đầu upload
# ==============================
if st.button("🚀 Upload tất cả ảnh"):

    validation_error = validate_inputs()
    if validation_error:
        st.error(validation_error)
        st.stop()

    if not uploaded_files:
        st.error("❌ Bạn chưa chọn ảnh.")
        st.stop()

    st.info("⏳ Đang xử lý và upload...")

    results = []

    for file in uploaded_files:
        img = Image.open(file)

        new_name = remove_accents(os.path.splitext(file.name)[0]) + ".jpg"

        img = resize_image(img, resize_width)

        if use_watermark:
            img = add_watermark_text(img, watermark_text)

        img_bytes = compress_image(img, quality)

        raw_url, cdn_url, api_error = github_upload(img_bytes, new_name)

        results.append({
            "name": new_name,
            "raw": raw_url,
            "cdn": cdn_url,
            "error": api_error
        })

        if create_thumb:
            thumb = create_thumbnail(img)
            buf = io.BytesIO()
            thumb.save(buf, format="JPEG", quality=quality)
            github_upload(buf.getvalue(), f"thumb_{new_name}")

    st.session_state["results"] = results
    st.success("🎉 Upload hoàn tất! Kiểm tra kết quả dưới đây 👇")
    st.balloons()


# ==============================
# KẾT QUẢ HIỂN THỊ
# ==============================
if st.session_state["results"]:
    st.subheader("🔗 Kết quả upload:")

    for r in st.session_state["results"]:
        st.markdown(f"### 📌 {r['name']}")

        if r["error"]:
            st.error(f"❌ Upload thất bại: {r['error']}")
        else:
            st.success("✔ Upload thành công!")
            st.write(f"RAW URL: `{r['raw']}`")
            st.write(f"CDN URL: `{r['cdn']}`")

