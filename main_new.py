import tkinter as tk
from tkinter import ttk
from monitor_utils import get_monitors, update_monitor_info, on_monitor_select
from coordinate_utils import on_canvas_click, save_location, run_click
from storage_utils import load_coordinates_from_storage, update_name, delete_item
from misc import show_saved_rectangle_image_from_listbox, show_current_rectangle_image_from_listbox
import elements
import misc

# Tkinter arayüzü oluşturalım
root = tk.Tk()
root.title("Monitör Seçimi ve Durumu")

# create global coordinates
drawmode_point = elements.DrawMode('Point')
drawmode_rect = elements.DrawMode('Rectangle')
coordinates = [drawmode_point, drawmode_rect]

# Monitörleri alalım
monitors = get_monitors()

# Ana çerçeve
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Sol tarafta monitör seçenekleri
monitor_listbox = tk.Listbox(main_frame, height=len(monitors))
for idx, monitor in enumerate(monitors):
    monitor_listbox.insert(tk.END, f"Monitör {idx + 1}: {monitor['width']}x{monitor['height']}")
monitor_listbox.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

# Sağ tarafta monitör bilgisi ve görüntüsü için alan
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

# Monitör bilgisi etiketi
monitor_info_label = tk.Label(right_frame, text="Monitör Bilgisi Görüntüleniyor...", justify=tk.LEFT)
monitor_info_label.pack(anchor="n")

# Seçim modunu belirleyecek radio butonları
radio_frame = tk.Frame(right_frame)
radio_frame.pack(pady=10)

# Radiobutton'lar DrawMode.active_mode'a bağlanıyor
radio_point = tk.Radiobutton(radio_frame, text="Point", variable=elements.DrawMode.active_mode, value=1)
radio_point.pack(side=tk.LEFT)

radio_rectangle = tk.Radiobutton(radio_frame, text="Rectangle", variable=drawmode_point.active_mode, value=2)
radio_rectangle.pack(side=tk.LEFT)

# İsim giriş alanı
name_label = tk.Label(right_frame, text="İsim:")
name_label.pack(anchor="w")

#name etry class called
name_entry = elements.name_entry(right_frame)
name_entry.name_input.pack(fill=tk.X, padx=10, pady=5)

# Güncelle ve Sil butonları
button_frame = tk.Frame(right_frame)
button_frame.pack(pady=10)

update_button = tk.Button(button_frame, text="Rename")
update_button.pack(side=tk.LEFT, padx=10)

delete_button = tk.Button(button_frame, text="Delete")
delete_button.pack(side=tk.LEFT, padx=10)

# Canvas monitör görüntüsünü barındıracak
monitor_canvas = tk.Canvas(right_frame, bg="black")
monitor_canvas.pack(fill=tk.BOTH, expand=True)

# Koordinatları kaydetme butonu
save_button = elements.m_button(right_frame, "Save Coordinate")
save_button.button.pack(pady=10)

# Koordinat listesi (Point)
coordinates_listbox = elements.listdrawer(right_frame, 1)
coordinates_listbox.listbox.pack(fill=tk.X, pady=10)

# Rectangle listesi
rectangles_listbox = elements.listdrawer(right_frame, 2)
rectangles_listbox.listbox.pack(fill=tk.X, pady=10)

listboxs = [coordinates_listbox, rectangles_listbox]

# Butonlar için alt çerçeve oluştur
buttons_frame = tk.Frame(right_frame)
buttons_frame.pack(pady=5)

# "Show Saved" butonu
show_saved_button = tk.Button(buttons_frame, text="Show Saved", command=lambda: show_saved_rectangle_image_from_listbox(root))
show_saved_button.pack(side=tk.LEFT, padx=5)

# "Show Current" butonu
show_current_button = tk.Button(buttons_frame, text="Show Saved", command=lambda: show_current_rectangle_image_from_listbox(root))
show_current_button.pack(side=tk.LEFT, padx=5)

# Koordinata tıklama butonu
run_click_button = tk.Button(right_frame, text="Run Click", command=run_click(coordinates_listbox))
run_click_button.pack(pady=10)

# Sağdaki çerçevenin dinamik olarak genişleyip küçülmesini sağla
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(0, weight=1)

# Canvas tıklama olayı için işleyici
monitor_canvas.bind("<Button-1>", lambda event: on_canvas_click(event, monitor_listbox, monitors, monitor_canvas, elements.DrawMode.active_mode.get(), name_entry, save_button, drawmode_point, drawmode_rect))

save_button.button.config(command=lambda: save_location(name_entry))
update_button.config(command=lambda: update_name(name_entry))
delete_button.config(command=lambda: delete_item())

# Seçilen monitör değiştiğinde işleyici
monitor_listbox.bind("<<ListboxSelect>>", lambda event: on_monitor_select(event, monitor_listbox, monitors, monitor_canvas, monitor_info_label))

# Program başlarken klasörleri tarayıp Listbox'ları doldur
load_coordinates_from_storage(coordinates_listbox, rectangles_listbox)

# Arayüzü başlatalım
root.mainloop()
