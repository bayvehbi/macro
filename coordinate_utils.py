import pyautogui
import tkinter as tk
from PIL import Image, ImageTk
import mss
import os
from storage_utils import save_to_json, get_screenshot, rename_coordinate_folder
from elements import listdrawer, DrawMode
import shutil

# Global değişkenlerin varsayılan değerleri
last_click_x = None
last_click_y = None
rectangle_start_x = None
rectangle_start_y = None

storage_folder = os.path.join("storage", "coordinates")


def save_location(name_entry):
    active_coords = DrawMode.find_instances_by_mode(DrawMode.active_mode.get())
    active_list = listdrawer.get_instance(DrawMode.active_mode.get())

    if active_coords.has_data is False:
        return

    coord_name = name_entry.name_input.get() or active_coords.type
    print(coord_name)

    active_list.list_update(coord_name)
    save_to_json(coord_name, active_coords.type, active_coords.coordinates)

    rect_folder = os.path.join(storage_folder, "Rectangle", coord_name)

    img = get_screenshot(active_coords.coordinates)
    
    # Klasör oluştur ve görüntüyü kaydet
    if not os.path.exists(rect_folder):
        os.makedirs(rect_folder)
    
    image_path = os.path.join(rect_folder, "image.png")
    img.save(image_path)


def run_click(coordinates_listbox):
    coordinates_listbox = coordinates_listbox.listbox
    selected_coord = coordinates_listbox.curselection()
    if selected_coord:
        coord_text = coordinates_listbox.get(selected_coord[0])
        coord_text = coord_text.split(":")[1].strip(" ()")
        coord_x, coord_y = map(int, coord_text.split(", "))
        
        pyautogui.click(x=coord_x, y=coord_y)


# Canvas tıklama olayı için işlev
def on_canvas_click(event, monitor_listbox, monitors, monitor_canvas, draw_mode, name_entry, save_button, point_coord, rect_coord):
    global last_click_x, last_click_y, rectangle_start_x, rectangle_start_y

    # Tıkladığınız canvas üzerindeki koordinatları al
    canvas_x = event.x
    canvas_y = event.y
    # Seçilen monitöre göre gerçek koordinatları hesapla
    selected_monitor = monitor_listbox.curselection()
    if selected_monitor:
        selected_monitor = int(selected_monitor[0])
        monitor = monitors[selected_monitor]

        # Gerçek monitör koordinatlarına dönüştür
        monitor_x = int(monitor['x'] + (canvas_x * monitor['width'] / monitor_canvas.winfo_width()))
        monitor_y = int(monitor['y'] + (canvas_y * monitor['height'] / monitor_canvas.winfo_height()))

        print(point_coord.coordinates)
        print(rect_coord.coordinates)
        print(draw_mode)
        # Point selected
        if draw_mode == 1:
            save_button.button.config(state=tk.NORMAL)
            point_coord.update_coordinates([monitor_x, monitor_y])
            print(f"Point selected: ({point_coord.coordinates[0]}, {point_coord.coordinates[1]})")
        
        # Rectangle selected
        elif draw_mode == 2:
            if rect_coord.coordinates['start'] == [] or rect_coord.coordinates['end'] != []:
                # İlk tıklama
                rectangle_start_x = monitor_x
                rectangle_start_y = monitor_y
                save_button.button.config(state=tk.DISABLED)
                rect_coord.update_coordinates({"start": [rectangle_start_x, rectangle_start_y], "end": []})
                print(f"Rectangle starting point: ({monitor_x}, {monitor_y})")
            else:
                # İkinci tıklama: Rectangle create

                rectangle_end_x = monitor_x
                rectangle_end_y = monitor_y
                save_button.button.config(state=tk.NORMAL)
                rect_coord.update_coordinates({"start": [rectangle_start_x, rectangle_start_y], "end": [rectangle_end_x, rectangle_end_y]})
                print(f"Rectangle ending point: ({rectangle_end_x}, {rectangle_end_y})")
