import tkinter as tk
from PIL import Image, ImageTk
import win32api
import win32con
import mss
import pyautogui
import os
import json

# Global değişkenlerin varsayılan değerleri
last_click_x = None
last_click_y = None
rectangle_start_x = None
rectangle_start_y = None

# Tkinter arayüzü oluşturalım
root = tk.Tk()
root.title("Monitör Seçimi ve Durumu")

# Seçim modu: 1 -> Nokta, 2 -> Dikdörtgen
selection_mode = tk.IntVar(value=1)
# Ana dizin ve koordinat klasörlerini oluşturma
storage_folder = "storage"
coordinates_folder = os.path.join(storage_folder, "coordinats")


# Monitör bilgilerini al
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

# Ekran görüntüsünü al ve göster
def update_monitor_info(selected_monitor, canvas):
    if selected_monitor is not None:
        monitor = monitors[selected_monitor]

        # mss kullanarak ekran görüntüsünü al
        with mss.mss() as sct:
            monitor_region = {
                "top": monitor["y"],
                "left": monitor["x"],
                "width": monitor["width"],
                "height": monitor["height"]
            }
            screenshot = sct.grab(monitor_region)
            img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

            # Görüntüyü canvas boyutuna göre yeniden boyutlandır
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
            screenshot_tk = ImageTk.PhotoImage(img)
        
            # Görüntüyü canvas üzerine çiz
            canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)
            canvas.image = screenshot_tk  # Referansı sakla

def on_monitor_select(event):
    # Seçilen monitörü güncelle
    selected_monitor = monitor_listbox.curselection()
    if selected_monitor:
        selected_monitor = int(selected_monitor[0])
        update_monitor_info(selected_monitor, monitor_canvas)
    else:
        monitor_info_label.config(text="Monitör Seçilmedi.")


# Dikdörtgen kaydetme fonksiyonu
def save_rectangle(rect_name, start_coords, end_coords):
    # Dikdörtgeni listeye ekle
    rectangles_listbox.insert(tk.END, f"{rect_name}: ({start_coords[0]}, {start_coords[1]}) - ({end_coords[0]}, {end_coords[1]})")

    # JSON olarak kaydet
    coords = {
        "start": start_coords,
        "end": end_coords
    }
    save_to_json(rect_name, "Dikdörtgen", coords)


# Canvas tıklama olayı için işlev
def on_canvas_click(event):
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

        # Nokta seçiliyse
        if selection_mode.get() == 1:
            last_click_x = monitor_x
            last_click_y = monitor_y
            print(f"Nokta seçildi: ({monitor_x}, {monitor_y})")
        
        # Dikdörtgen seçiliyse
        elif selection_mode.get() == 2:
            if rectangle_start_x is None and rectangle_start_y is None:
                # İlk tıklama
                rectangle_start_x = monitor_x
                rectangle_start_y = monitor_y
                print(f"Dikdörtgen başlangıç noktası: ({monitor_x}, {monitor_y})")
            else:
                # İkinci tıklama: Dikdörtgeni oluştur
                rectangle_end_x = monitor_x
                rectangle_end_y = monitor_y
                print(f"Dikdörtgen bitiş noktası: ({rectangle_end_x}, {rectangle_end_y})")

                # Dikdörtgeni kaydet
                rect_name = name_entry.get() or "Dikdörtgen"
                save_rectangle(rect_name, [rectangle_start_x, rectangle_start_y], [rectangle_end_x, rectangle_end_y])
                
                # Dikdörtgeni sıfırla
                rectangle_start_x = None
                rectangle_start_y = None

# Koordinatları kaydet (Nokta için)
def save_location():
    global last_click_x, last_click_y

    if last_click_x is None or last_click_y is None:
        # Eğer canvas üzerinde hiç tıklama yapılmadıysa hata vermeden çık
        return

    # Noktayı isimlendirme
    point_name = name_entry.get() or "Nokta"
    
    # Koordinatları listeye ekle
    coordinates_listbox.insert(tk.END, f"{point_name}: ({last_click_x}, {last_click_y})")


def rename_coordinate_folder(old_name, new_name):
    old_folder = os.path.join(coordinates_folder, old_name)
    new_folder = os.path.join(coordinates_folder, new_name)

    # Klasör varsa yeniden adlandır
    if os.path.exists(old_folder):
        os.rename(old_folder, new_folder)
        print(f"Klasör ismi değiştirildi: {old_name} -> {new_name}")
    else:
        print(f"Hata: '{old_name}' klasörü bulunamadı.")


