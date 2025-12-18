import streamlit as st
import requests
import base64
import os
from datetime import datetime
from PIL import Image
import io

# Import xử lý ảnh từ utils_smart_pro.py (sẽ gửi sau)
from utils_smart_pro import (
    remove_accents,
    resize_image,
    compress_image,
    create_thumbnail,
    add_watermark_text,
    add_watermark_logo,
    is_image_valid
)

# ======================================
# SMART RESET FUNCTION
# ======================================
def smart_reset():
    reserved_keys = [
        "token", "repo", "branch",
        "folder_mode", "custom_folder"
    ]
    for key in list(st.session_state.keys()):
        if key not in reserved_keys:
            del st.session_state[key]
    st.rerun()


# ======================================
# STREAMLIT PAGE CONFIG
# ======================================
st.set_page_config(
    page_title="GitHub Image Uploader – SMART PRO+",
    page_icon="🖼",
    layout="wide"
)

st.title("🚀 GitHub Image Uploader – SMART PRO+ Edition")
st.markdown("""
Phiên bản **SMART PRO+** với tính năng nâng cao:
- Kiểm tra lỗi đầu vào
- Check Token / Repo / Branch
- Reset thông minh (giữ token & repo)
- Log chi tiết theo từng file
- Export RAW/CDN link
- Xử lý ảnh PRO (resize, compress, watermark, thumbnail)
""")

# ======================================
# SIDEBAR: Cấu hình GitHub
# ======================================
st.sidebar.header("🔧 Cấu hình GitHub")

# Giữ token/repo trong session
token = st.sidebar.text_input("GitHub Token (PAT)", type="password",
    value=st.session_state.get("token", "")
)
st.session_state["token"] = token

repo = st.sidebar.text_input("Repository (username/repo)",
    value=st.session_state.get("repo", "")
)
st.session_state["repo"] = repo

branch = st.sidebar.text_input("Branch", value=st.session_state.get("branch", "main"))
st.session_state["branch"] = branch

folder_mode = st.sidebar.selectbox(
    "Thư mục GitHub:",
    ["images/", "images/{year}/{month}/", "images/{custom}/"],
    index=0,
    key="folder_mode"
)

if "{custom}" in folder_mode:
    custom_folder = st.sidebar.text_input("Tên thư mục tùy chọn", key="custom_folder")
else:
    st.session_state["custom_folder"] = ""

# RESET THÔNG MINH
if st.sidebar.button("🔄 Reset phiên làm việc (giữ token)"):
    smart_reset()


# ======================================
# VALIDATION
# ======================================
def validate_inputs():
    if not token:
        return "❌ Chưa nhập GitHub Token."

    if "/" not in repo:
        return "❌ Repo phải theo dạng: username/repo_name."

    repo_url = f"https://api.github.com/repos/{repo}"
    r = requests.get(repo_url, headers={"Authorization": f"Bearer {token}"})

    if r.status_code == 404:
        return "❌ Repo không tồn tại hoặc bạn không có quyền truy cập."
    if r.status_code == 401:
        return "❌ Token không hợp lệ hoặc không có quyền."

    branch_url = f"https://api.github.com/repos/{repo}/branches/{branch}"
    r2 = requests.get(branch_url, headers={"Authorization": f"Bearer {token}"})

    if r2.status_code == 404:
        return f"❌ Branch '{branch}' không tồn tại."

    return None


# ======================================
# UPLOAD FILE SECTION
# ======================================
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


# ======================================
# FUNC UPLOAD TO GITHUB
# ======================================
def github_upload(file_bytes, filename):
    folder = folder_mode.replace("{year}", str(datetime.now().year))
    folder = folder.replace("{month}", str(datetime.now().month))
    folder = folder.replace("{custom}", remove_accents(st.session_state.get("custom_folder", "")))

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

        return raw_url, cdn_url, None

    return None, None, res.json()


# ======================================
# BUTTON UPLOAD
# ======================================
if st.button("🚀 Upload tất cả ảnh"):
    error = validate_inputs()
    if error:
        st.error(error)
        st.stop()

    if not uploaded_files:
        st.error("❌ Bạn chưa chọn ảnh.")
        st.stop()

    st.info("⏳ Đang upload...")

    st.session_state["results"] = []

    for file in uploaded_files:
        if not is_image_valid(file):
            st.session_state["results"].append({
                "name": file.name,
                "error": "Ảnh lỗi hoặc không đọc được."
            })
            continue

        img = Image.open(file)

        new_name = remove_accents(os.path.splitext(file.name)[0]) + ".jpg"
        img = resize_image(img, 1200)
        img_bytes = compress_image(img, 85)

        raw_url, cdn_url, api_error = github_upload(img_bytes, new_name)

        st.session_state["results"].append({
            "name": new_name,
            "raw": raw_url,
            "cdn": cdn_url,
            "error": api_error
        })

    st.success("🎉 Upload hoàn tất!")
    st.balloons()


# ======================================
# KẾT QUẢ
# ======================================
if "results" in st.session_state and st.session_state["results"]:
    st.subheader("🔗 Kết quả upload:")

    for r in st.session_state["results"]:
        st.markdown(f"### 📌 {r['name']}")

        if r["error"]:
            st.error(f"❌ Lỗi upload: `{r['error']}`")
        else:
            st.success("✔ Upload thành công!")
            st.write(f"RAW URL: `{r['raw']}`")
            st.write(f"CDN URL: `{r['cdn']}`")
