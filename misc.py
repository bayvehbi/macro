import os
import json
from PIL import Image, ImageTk
import tkinter as tk
import mss
from elements import listdrawer, DrawMode, name_entry
import shutil
from tkinter import messagebox
from storage_utils import get_screenshot

# Ana dizin ve koordinat klasörlerini oluşturma


# Show anlık fotoğraf alıp gösteren fonksiyon
def show_saved_rectangle_image_from_listbox(root):
    selected_rect = listdrawer.get_active_instance()
    storage_folder = os.path.join("storage", "coordinates", "Rectangle")

    if selected_rect and selected_rect.name == "Rectangle":
        rect_text = selected_rect.listbox.get(selected_rect.listbox.curselection()[0])
        rect_name = rect_text.split(":")[0]
        
        # Klasörde kaydedilen resmi bul
        image_path = os.path.join(storage_folder, rect_name.strip(), "image.png")
        
        if os.path.exists(image_path):
            # Resmi yükle ve göster
            img = Image.open(image_path)
            view_window = tk.Toplevel(root)
            view_window.title(f"Kaydedilen Görüntü: {rect_name.strip()}")
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(view_window, image=img_tk)
            label.image = img_tk  # Referans tutmak için
            label.pack()
        else:
            print(f"Görüntü bulunamadı: {image_path}")


# Show anlık fotoğraf alıp gösteren fonksiyon
def show_current_rectangle_image_from_listbox(root):
    selected_rect = listdrawer.get_active_instance()
    storage_folder = os.path.join("storage", "coordinates", "Rectangle")

    if selected_rect and selected_rect.name == "Rectangle":
        rect_text = selected_rect.listbox.get(selected_rect.listbox.curselection()[0])
        rect_name, rect_coords = rect_text.split(":", 1) 
        rect_name = rect_name.strip()
        rect_coords = rect_coords.strip()
        rect_coords = eval(rect_coords)

        
        # Klasörde kaydedilen resmi bul
        image_path = os.path.join(storage_folder, rect_name.strip(), "image.png")
        
        if os.path.exists(image_path):
            # Resmi yükle ve göster
            img = get_screenshot(rect_coords)
            # Yeni bir pencere açarak görüntüyü göster
            view_window = tk.Toplevel(root)
            view_window.title(f"Güncel Görüntü: {rect_name.strip()}")
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(view_window, image=img_tk)
            label.image = img_tk  # Referans tutmak için
            label.pack()