# Seçili ismi değiştirme işlevi (Nokta veya Dikdörtgen)
def update_name():
    if coordinates_listbox.curselection():
        selected_index = coordinates_listbox.curselection()[0]
        new_name = name_entry.get()
        if new_name:
            # Koordinat ismini güncelle
            coord_text = coordinates_listbox.get(selected_index)
            coord_info = coord_text.split(":")[1]
            coordinates_listbox.delete(selected_index)
            coordinates_listbox.insert(selected_index, f"{new_name}: {coord_info}")
            rename_coordinate_folder(rect_text.split(':')[0], new_name)
    elif rectangles_listbox.curselection():
        selected_index = rectangles_listbox.curselection()[0]
        new_name = name_entry.get()
        if new_name:
            # Dikdörtgen ismini güncelle
            rect_text = rectangles_listbox.get(selected_index)
            rect_info = rect_text.split(":")[1]
            rectangles_listbox.delete(selected_index)
            rectangles_listbox.insert(selected_index, f"{new_name}: {rect_info}")
            rename_coordinate_folder(rect_text.split(':')[0], new_name)


# Seçili öğeyi silme işlevi
def delete_item():
    if coordinates_listbox.curselection():
        selected_index = coordinates_listbox.curselection()[0]
        coordinates_listbox.delete(selected_index)
    elif rectangles_listbox.curselection():
        selected_index = rectangles_listbox.curselection()[0]
        rectangles_listbox.delete(selected_index)

# Koordinata tıklama yap
def run_click():
    selected_coord = coordinates_listbox.curselection()
    if selected_coord:
        coord_text = coordinates_listbox.get(selected_coord)
        coord_text = coord_text.split(":")[1].strip(" ()")
        coord_x, coord_y = map(int, coord_text.split(", "))
        
        # Seçilen koordinata sol tıklama yap
        pyautogui.click(x=coord_x, y=coord_y)


# Show anlık fotoğraf alıp gösteren fonksiyon
def show_current_rectangle_image_from_listbox():
    selected_rect = rectangles_listbox.curselection()
    if selected_rect:
        rect_text = rectangles_listbox.get(selected_rect[0])
        rect_name, rect_coords = rect_text.split(":")
        
        # Koordinatları düzgün şekilde işlemek için ayırıyoruz
        rect_coords = rect_coords.strip().replace("(", "").replace(")", "")
        start_coords_str, end_coords_str = rect_coords.split("-")
        start_coords = [int(x.strip()) for x in start_coords_str.split(",")]
        end_coords = [int(x.strip()) for x in end_coords_str.split(",")]

        # Şimdiki ekran görüntüsünü al ve göster
        with mss.mss() as sct:
            monitor_region = {
                "top": start_coords[1],
                "left": start_coords[0],
                "width": abs(end_coords[0] - start_coords[0]),
                "height": abs(end_coords[1] - start_coords[1])
            }
            screenshot = sct.grab(monitor_region)
            img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

            # Yeni bir pencere açarak görüntüyü göster
            view_window = tk.Toplevel(root)
            view_window.title(f"Güncel Görüntü: {rect_name.strip()}")
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(view_window, image=img_tk)
            label.image = img_tk  # Referans tutmak için
            label.pack()


# Show anlık fotoğraf alıp gösteren fonksiyon
def show_saved_rectangle_image_from_listbox():
    selected_rect = rectangles_listbox.curselection()
    if selected_rect:
        rect_text = rectangles_listbox.get(selected_rect[0])
        rect_name, rect_coords = rect_text.split(":")
        
        # Koordinatları düzgün şekilde işlemek için ayırıyoruz
        rect_coords = rect_coords.strip().replace("(", "").replace(")", "")
        start_coords_str, end_coords_str = rect_coords.split("-")
        start_coords = [int(x.strip()) for x in start_coords_str.split(",")]
        end_coords = [int(x.strip()) for x in end_coords_str.split(",")]

        # Şimdiki ekran görüntüsünü al ve göster
        with mss.mss() as sct:
            monitor_region = {
                "top": start_coords[1],
                "left": start_coords[0],
                "width": abs(end_coords[0] - start_coords[0]),
                "height": abs(end_coords[1] - start_coords[1])
            }
            screenshot = sct.grab(monitor_region)
            img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

            # Yeni bir pencere açarak görüntüyü göster
            view_window = tk.Toplevel(root)
            view_window.title(f"Güncel Görüntü: {rect_name.strip()}")
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(view_window, image=img_tk)
            label.image = img_tk  # Referans tutmak için
            label.pack()


