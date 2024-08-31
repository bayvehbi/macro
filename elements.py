import tkinter as tk

class name_entry:
    name_input = None

    def __init__(self, location):
        name_entry.name_input = tk.Entry(location)

class listdrawer:
    active_instance = None
    instances = []
    def __init__(self, location, type):
        self.listbox = tk.Listbox(location)
        self.listbox.bind("<Button-1>", self.set_active)
        self.__class__.instances.append(self)
        self.type = type
        if type == 1:
            self.name = 'Point'
        elif type == 2:
            self.name = 'Rectangle'


    def list_update(self, name):
        active_coords = DrawMode.find_instances_by_mode(DrawMode.active_mode.get())
        items = self.listbox.get(0, tk.END)
        r_index = tk.END
        # Elemanlar içinde kelimeyi arayarak indeksini bul
        for index, item in enumerate(items):
            if name.lower() in item.lower():  # Kelimeyi küçük harf duyarlı olarak karşılaştır
                self.listbox.delete(index)
                r_index = index
            
        if name:
            # Koordinat ismini güncelle
            print(r_index)
            print(f"{name}: {active_coords.coordinates}")
            self.listbox.insert(r_index, f"{name}: {active_coords.coordinates}")

    def set_active(self, event):
        listdrawer.active_instance = self
        print(f"Active instance set to: {self}")

    @classmethod
    def get_active_instance(cls):
        print(cls.active_instance)
        return cls.active_instance
    
    @classmethod
    def get_instance(cls, m_type):
        # 'Point' tipinde olan tüm örnekleri bul ve liste olarak döndür
        matching_instances = [instance for instance in cls.instances if instance.type == m_type]
        return matching_instances[0] if len(matching_instances) == 1 else matching_instances

    
    
class m_button:
    def __init__(self, location, text):
        self.button = tk.Button(location, text=text)
        self.button.config(state=tk.DISABLED)
        pass

    def function_mode(self, function):
        self.button.config(state=function)


class DrawMode:
    instances = []
    global active_mode
    def __init__(self, m_type):
        # Yeni oluşturulan örneği instances listesine ekliyoruz
        self.__class__.instances.append(self)

        # selection_mode bir IntVar olarak ayarlanıyor
        DrawMode.active_mode = tk.IntVar(value=1)
        
        if m_type == 'Point':
            self.selection_mode = 1
            self.has_data = False
            self.coordinates = []
            self.type = 'Point'
        elif m_type == 'Rectangle':
            self.selection_mode = 2
            self.has_data = False
            self.coordinates = {"start": [], "end": []}
            self.type = 'Rectangle'

    def update_coordinates(self, coordinates):
        self.coordinates = coordinates
        self.has_data = True

    @classmethod
    def find_instances_by_mode(cls, m_type):
        # Seçim moduna göre tüm örnekleri bul ve liste olarak döndür
        matching_instances = [instance for instance in cls.instances if instance.selection_mode == m_type]
        return matching_instances[0] if len(matching_instances) == 1 else matching_instances