import subprocess
import json
import os
import csv
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pymysql


class VideoFile:
    def __init__(self, path):
        self.__path = path
        self.__width = 0
        self.__height = 0
        self.__codec = ""
        self.__auto_scan()

    def __auto_scan(self):
        """扫描引擎"""
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            ffprobe_cmd = os.path.join(base_path, "ffprobe.exe")
        else:
            ffprobe_cmd = "ffprobe"

        cmd_list = [
            ffprobe_cmd, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height", "-of", "json", self.__path
        ]

        #  防止调用导致黑框
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        raw = subprocess.check_output(cmd_list, encoding='utf-8', errors='ignore', startupinfo=startupinfo)
        data = json.loads(raw)

        if 'streams' in data and len(data['streams']) > 0:
            self.__width = data['streams'][0].get('width', 0)
            self.__height = data['streams'][0].get('height', 0)
            self.__codec = data['streams'][0].get('codec_name', 'unknown')
        else:
            raise ValueError(f"无法解析元数据: {self.get_name()}")

    def get_name(self):
        return os.path.basename(self.__path)

    def get_resolution(self):
        return f"{self.__width}x{self.__height}"

    def get_codec(self):
        return self.__codec

    def check_compliance(self):
        if self.__width == 1920 and self.__codec == "h264":
            return "PASS"
        return "FAIL"


def save_local_files(output_dir, data_list, timestamp):
    """本地双存储：生成 CSV 与 JSON """
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "audit_report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "resolution", "codec", "status", "timestamp"])
        writer.writeheader()
        writer.writerows(data_list)

    json_path = os.path.join(output_dir, "audit_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"job_time": timestamp, "results": data_list}, f, indent=4, ensure_ascii=False)


def upload_to_vps(data_list):
    """异地MySQL"""
    db_connection = None
    try:
        db_connection = pymysql.connect(
            host="your_vps_ip_address", port=3306, user="your_database_user", password="your_secure_password",
            database="video_audit_db", charset="utf8mb4", connect_timeout=5
        )
        with db_connection.cursor() as cursor:
            # 建表 SQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_name VARCHAR(255),
                    resolution VARCHAR(50),
                    codec VARCHAR(50),
                    status VARCHAR(20),
                    audit_time DATETIME
                )
            """)
            sql = "INSERT INTO audit_logs (file_name, resolution, codec, status, audit_time) VALUES (%s, %s, %s, %s, %s)"
            for row in data_list:
                cursor.execute(sql, (row["file_name"], row["resolution"], row["codec"], row["status"], row["timestamp"]))
        db_connection.commit()
        return "📡 云服务器成功收到结果 [OK]\n"
    except Exception as db_err:
        return f"❌ 云服务器数据库握手失败: {str(db_err)}\n"
    finally:
        if db_connection:
            db_connection.close()


def run_audit():
    """前端 GUI 选择文件夹"""
    target_dir = filedialog.askdirectory(title="选择你要审计的视频文件夹")
    if not target_dir:
        return

    # 初始化进度条窗口
    progress_win = tk.Toplevel()
    progress_win.title("审计流程")
    progress_win.geometry("400x120")
    progress_win.resizable(False, False)
    progress_win.attributes("-topmost", True)

    status_label = ttk.Label(progress_win, text="[1/5] 正在查看目标目录...", font=("微软雅黑", 10))
    status_label.pack(pady=15)

    p_bar = ttk.Progressbar(progress_win, length=320, mode='determinate')
    p_bar.pack()

    def update_step(val, text):
        p_bar['value'] = val
        status_label.config(text=text)
        progress_win.update()

    # [1/5] 检查文件...
    update_step(10, "[1/5] 正在扫描目标目录下的资产...")
    audit_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_list = []
    report_text = f"📂 目标地址: {target_dir}\n" + "=" * 40 + "\n"

    all_files = os.listdir(target_dir)
    video_files = [f for f in all_files if f.lower().endswith((".mp4", ".mkv", ".mov"))]

    if not video_files:
        progress_win.destroy()
        messagebox.showinfo("审计提示", "❌ 未发现有效的视频资产。")
        return

    total_count = len(video_files)

    # 循环视频
    for idx, file_name in enumerate(video_files, 1):
        full_path = os.path.join(target_dir, file_name).replace("\\", "/")
        current_progress = 10 + int((idx / total_count) * 60)

        # [2-4/5] 调用 ffprobe / 解析 JSON / 质量审计
        update_step(current_progress, f"[2-4/5] 扫描中 ({idx}/{total_count}): {file_name}")

        try:
            video = VideoFile(full_path)
            item_data = {
                "file_name": video.get_name(), "resolution": video.get_resolution(),
                "codec": video.get_codec(), "status": video.check_compliance(), "timestamp": audit_timestamp
            }
            report_list.append(item_data)
            report_text += f"【资产】: {item_data['file_name']}\n【审计】: {item_data['resolution']} -> {item_data['status']}\n" + "-" * 40 + "\n"
        except Exception as file_err:
            report_text += f"⚠️【损坏资产】: {file_name} (解析失败: {str(file_err)})\n" + "-" * 40 + "\n"

    # [5/5] 输出结果...
    update_step(85, "[5/5] 采集完毕，正在生成本地 CSV/JSON 报告...")
    save_local_files(os.path.join(target_dir, "report"), report_list, audit_timestamp)

    update_step(95, "[5/5] TCP 传输结果到云服务器中")
    vps_result = upload_to_vps(report_list)
    report_text += vps_result

    update_step(100, "🏁 审计就绪")
    progress_win.destroy()

    # 前端顶部告示
    messagebox.showinfo("基于python的视频审计软件（覃昊天面试深圳阿特辣用）", report_text)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    run_audit()