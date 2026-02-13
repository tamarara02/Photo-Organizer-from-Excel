import pandas as pd
import os
import glob
import shutil
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# ----- Custom messagebox sa istim fontom -----
def custom_message(title, message, kind="info"):
    win = tk.Toplevel(root)
    win.withdraw()
    win.title(title)
    win.resizable(False, False)
    win.configure(bg="#f4f6fb")

    # Ikonica prema tipu poruke
    if kind == "error":
        win.iconbitmap("error.ico")
    elif kind == "warning":
        win.iconbitmap("warning.ico")
    else:
        win.iconbitmap("info.ico")

    tk.Label(win, text=message, font=("Segoe UI Semibold", 10),
             bg="#f4f6fb", fg="#1f2937", wraplength=350, justify="left").pack(padx=20, pady=20)

    # OK dugme (uvek ista boja)
    tk.Button(win, text="OK", font=("Segoe UI", 10),
              bg="#d1d5db", fg="#1f2937", relief="flat",
              command=win.destroy).pack(pady=(0, 20))

    win.update_idletasks()
    # Centriranje
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()

    win_w = win.winfo_width()
    win_h = win.winfo_height()

    pos_x = root_x + (root_w - win_w) // 2
    pos_y = root_y + (root_h - win_h) // 2

    win.geometry(f"+{pos_x}+{pos_y}")
    win.deiconify()  # Pokaži prozor tek nakon što je centriran
    win.grab_set()  # blokira interakciju sa glavnim prozorom dok se ne zatvori
    win.transient(root)
    win.wait_window()

def browse_excel_file():
    excel_path.set(filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")]))

def browse_photos_from():
    photos_from.set(filedialog.askdirectory())

def browse_photos_to():
    photos_to.set(filedialog.askdirectory())

def merge_duplicate_images(df):
    df = df.copy()
    sum_cols = df.columns[3:9]
    for col in sum_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    merged_rows = []
    for image_number, group in df.groupby(df.columns[2]):
        first_row = group.iloc[0].copy()
        first_row[sum_cols] = group[sum_cols].sum()
        merged_rows.append(first_row)
    return pd.DataFrame(merged_rows)

def show_message_from_thread(title, message, kind="info"):
    # Schedule poruku da se prikaže u glavnoj niti
    root.after(0, lambda: custom_message(title, message, kind))

def start_processing():
    try:
        excel = excel_path.get()
        photos_from_folder = photos_from.get()
        photos_to_folder = photos_to.get()

        if not excel or not photos_from_folder or not photos_to_folder:
            progress.stop()
            progress.grid_forget()
            custom_message("Greška", "Morate uneti sve putanje!", "error")
            return

        file = pd.read_excel(excel, engine='openpyxl', dtype=str)
        file = merge_duplicate_images(file)
        folders = file.columns[3:]

        for folder in folders:
            path = os.path.join(photos_to_folder, folder)
            os.makedirs(path, exist_ok=True)

        for _, row in file.iterrows():
            raw_value = row.iloc[2]
            if pd.isna(raw_value) or str(raw_value).strip().lower() == "nan":
                continue
            image_number = str(row.iloc[2]).strip().zfill(4)
            image_pattern = os.path.join(photos_from_folder, f"{image_number}*.JPG")
            matching_images = glob.glob(image_pattern)

            if matching_images:
                image_path = matching_images[0]
                for i, folder in enumerate(folders, start=3):
                    copies = row.iloc[i]
                    if pd.notna(copies) and str(copies).strip() != "":
                        copies = int(float(copies))
                        for j in range(copies):
                            dest_folder = os.path.join(photos_to_folder, folder)
                            base_name = os.path.basename(image_path)
                            name, ext = os.path.splitext(base_name)
                            new_name = f"{name}_{j + 1}{ext}"
                            dest_image = os.path.join(dest_folder, new_name)
                            shutil.copy(image_path, dest_image)
            else:
                custom_message("Upozorenje", f"Slika {image_number} nije pronađena!", "warning")

        progress.stop()
        progress.grid_forget()
        show_message_from_thread("Završeno", "Kopiranje je uspešno izvršeno!", "info")
        excel_path.set("")
        photos_from.set("")
        photos_to.set("")
    except Exception as e:
        custom_message("Greška", f"Došlo je do greške: {e}", "error")
    finally:
        # Ponovo aktiviraj sve dugmadi
        for b in all_buttons:
            b.configure(state="normal")

# ----- Threading + progress -----
def start_processing_thread():
    for b in all_buttons:
        b.configure(state="disabled")  # deaktiviraj sve dugmadi
    progress.grid(row=5, column=0, columnspan=3, pady=(0,10))
    progress.start(10)
    t = threading.Thread(target=start_processing)
    t.start()

# ----- GUI -----
root = tk.Tk()
root.iconbitmap("ikonica.ico")
root.title("Razvrstavanje slika")
root.geometry("720x450")
root.configure(bg="#eef7f1")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#f4f6fb", font=("Segoe UI Semibold", 10))
style.configure("TEntry", padding=5, relief="flat", font=("Segoe UI", 10))
style.configure("Modern.TButton",
                font=("Segoe UI", 10, "bold"),
                padding=8,
                borderwidth=0,
                background="#d1d5db",
                foreground="#1f2937")
style.map("Modern.TButton",
          background=[("active", "#9ca3af")],
          foreground=[("active", "#1f2937")],
          focuscolor=[("pressed", "none"), ("active", "none")])

container = tk.Frame(root, bg="#f4f6fb", padx=40, pady=30)
container.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(container,
          text="Razvrstavanje i kopiranje slika",
          font=("Segoe UI Semibold", 14),
          background="#f4f6fb",
          foreground="#1f2937").grid(row=0, column=0, columnspan=3, pady=(0, 20))

excel_path = tk.StringVar()
photos_from = tk.StringVar()
photos_to = tk.StringVar()

# Dugmad i entry polja
ttk.Label(container, text="Excel fajl:").grid(row=1, column=0, sticky="e", pady=10, padx=(0,10))
ttk.Entry(container, textvariable=excel_path, width=45).grid(row=1, column=1, padx=15)
btn1 = ttk.Button(container, text="Izaberi", style="Modern.TButton", command=browse_excel_file)
btn1.grid(row=1, column=2)

ttk.Label(container, text="Folder sa slikama:").grid(row=2, column=0, sticky="e", pady=10, padx=(0,10))
ttk.Entry(container, textvariable=photos_from, width=45).grid(row=2, column=1, padx=15)
btn2 = ttk.Button(container, text="Izaberi", style="Modern.TButton", command=browse_photos_from)
btn2.grid(row=2, column=2)

ttk.Label(container, text="Folder za kopiranje:").grid(row=3, column=0, sticky="e", pady=10, padx=(0,10))
ttk.Entry(container, textvariable=photos_to, width=45).grid(row=3, column=1, padx=15)
btn3 = ttk.Button(container, text="Izaberi", style="Modern.TButton", command=browse_photos_to)
btn3.grid(row=3, column=2)

start_btn = ttk.Button(container,
                       text="POKRENI PROCES",
                       style="Modern.TButton",
                       command=start_processing_thread)
start_btn.grid(row=4, column=0, columnspan=3, pady=20)

progress = ttk.Progressbar(container, mode="indeterminate", length=450)

all_buttons = [btn1, btn2, btn3, start_btn]
for b in all_buttons:
    b.configure(takefocus=False)

root.mainloop()
