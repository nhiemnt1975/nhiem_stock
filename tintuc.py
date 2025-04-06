import subprocess
import sys
import time
from threading import Thread


def run_script(script_name):
    """Hàm chạy một script Python"""
    try:
        print(f"Đang khởi chạy {script_name}...")
        process = subprocess.Popen([sys.executable, script_name])
        return process
    except Exception as e:
        print(f"Lỗi khi chạy {script_name}: {e}")
        return None


def monitor_processes(processes):
    """Hàm giám sát các tiến trình và khởi động lại nếu bị dừng"""
    while True:
        for i, (name, process) in enumerate(processes):
            if process.poll() is not None:  # Kiểm tra nếu tiến trình đã kết thúc
                print(f"{name} đã dừng, đang khởi động lại...")
                new_process = run_script(name)
                if new_process:
                    processes[i] = (name, new_process)
        time.sleep(5)  # Kiểm tra mỗi 5 giây


def main():
    scripts = [
        ("tintuc_vnexpress.py", None),
        ("tintuc_vietstock.py", None)
    ]

    # Khởi chạy tất cả các script
    for i, (name, _) in enumerate(scripts):
        process = run_script(name)
        if process:
            scripts[i] = (name, process)

    # Bắt đầu thread giám sát
    monitor_thread = Thread(target=monitor_processes, args=(scripts,))
    monitor_thread.daemon = True
    monitor_thread.start()

    print("Đang chạy cả 2 script. Nhấn Ctrl+C để dừng...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang dừng tất cả các tiến trình...")
        for name, process in scripts:
            if process:
                process.terminate()
        print("Đã dừng tất cả các tiến trình.")


if __name__ == "__main__":
    main()