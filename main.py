import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import pymem
import os
import sys
import subprocess
import time


class MemoryReader:
    def __init__(self, root, process_name):
        self.root = root
        self.process_name = process_name
        self.base_address = None
        self.auto_update_thread = None
        self.auto_update_flag = threading.Event()
        self.auto_update_interval = tk.DoubleVar(value=6.0)
        self.toggle_state = tk.BooleanVar(value=False)
        self.update_names_flag = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Konfiguration des modernen Dunkelmodus-Themas
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#333")
        self.style.configure("TLabel", background="#333", foreground="white", font=("Helvetica", 12))
        self.style.configure("TCheckbutton", background="#333", foreground="white", font=("Helvetica", 12))
        self.style.configure("Horizontal.TScale", background="#333", foreground="white")
        self.style.configure("TButton", background="#444", foreground="white", font=("Helvetica", 12, "bold"),
                             padding=10)

        # Rollen in Among Us
        self.roles = {
            0: "Crewmate",
            65537: "Impostor",
            131074: "Scientist",
            196611: "Engineer",
            327685: "Shapeshifter",
            327687: "Guardian Angel"
        }

        # Farben und Farbnamen
        self.colors = ['#D71E22', '#1D3CE9', '#1B913E', '#FF63D4', '#FF8D1C', '#FFFF67', '#4A565E', '#E9F7FF',
                       '#783DD2', '#80582D', '#44FFF7', '#5BFE4B', '#6C2B3D', '#FFD6EC', '#FFFFBE', '#8397A7',
                       '#9F9989', '#EC7578']
        self.colornames = ['Red', 'Blue', 'Green', 'Pink', 'Orange', 'Yellow', 'Black', 'White', 'Purple', 'Brown',
                           'Cyan', 'Lime', 'Maroon', 'Rose', 'Banana', 'Grey', 'Tan', 'Coral']
        self.output_text = tk.Text(root, height=15, width=50, bg='#222', fg='white', insertbackground='white',
                                   highlightbackground='#444', highlightcolor='#444', font=("Consolas", 11))
        self.output_text.pack(padx=10, pady=10)
        for color_hex, color_tag in zip(self.colors, self.colornames):
            self.output_text.tag_configure(color_tag, foreground=color_hex)

        self.output_text.tag_configure('gray', foreground='gray')
        self.output_text.tag_configure('imp', foreground='red')
        self.footer_label = ttk.Label(root,
                                      text="0: Close   ||   1: Read Players   ||   9: PANIC! (delete) || credits: hskys")
        self.output_text.insert(tk.END,
                                "* Start Among Us\n* Start a game\n* Press 1 to know who the Impostors are!\n* Press 9 to PANIC (delete this cheat)")
        self.footer_label.pack(side='bottom', fill='x', pady=5)

        # Rahmen für Buttons und Checkbox
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=10)

        # Checkbox zum Ein-/Ausschalten der automatischen Überprüfung
        self.auto_check_var = tk.BooleanVar()
        self.auto_check = ttk.Checkbutton(self.control_frame, text="Auto Check Who is Imposter",
                                          variable=self.auto_check_var, command=self.toggle_auto_check,
                                          style="TCheckbutton")
        self.auto_check.pack(side=tk.LEFT, padx=10, pady=10)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # Funktion zur Bestimmung der Basisadresse
    def find_base_address(self):
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base_address = module.lpBaseOfDll
        add_offset = pm.read_uint(module_base_address + 0x022F4F10)
        add_offset = pm.read_uint(add_offset + 0x5C)
        self.base_address = pm.read_uint(add_offset)
        pm.close_process()

    # Funktion zur Identifizierung der Impostors
    def find_impostors(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_uint(self.base_address + 0x60)
            items_ptr = pm.read_uint(allclients_ptr + 0x8)
            items_count = pm.read_uint(allclients_ptr + 0xC)
            for i in range(items_count):
                item_base = pm.read_uint(items_ptr + 0x10 + (i * 4))

                item_char_ptr = pm.read_uint(item_base + 0x10)
                item_data_ptr = pm.read_uint(item_char_ptr + 0x54)
                item_role = pm.read_uint(item_data_ptr + 0x14)
                role_name = self.roles.get(item_role, "Dead")

                item_color_id = pm.read_uint(item_base + 0x28)

                coordinates = (0, 0, item_color_id)  # Koordinaten sind nicht mehr benötigt
                item_name_ptr = pm.read_uint(item_base + 0x1C)
                item_name_length = pm.read_uint(item_name_ptr + 0x8)
                item_name_address = item_name_ptr + 0xC
                raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)
                item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')

                player_details = f"{item_name:10} | {self.colornames[item_color_id]:7} | "
                players.append((player_details, role_name, coordinates))
            pm.close_process()
            return players
        except pymem.exception.PymemError as e:
            pm.close_process()
            return players

    # Funktion zum Lesen des Speichers
    def read_memory(self):
        self.find_base_address()
        players = self.find_impostors()

        if self.update_names_flag:
            self.output_text.delete('1.0', tk.END)  # Bestehenden Text löschen
            for player_details, role_name, (playerx, playery, playercolor) in players:
                if role_name in ["Shapeshifter", "Impostor"]:
                    self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                    self.output_text.insert(tk.END, f"{role_name}\n", 'imp')
                elif role_name in ["Dead", "Guardian Angel"]:
                    self.output_text.insert(tk.END, f"{player_details} {role_name}\n", 'gray')
                else:
                    self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                    self.output_text.insert(tk.END, f"{role_name}\n")
            self.update_names_flag = False

    # Funktion zum Aktualisieren der Namen
    def update_names(self):
        self.update_names_flag = True
        self.read_memory()

    # Funktion zum Ein-/Ausschalten der automatischen Überprüfung
    def toggle_auto_check(self):
        if self.auto_check_var.get():
            self.auto_update_flag.set()
            self.auto_update_thread = threading.Thread(target=self.auto_update_names)
            self.auto_update_thread.start()
        else:
            self.auto_update_flag.clear()

    # Funktion zur automatischen Aktualisierung der Namen
    def auto_update_names(self):
        while self.auto_update_flag.is_set():
            start_time = time.time()  # Startzeit erfassen

            self.update_names()

            elapsed_time = time.time() - start_time  # Vergangene Zeit seit dem Start erfassen
            if elapsed_time < self.auto_update_interval.get():
                time.sleep(self.auto_update_interval.get() - elapsed_time)

    # Funktion zum Schließen des Fensters
    def on_close(self):
        self.disable_auto_update()
        self.root.destroy()

    # Funktion zum Deaktivieren der automatischen Aktualisierung
    def disable_auto_update(self):
        self.auto_update_flag.clear()
        if self.auto_update_thread is not None:
            self.auto_update_thread.join()


def update(memory_reader):
    threading.Thread(target=memory_reader.read_memory).start()


def on_close(root, memory_reader):
    memory_reader.disable_auto_update()
    root.destroy()


def self_delete():
    executable_name = os.path.basename(sys.executable)
    command = f"cmd /c ping localhost -n 3 > nul & del {executable_name}"
    subprocess.Popen(command, shell=True)
    root.destroy()


root = tk.Tk()
root.title("Among Us Memory Reader v0.1")
root.configure(bg='#333')
root.geometry("500x500")

memory_reader = MemoryReader(root, "Among Us.exe")

# Hotkeys hinzufügen
keyboard.add_hotkey('1', lambda: memory_reader.update_names())
keyboard.add_hotkey('0', lambda: on_close(root, memory_reader))
keyboard.add_hotkey('9', lambda: self_delete())

root.mainloop()
