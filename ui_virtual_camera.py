import tkinter as tk
from tkinter import messagebox
import cv2
import subprocess
from PIL import Image, ImageTk
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FFMPEG_PATH = BASE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe"

class RTSPPublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trạm Phát Sóng RTSP (Camera Ảo)")
        self.root.geometry("600x550")
        
        # --- Biến trạng thái ---
        self.is_streaming = False
        self.cap = None
        self.pipe = None
        
        # --- Thiết kế Giao diện (UI) ---
        frame_controls = tk.Frame(root, pady=10)
        frame_controls.pack(fill=tk.X)
        
        tk.Label(frame_controls, text="Cổng Camera (0,1,2...):").grid(row=0, column=0, padx=5, pady=5)
        self.cam_index = tk.Entry(frame_controls, width=5)
        self.cam_index.insert(0, "0") # Mặc định để số 0 (cho OBS Virtual Camera) hoặc 0 cho Webcam
        self.cam_index.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_controls, text="Link RTSP:").grid(row=0, column=2, padx=5, pady=5)
        self.rtsp_url = tk.Entry(frame_controls, width=30)
        self.rtsp_url.insert(0, "rtsp://localhost:8554/live")
        self.rtsp_url.grid(row=0, column=3, padx=5, pady=5)
        
        # Nút bấm
        self.btn_start = tk.Button(frame_controls, text="▶ BẮT ĐẦU", bg="#22c55e", fg="white", font=("Arial", 10, "bold"), command=self.start_stream)
        self.btn_start.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.btn_stop = tk.Button(frame_controls, text="⏹ DỪNG", bg="#ef4444", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED, command=self.stop_stream)
        self.btn_stop.grid(row=1, column=2, columnspan=2, pady=10)
        
        self.lbl_status = tk.Label(root, text="Trạng thái: Đang chờ...", fg="gray", font=("Arial", 10, "italic"))
        self.lbl_status.pack()
        
        # Khung hiển thị video Preview
        self.video_label = tk.Label(root, bg="black", width=500, height=375)
        self.video_label.pack(pady=10)
        
    def start_stream(self):
        cam_idx = int(self.cam_index.get())
        url = self.rtsp_url.get()
        
        self.cap = cv2.VideoCapture(cam_idx)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", f"Không thể kết nối Camera ở cổng {cam_idx}!\nHãy chắc chắn bạn đã bật Camera ảo.")
            return
            
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        if fps == 0: fps = 30
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Lệnh ép FFmpeg đẩy video
        command = [
            str(FFMPEG_PATH), '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24', '-s', f"{width}x{height}", '-r', str(fps),
            '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast', '-f', 'rtsp', url
        ]
        
        try:
            self.pipe = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.is_streaming = True
            
            # Cập nhật UI
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.cam_index.config(state=tk.DISABLED)
            self.rtsp_url.config(state=tk.DISABLED)
            self.lbl_status.config(text=f"ĐANG PHÁT SÓNG LÊN: {url}", fg="red", font=("Arial", 10, "bold"))
            
            self.update_frame() # Khởi động vòng lặp video
        except Exception as e:
            messagebox.showerror("Lỗi FFmpeg", f"Không thể gọi FFmpeg. Đảm bảo bạn đã cài FFmpeg.\nChi tiết: {str(e)}")
            self.stop_stream()
            
    def update_frame(self):
        """Hàm đọc ảnh và cập nhật lên UI liên tục"""
        if not self.is_streaming:
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Chèn chữ mô phỏng bệnh nhân vào hình
            cv2.putText(frame, "Streaming...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Đẩy ảnh vào đường ống mạng (Gửi cho MediaMTX)
            try:
                self.pipe.stdin.write(frame.tobytes())
            except:
                pass
            
            # Xử lý màu sắc để hiển thị lên UI của Python (BGR -> RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb).resize((500, 375)) 
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk # Lưu vào bộ nhớ để không bị xóa mất
            self.video_label.configure(image=imgtk)
            
        # Tự động gọi lại hàm này sau 15 mili-giây (tạo cảm giác video mượt)
        self.root.after(15, self.update_frame)
        
    def stop_stream(self):
        self.is_streaming = False
        if self.cap: self.cap.release()
        if self.pipe: 
            try:
                self.pipe.stdin.close()
                self.pipe.wait()
            except: pass
            
        # Trả UI về trạng thái ban đầu
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.cam_index.config(state=tk.NORMAL)
        self.rtsp_url.config(state=tk.NORMAL)
        self.lbl_status.config(text="Trạng thái: Đã dừng phát.", fg="gray", font=("Arial", 10, "italic"))
        self.video_label.configure(image='')

if __name__ == "__main__":
    root = tk.Tk()
    app = RTSPPublisherApp(root)
    # Bắt sự kiện khi người dùng bấm dấu X đỏ để tắt cửa sổ
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_stream(), root.destroy()))
    root.mainloop()