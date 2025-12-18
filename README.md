# 🚀 GitHub Image Uploader – SMART PRO+ Edition

**GitHub Image Uploader – SMART PRO+** là công cụ upload ảnh thông minh, chạy trực tiếp bằng Streamlit Cloud hoặc HuggingFace Spaces.  
Ứng dụng cho phép bạn upload nhiều ảnh lên GitHub với tính năng nâng cấp mạnh mẽ:

---

## 🌟 Tính năng chính (SMART PRO+)

### 🧠 1. Smart Reset (Giữ Token & Repo)
- Xóa toàn bộ dữ liệu session nhưng **giữ lại**:
  - GitHub Token (PAT)
  - Repository name (username/repo)
  - Branch
  - Thư mục GitHub
- Tạo phiên làm việc mới mà không cần nhập lại cấu hình.

### 🔐 2. Kiểm tra lỗi đầu vào
- Kiểm tra token hợp lệ (401)
- Kiểm tra repo tồn tại (404)
- Kiểm tra branch tồn tại
- Kiểm tra quyền ghi (WRITE) vào repo
- Kiểm tra định dạng repo `username/repo`

### 🖼 3. Xử lý ảnh PRO
- Auto-fix orientation (ảnh xoay sai từ điện thoại)
- Resize theo chiều rộng
- Nén JPG PRO
- Xuất WebP
- Watermark chữ PRO (tự scale, tự chọn vị trí)
- Watermark logo PRO
- Tạo Thumbnail 300px

### 📤 4. Upload lên GitHub qua API
- Tự tạo thư mục  
- Tạo RAW link  
- Tạo CDN link (jsDelivr)  
- Phản hồi chi tiết từng file

### 📦 5. Log & Debug
- Log API lỗi  
- Log ảnh lỗi  
- Thông báo theo từng file (success/fail)

---

## 📁 Cấu trúc repo

