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

# Seçim modu: 1 -> Point, 2 -> Rectangle
selection_mode = tk.IntVar(value=1)
# Ana dizin ve koordinat klasörlerini oluşturma
storage_folder = "storage"
coordinates_folder = os.path.join(storage_folder, "coordinates")


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


# Rectangle kaydetme fonksiyonu
def save_rectangle(rect_name, start_coords, end_coords):
    # Rectangle add to list
    rectangles_listbox.insert(tk.END, f"{rect_name}: ({start_coords[0]}, {start_coords[1]}) - ({end_coords[0]}, {end_coords[1]})")
    
    # JSON olarak kaydet
    coords = {
        "start": start_coords,
        "end": end_coords
    }
    obj_folder = save_to_json(rect_name, "Rectangle", coords)

    # Anlık ekran görüntüsünü al ve uygun yere kaydet
    img = get_screenshot(f"({start_coords[0]}, {start_coords[1]}) - ({end_coords[0]}, {end_coords[1]})")
    
    # Klasör oluştur ve görüntüyü kaydet
    if not os.path.exists(obj_folder):
        os.makedirs(obj_folder)
    
    image_path = os.path.join(obj_folder, "image.png")
    img.save(image_path)
    
    print(f"Ekran görüntüsü kaydedildi: {image_path}")


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

        # Point selected
        if selection_mode.get() == 1:
            last_click_x = monitor_x
            last_click_y = monitor_y
            print(f"Point selected: ({monitor_x}, {monitor_y})")
        
        # Rectangle selected
        elif selection_mode.get() == 2:
            if rectangle_start_x is None and rectangle_start_y is None:
                # İlk tıklama
                rectangle_start_x = monitor_x
                rectangle_start_y = monitor_y
                print(f"Rectangle starting point: ({monitor_x}, {monitor_y})")
            else:
                # İkinci tıklama: Rectangle create
                rectangle_end_x = monitor_x
                rectangle_end_y = monitor_y
                print(f"Rectangle ending point: ({rectangle_end_x}, {rectangle_end_y})")

                # Rectangle save
                rect_name = name_entry.get() or "Rectangle"
                save_rectangle(rect_name, [rectangle_start_x, rectangle_start_y], [rectangle_end_x, rectangle_end_y])
                
                # Rectangle reset
                rectangle_start_x = None
                rectangle_start_y = None


def rename_coordinate_folder(old_name, new_name):
    old_folder = os.path.join(coordinates_folder, old_name)
    new_folder = os.path.join(coordinates_folder, new_name)

    # Klasör varsa yeniden adlandır
    if os.path.exists(old_folder):
        os.rename(old_folder, new_folder)
        print(f"Klasör ismi değiştirildi: {old_name} -> {new_name}")
    else:
        print(f"Hata: '{old_name}' klasörü bulunamadı.")


# Seçili ismi değiştirme işlevi (Point or Rectangle)
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
            rename_coordinate_folder(coord_text.split(':')[0], new_name)
    elif rectangles_listbox.curselection():
        selected_index = rectangles_listbox.curselection()[0]
        new_name = name_entry.get()
        if new_name:
            # Rectangle rename
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



def get_screenshot(rect_coords):
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
        return img


# Show anlık fotoğraf alıp gösteren fonksiyon
def show_current_rectangle_image_from_listbox():
    selected_rect = rectangles_listbox.curselection()
    if selected_rect:
        rect_text = rectangles_listbox.get(selected_rect[0])
        rect_name, rect_coords = rect_text.split(":")
        
        img = get_screenshot(rect_coords)
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
        rect_name, _ = rect_text.split(":")
        
        # Klasörde kaydedilen resmi bul
        image_path = os.path.join(coordinates_folder, rect_name.strip(), "image.png")
        
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
    json_path = os.path.join(obj_folder, "data.json")
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON kaydedildi: {json_path}")

    return obj_folder


# Point save function
def save_location():
    global last_click_x, last_click_y

    if last_click_x is None or last_click_y is None:
        return

    # Name json
    point_name = name_entry.get() or "Point"
    
    # Koordinatları listeye ekle
    coordinates_listbox.insert(tk.END, f"{point_name}: ({last_click_x}, {last_click_y})")

    # JSON olarak kaydet
    coords = [last_click_x, last_click_y]
    save_to_json(point_name, "Point", coords)


def load_coordinates_from_storage():
    # Dizini kontrol et, varsa listeleri doldur
    if os.path.exists(coordinates_folder):
        for folder_name in os.listdir(coordinates_folder):
            folder_path = os.path.join(coordinates_folder, folder_name)
            json_file_path = os.path.join(folder_path, "data.json")

            if os.path.isdir(folder_path) and os.path.exists(json_file_path):
                # JSON dosyasını aç ve veriyi al
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)

                # Koordinat türüne göre ilgili Listbox'a ekle
                if data['type'] == 'Point':
                    coords = data['coordinates']
                    coordinates_listbox.insert(tk.END, f"{folder_name}: ({coords[0]}, {coords[1]})")
                elif data['type'] == 'Rectangle':
                    coords = data['coordinates']
                    rectangles_listbox.insert(tk.END, f"{folder_name}: ({coords['start'][0]}, {coords['start'][1]}) - ({coords['end'][0]}, {coords['end'][1]})")
    else:
        print(f"Dizin '{coordinates_folder}' mevcut değil.")


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

# Seçim modunu belirleyecek radio butonları (Point / Rectangle)
radio_frame = tk.Frame(right_frame)
radio_frame.pack(pady=10)

radio_point = tk.Radiobutton(radio_frame, text="Point", variable=selection_mode, value=1)
radio_point.pack(side=tk.LEFT)

radio_rectangle = tk.Radiobutton(radio_frame, text="Rectangle", variable=selection_mode, value=2)
radio_rectangle.pack(side=tk.LEFT)

# İsim giriş alanı (Point/Rectangle)
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

# Koordinatları kaydetme butonu (Point)
save_button = tk.Button(button_frame, text="Koordinat Kaydet", command=save_location)
save_button.pack(side=tk.LEFT, padx=5)

# Show coordinat button (For rectangle)
show_coordinat_button = tk.Button(button_frame, text="Koordinat Göster", command=show_current_rectangle_image_from_listbox)
show_coordinat_button.pack(side=tk.LEFT, padx=5)

# Show object button (For rectangle)
show_object_button = tk.Button(button_frame, text="Görüntüyü Göster", command=show_saved_rectangle_image_from_listbox)
show_object_button.pack(side=tk.LEFT, padx=5)

# Koordinat listesi (Point)
coordinates_listbox = tk.Listbox(right_frame)
coordinates_listbox.pack(fill=tk.X, pady=10)

# Rectangle listesi
rectangles_listbox = tk.Listbox(right_frame)
rectangles_listbox.pack(fill=tk.X, pady=10)

# Koordinata tıklama butonu (Point)
run_click_button = tk.Button(right_frame, text="Run Click", command=run_click)
run_click_button.pack(pady=10)

# Sağdaki çerçevenin dinamik olarak genişleyip küçülmesini sağla
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(0, weight=1)

# Seçilen monitör değiştiğinde işleyici
monitor_listbox.bind("<<ListboxSelect>>", on_monitor_select)

# Program başlarken klasörleri tarayıp Listbox'ları doldur
load_coordinates_from_storage()

# Arayüzü başlatalım
root.mainloop()
