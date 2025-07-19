# USB Drive Logger
#  Developed by GH0STH4CKER
# https://github.com/GH0STH4CKER
import os
import time
import ctypes
from ctypes import wintypes
from datetime import datetime

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
LOG_FILE = "usb_activity_log.txt" # Add a path to change where it saves. ex- C:\Users\...log.txt

def get_logical_drives():
    drives_bitmask = kernel32.GetLogicalDrives()
    drives = []
    for i in range(26):
        if drives_bitmask & (1 << i):
            drives.append(chr(ord('A') + i) + ':')
    return drives

def get_drive_type(drive):
    DRIVE_REMOVABLE = 2
    return kernel32.GetDriveTypeW(f"{drive}\\") == DRIVE_REMOVABLE

def get_volume_label(drive):
    volume_name_buffer = ctypes.create_unicode_buffer(1024)
    fs_name_buffer = ctypes.create_unicode_buffer(1024)
    serial_number = wintypes.DWORD()
    max_component_len = wintypes.DWORD()
    file_system_flags = wintypes.DWORD()

    res = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive + "\\"),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        ctypes.byref(serial_number),
        ctypes.byref(max_component_len),
        ctypes.byref(file_system_flags),
        fs_name_buffer,
        ctypes.sizeof(fs_name_buffer),
    )
    return volume_name_buffer.value if res else "Unknown"

def list_drive_contents(drive):
    contents = []
    try:
        for item in os.listdir(drive + "\\"):
            full_path = os.path.join(drive + "\\", item)
            if os.path.isdir(full_path):
                contents.append(f"[Folder] {item}")
            else:
                contents.append(f"[File]   {item}")
    except Exception as e:
        contents.append(f"[Error reading contents: {e}]")
    return contents

def log_event(text, include_timestamp=True):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") if include_timestamp else ""
    entry = f"{timestamp} {text}\n" if include_timestamp else f"{text}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(entry)
    print(entry.strip())

def main():
    print("Monitoring for USB drives. Press Ctrl+C to stop.")
    previous_drives = get_logical_drives()

    while True:
        time.sleep(2)
        current_drives = get_logical_drives()
        new_drives = [d for d in current_drives if d not in previous_drives]

        for d in new_drives:
            if get_drive_type(d):
                label = get_volume_label(d)
                log_event(f"USB inserted: Drive {d} | Label: {label}")
                log_event("Contents:")
                for line in list_drive_contents(d):
                    log_event(f"    {line}", include_timestamp=False)
                log_event("-" * 40, include_timestamp=False)
            else:
                log_event(f"New non-removable drive detected: {d}")

        removed_drives = [d for d in previous_drives if d not in current_drives]
        for d in removed_drives:
            log_event(f"Drive removed: {d}")

        previous_drives = current_drives

if __name__ == "__main__":
    main()