# JSON dosyasına kaydetme fonksiyonu
def save_to_json(unique_name, obj_type, coords):
    # Unique klasörü oluştur
    obj_folder = os.path.join(coordinates_folder, unique_name)
    if not os.path.exists(obj_folder):
        os.makedirs(obj_folder)
    
    # JSON dosyasının içeriği
    data = {
        "type": obj_type,
        "coordinates": coords
    }
    
    # JSON dosyasını kaydet
    json_path = os.path.join(obj_folder, f"{unique_name}.json")
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON kaydedildi: {json_path}")


# Nokta kaydetme fonksiyonu
def save_location():
    global last_click_x, last_click_y

    if last_click_x is None or last_click_y is None:
        return

    # Noktayı isimlendirme
    point_name = name_entry.get() or "Nokta"
    
    # Koordinatları listeye ekle
    coordinates_listbox.insert(tk.END, f"{point_name}: ({last_click_x}, {last_click_y})")

    # JSON olarak kaydet
    coords = [last_click_x, last_click_y]
    save_to_json(point_name, "Nokta", coords)


# Pencere yeniden boyutlandırıldığında güncellemeyi tetiklemek için gecikmeli mekanizma
def on_resize(event):
    global resize_job
    if resize_job is not None:
        root.after_cancel(resize_job)
    
    # Yeniden boyutlandırma işlemi tamamlandıktan sonra 200ms bekle ve güncelle
    resize_job = root.after(200, lambda: on_monitor_select(None))

# Yeniden boyutlandırmayı gecikmeli olarak işlemek için bir iş tanımlayıcı
resize_job = None

# Pencere yeniden boyutlandırıldığında tetiklenen olay
root.bind("<Configure>", on_resize)

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

# Seçim modunu belirleyecek radio butonları (Nokta / Dikdörtgen)
radio_frame = tk.Frame(right_frame)
radio_frame.pack(pady=10)

radio_point = tk.Radiobutton(radio_frame, text="Nokta", variable=selection_mode, value=1)
radio_point.pack(side=tk.LEFT)

radio_rectangle = tk.Radiobutton(radio_frame, text="Dikdörtgen", variable=selection_mode, value=2)
radio_rectangle.pack(side=tk.LEFT)

# İsim giriş alanı (Nokta/Dikdörtgen için)
name_label = tk.Label(right_frame, text="İsim:")
name_label.pack(anchor="w")

name_entry = tk.Entry(right_frame)
name_entry.pack(fill=tk.X, padx=10, pady=5)

# Güncelle ve Sil butonları
button_frame = tk.Frame(right_frame)
button_frame.pack(pady=10)

update_button = tk.Button(button_frame, text="Rename", command=update_name)
update_button.pack(side=tk.LEFT, padx=10)

delete_button = tk.Button(button_frame, text="Delete", command=delete_item)
delete_button.pack(side=tk.LEFT, padx=10)

# Canvas monitör görüntüsünü barındıracak
monitor_canvas = tk.Canvas(right_frame, bg="black")
monitor_canvas.pack(fill=tk.BOTH, expand=True)

# Canvas tıklama olayı için işleyici
monitor_canvas.bind("<Button-1>", on_canvas_click)

# Create a frame for the buttons
button_frame = tk.Frame(right_frame)
button_frame.pack(pady=10)

# Koordinatları kaydetme butonu (Nokta için)
save_button = tk.Button(button_frame, text="Koordinat Kaydet", command=save_location)
save_button.pack(side=tk.LEFT, padx=5)

# Show coordinat button (For rectangle)
show_coordinat_button = tk.Button(button_frame, text="Koordinat Göster", command=show_current_rectangle_image_from_listbox)
show_coordinat_button.pack(side=tk.LEFT, padx=5)

# Show object button (For rectangle)
show_object_button = tk.Button(button_frame, text="Görüntüyü Göster", command=save_location)
show_object_button.pack(side=tk.LEFT, padx=5)

# Koordinat listesi (Nokta)
coordinates_listbox = tk.Listbox(right_frame)
coordinates_listbox.pack(fill=tk.X, pady=10)

# Rectangle listesi
rectangles_listbox = tk.Listbox(right_frame)
rectangles_listbox.pack(fill=tk.X, pady=10)

# Koordinata tıklama butonu (Nokta için)
run_click_button = tk.Button(right_frame, text="Run Click", command=run_click)
run_click_button.pack(pady=10)

# Sağdaki çerçevenin dinamik olarak genişleyip küçülmesini sağla
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(0, weight=1)

# Seçilen monitör değiştiğinde işleyici
monitor_listbox.bind("<<ListboxSelect>>", on_monitor_select)

# Arayüzü başlatalım
root.mainloop()
