import pandas as pd
import os
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def browse_excel_file():
    excel_path.set(filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")]))  # Otvara dijalog za izbor fajla

def browse_photos_from():
    photos_from.set(filedialog.askdirectory())  # Otvara dijalog za izbor foldera

def browse_photos_to():
    photos_to.set(filedialog.askdirectory())  # Otvara dijalog za izbor foldera

def start_processing():
    try:
        excel = excel_path.get()
        photos_from_folder = photos_from.get()
        photos_to_folder = photos_to.get()

        if not excel or not photos_from_folder or not photos_to_folder:
            messagebox.showerror("Greška", "Morate uneti sve putanje!")
            return

        file = pd.read_excel(excel, engine='openpyxl')
        folders = file.columns[3:]

        # Kreiranje foldera u 'photosto' putanji
        for folder in folders:
            path = os.path.join(photos_to_folder, folder)
            os.makedirs(path, exist_ok=True)

        # Procesiranje svakog reda u Excel fajlu
        for _, row in file.iterrows():
            image_number = str(int(row.iloc[2]))  # Pretvaramo u int pa u string
            image_pattern = os.path.join(photos_from_folder, f"{image_number}*.JPG")
            matching_images = glob.glob(image_pattern)

            if matching_images:
                image_path = matching_images[0]
                for i, folder in enumerate(folders, start=3):
                    copies = row.iloc[i]
                    if pd.notna(copies):
                        copies = int(copies)
                        for j in range(copies):
                            dest_folder = os.path.join(photos_to_folder, folder)
                            base_name = os.path.basename(image_path)
                            name, ext = os.path.splitext(base_name)
                            new_name = f"{name}_{j + 1}{ext}"
                            dest_image = os.path.join(dest_folder, new_name)
                            shutil.copy(image_path, dest_image)

            else:
                messagebox.showwarning("Upozorenje", f"Slika {image_number} nije pronađena!")

        # Poruka o uspešnom završetku
        messagebox.showinfo("Završeno", "Kopiranje je uspešno izvršeno!")

        # Isprazniti polja
        excel_path.set("")
        photos_from.set("")
        photos_to.set("")

    except Exception as e:
        messagebox.showerror("Greška", f"Došlo je do greške: {e}")

# Kreiranje GUI-ja
root = tk.Tk()
root.title("Razvrstavanje slika")

# Varijable za putanje
excel_path = tk.StringVar()
photos_from = tk.StringVar()
photos_to = tk.StringVar()

# UI komponente
tk.Label(root, text="Excel fajl:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=excel_path, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Izaberi", command=browse_excel_file).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Putanja do foldera sa slikama:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=photos_from, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Izaberi", command=browse_photos_from).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Putanja do foldera za kopiranje slika:").grid(row=2, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=photos_to, width=50).grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Izaberi", command=browse_photos_to).grid(row=2, column=2, padx=10, pady=5)

tk.Button(root, text="Pokreni proces", command=start_processing).grid(row=3, column=0, columnspan=3, pady=20)

# Pokretanje GUI-ja
root.mainloop()
