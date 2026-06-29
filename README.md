# Trạm Phát Sóng Camera Ảo (RTSP Virtual Camera)

Hệ thống giả lập luồng video RTSP từ OBS Virtual Camera hoặc Webcam vật lý, phục vụ việc đẩy luồng video lên mạng nội bộ để test các mô hình AI/Computer Vision.

## Yêu Cầu Hệ Thống (Prerequisites)
1. **Python 3.11+**
2. **MediaMTX:** RTSP Server để nhận luồng. (https://github.com/bluenviron/mediamtx/tags)
3. **FFmpeg:** Tải về , giải nén bỏ vào root của dự án. Đổi tên thành ffmpeg (https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-8.0.1-essentials_build.zip)

**Đảm bảo cây dự án:**
ui_virtual_camera/
│
├── ffmpeg/
│   └── bin/
│       └── ffmpeg.exe
│
└── ui_virtual_camera.py

## Hướng Dẫn Setup Cài Đặt
Khi vừa clone dự án này về máy, hãy chạy lần lượt các lệnh sau trên Terminal:

**1. Tạo môi trường ảo (Virtual Environment):**
```cmd
python -m venv venv
```
**2. Kích hoạt môi trường ảo:**

Trên Windows (CMD): 
```cmd
venv\Scripts\activate
```

Trên Linux/Mac: 
```cmd
source venv/bin/activate
```
**3. Cài đặt các thư viện lõi:**
```cmd
pip install -r requirements.txt
```

**Hướng Dẫn Chạy (Workflow)**
B1: Bật file mediamtx.exe và để nó chạy ngầm.

B2: Vào lại cmd dự án chạy:
```cmd
python ui_virtual_camera.py
```

B3: Chọn luồng camera bằng cách nhập số (mặc định số 0)

B4: Bấm bắt đầu và xem màng hình preview đã hiện hình ảnh là thành công