import os
import json
from PIL import Image
import tkinter as tk
import mss
from elements import listdrawer, DrawMode, name_entry
import shutil
from tkinter import messagebox

# Ana dizin ve koordinat klasörlerini oluşturma
storage_folder = "storage"
storage_folder = os.path.join(storage_folder, "coordinates")

# JSON dosyasına kaydetme fonksiyonu
def save_to_json(unique_name, obj_type, coords):
    # Unique klasörü oluştur

    obj_folder = os.path.join(storage_folder, obj_type)
    obj_folder = os.path.join(obj_folder, unique_name)

    if not os.path.exists(obj_folder):
        os.makedirs(obj_folder)
    
    # JSON dosyasının içeriği
    data = {
        "active": True,
        "type": obj_type,
        "coordinates": coords
    }
    
    # JSON dosyasını kaydet
    json_path = os.path.join(obj_folder, "data.json")
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON kaydedildi: {json_path}")
    return obj_folder


def load_coordinates_from_storage(coordinates_listbox, rectangles_listbox):
    # Listbox'ları ayarlıyoruz
    coordinates_listbox = coordinates_listbox.listbox
    rectangles_listbox = rectangles_listbox.listbox

    # Tüm DrawMode instance'larını kontrol ediyoruz
    for instance in DrawMode.instances:
        # Her bir instance için storage_folder'da bir klasör olup olmadığını kontrol ediyoruz
        instance_folder = os.path.join(storage_folder, instance.type)
        
        if os.path.exists(instance_folder):
            for folder_name in os.listdir(instance_folder):
                folder_path = os.path.join(instance_folder, folder_name)
                json_file_path = os.path.join(folder_path, "data.json")

                if os.path.isdir(folder_path) and os.path.exists(json_file_path):
                    # JSON dosyasını aç ve veriyi al
                    with open(json_file_path, 'r') as json_file:
                        data = json.load(json_file)

                    # Koordinat türüne göre ilgili Listbosx'a ekle
                    if instance.type == 'Point':
                        coords = data['coordinates']
                        coordinates_listbox.insert(tk.END, f"{folder_name}: ({coords[0]}, {coords[1]})")
                    elif instance.type == 'Rectangle':
                        coords = data['coordinates']
                        rectangles_listbox.insert(tk.END, f"{folder_name}: ({coords['start'][0]}, {coords['start'][1]}) - ({coords['end'][0]}, {coords['end'][1]})")


# Ekran görüntüsü alma fonksiyonu (Bu fonksiyon monitor_utils.py'da da yer alabilir)
def get_screenshot(rect_coords_str):
    # Start ve end koordinatlarını doğrudan sözlükten al
    start_coords = rect_coords_str['start']
    end_coords = rect_coords_str['end']

    with mss.mss() as sct:
        monitor_region = {
            "top": start_coords[1],
            "left": start_coords[0],
            "width": abs(end_coords[0] - start_coords[0]),
            "height": abs(end_coords[1] - start_coords[1])
        }
        screenshot = sct.grab(monitor_region)
        img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
        return img


def delete_item():
    # Mevcut aktif listbox instance'ını alıyoruz
    active_list = listdrawer.get_active_instance()

    if active_list:
        # Seçili öğe olup olmadığını kontrol ediyoruz
        selected_indices = active_list.listbox.curselection()

        if selected_indices:
            # Seçilen öğeyi alıp siliyoruz
            selected_index = selected_indices[0]
            selected_item = active_list.listbox.get(selected_index)
            active_list.listbox.delete(selected_index)

            # Seçilen öğenin ismini alıyoruz (örneğin "folder_name: (x, y)" gibi)
            folder_name = selected_item.split(":")[0]

            # Klasör yolunu oluşturuyoruz
            folder_path = os.path.join(storage_folder, active_list.name, folder_name)

            # Klasörün var olup olmadığını kontrol ediyoruz ve siliyoruz
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Klasör silindi: {folder_path}")
            else:
                print(f"Hata: '{folder_path}' klasörü bulunamadı.")
        else:
            print("Hata: Listede seçili bir öğe yok.")
    else:
        print("Hata: Aktif bir liste bulunamadı.")


def rename_coordinate_folder(old_name, new_name, listbox):
    coordinates_folder = os.path.join(storage_folder, listbox.name)
    old_folder = os.path.join(coordinates_folder, old_name)
    new_folder = os.path.join(coordinates_folder, new_name)

    # Klasör varsa yeniden adlandır
    if os.path.exists(old_folder):
        os.rename(old_folder, new_folder)
        print(f"Klasör ismi değiştirildi: {old_name} -> {new_name}")
    else:
        print(f"Hata: '{old_name}' klasörü bulunamadı.")


def update_name(name_entry):
    if DrawMode.active_mode.get() == listdrawer.get_active_instance().type:
        active_listbox = listdrawer.get_active_instance()
        new_name = name_entry.name_input.get()
        if active_listbox.listbox.curselection() != ():
            selected_index = active_listbox.listbox.curselection()[0]
            coord_text = active_listbox.listbox.get(selected_index)
            active_listbox.list_update(new_name)
            active_listbox.listbox.delete(selected_index)
            rename_coordinate_folder(coord_text.split(':')[0], new_name, active_listbox)
        else:
            print("Warning: No listbox is selected.")
    else:
        print("Warning: Active mode is not equal to active listbox type.")
        messagebox.showwarning("Warning: Active mode is not equal to active listbox type.")

