import mss
from PIL import Image, ImageTk
import win32api
import win32con
import tkinter as tk


def get_monitors():
    monitors = []
    i = 0
    while True:
        try:
            monitor_info = win32api.EnumDisplayDevices(None, i)
            monitor_settings = win32api.EnumDisplaySettings(monitor_info.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
            monitors.append({
                "device_name": monitor_info.DeviceName,
                "width": monitor_settings.PelsWidth,
                "height": monitor_settings.PelsHeight,
                "x": monitor_settings.Position_x,
                "y": monitor_settings.Position_y
            })
            i += 1
        except:
            break
    return monitors

def update_monitor_info(selected_monitor, monitors, canvas):
    if selected_monitor is not None:
        monitor = monitors[selected_monitor]

        with mss.mss() as sct:
            monitor_region = {
                "top": monitor["y"],
                "left": monitor["x"],
                "width": monitor["width"],
                "height": monitor["height"]
            }
            screenshot = sct.grab(monitor_region)
            img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
            screenshot_tk = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)
            canvas.image = screenshot_tk

def on_monitor_select(event, monitor_listbox, monitors, monitor_canvas, monitor_info_label):
    selected_monitor = monitor_listbox.curselection()
    if selected_monitor:
        selected_monitor = int(selected_monitor[0])
        update_monitor_info(selected_monitor, monitors, monitor_canvas)
    else:
        monitor_info_label.config(text="Monitör Seçilmedi.")
