import tkinter as tk
from tkinter import Frame, messagebox
from tkinter.filedialog import asksaveasfile

from PIL import Image, ImageTk
from pathlib import Path
import string
import secrets
import json
from tkinter import ttk

root = tk.Tk()
root.geometry("650x600")
root.maxsize(width=650, height=600)
root.minsize(width=650, height=600)
root.title("Password Manager")

website_var = tk.StringVar()
username_var = tk.StringVar()
password_var = tk.StringVar()

field_bg = "#f7f7f7"
button_bg = "#f0f0f0"
button_bg = "#f4f4f4"
button_fg = "black"
highlightbackground="white"

# ------------------- PASSWORD GENERATOR ------------------- #

def generate_password():
    gen_pass_length = 16
    chars = string.ascii_letters + string.digits + string.punctuation
    pw = ''.join(secrets.choice(chars) for _ in range(gen_pass_length))

    password_entry.delete(0, tk.END)  # önce temizle
    password_entry.insert(0, pw)  # sonra yaz
    add_button.config(state=tk.NORMAL)  # Add aktif olsun

# ------------------- COPY CLIPBOARD PASSWORD GENERATOR ------------------- #
def copy_password_to_clipboard(pw: str):
    root.clipboard_clear()
    root.clipboard_append(pw)
    messagebox.showinfo("Copied", "Password copied to clipboard.")

# ------------------- CHECK EMTPY FIELDS ------------------- #
def is_empty(_username, _website, _password):
    return len(_username) == 0 or len(_website) == 0 or len(_password) == 0

# ------------------- CLEAR FIELDS ------------------- #
def clear_fields():
    website_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    add_button.config(state=tk.DISABLED)

# ------------------- SAVE PASSWORD ------------------- #
def save_password():
    password_store_file = "passwords.txt"

    # StringVar'ları ezme: ayrı isimlere al
    username = username_entry.get().strip()
    website = website_entry.get().strip()
    password = password_entry.get().strip()
    is_empty(username, website, password)
    if is_empty(username, website, password):
        messagebox.showerror("Error", "Please enter a correct username, password, and website.")
        return

    # lines = [f"username: {username} | ", f"website: {website} | ", f"password: {password}"]
    if not messagebox.askyesno(title="Save New Password",
                               message="Do you want to save the new password?"):
        messagebox.showinfo(title="Warning", message="No saved password")
        return

        # 2 seçenekten birini kullan:

        # (A) Kullanıcıdan dosya seçtirmek (asksaveasfile'ı DOĞRU kullan)
    # f = asksaveasfile(mode="a",  # append
    #                   initialfile="passwords.txt",
    #                   defaultextension=".txt",
    #                   title="Save Password",
    #                   filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")],
    #                   confirmoverwrite=False)

    f = asksaveasfile(mode="a",  # append
                      initialfile="passwords.json",
                      defaultextension=".json",
                      title="Save Password",
                      filetypes=[("JSON Documents", "*.json"), ("All Files", "*.*")],
                      confirmoverwrite=False)

    if f is None:
        return  # dialog iptal edildi

    # try:
    #     f.write(', '.join(lines) + "\n")  # satır sonu ekle
    #     f.close()
    #     messagebox.showinfo("Password Saved", "Password has been successfully saved.")
    #     clear_fields()
    # except Exception as e:
    #     try:
    #         f.close()
    #     except Exception:
    #         pass
    #     messagebox.showerror("Error", str(e))

    # (B) Diyalog istemezsen sabit dosyaya ekle:
    # with open("passwords.txt", "a", encoding="utf-8") as wf:
    #     wf.write(', '.join(lines) + "\n")
    # messagebox.showinfo("Password Saved", "Password has been successfully saved.")
    # clear_fields()

    # VAR OLANI YÜKLE (yoksa boş dict)
    path = "passwords.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        # dosya bozulmuşsa sıfırla
        data = {}

    # Yapı: { "website.com": {"email": "...", "password": "..."} }
    data[website] = {"email": username, "password": password}

    # OVERWRITE ile yaz (JSON'da append yapılmaz!)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Write error: {e}")
        return

    messagebox.showinfo("Password Saved", "Password has been successfully saved.")
    clear_fields()



# ------------------- SEARCH PASSWORD ------------------- #
def search_password():
    website = website_entry.get().strip()
    if not website:
        messagebox.showerror("Error", "Please enter a correct website.")
        return
    try:
        with open("passwords.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, dict):
                messagebox.showerror("Error", "Password store is corrupted.")
                return
    except FileNotFoundError:
        messagebox.showerror("Error", "No passwords.json file found yet.")
        return
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Password file is not valid JSON.")
        return

    creds = data.get(website)
    if not creds:
        messagebox.showinfo("Not Found", f"No saved credentials for:\n{website}")
        return

    # alanları doldur
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    username_entry.insert(0, creds.get("email", ""))
    password_entry.insert(0, creds.get("password", ""))

    # istersen burada Add'ı aktif bırak (güncellemek için)
    add_button.config(state=tk.NORMAL)

    # sonuçları listbox'a yaz
    result_listbox.insert(0, creds.get("website", ""))
    result_listbox.insert(0, creds.get("email", ""))
    result_listbox.insert(0, creds.get("password", ""))

# Read from .txt file:
#     # with open("passwords.txt", "r") as file:
#     #     lines = file.readlines()
#     #     for row in lines:
#     #         if row.find(website_var.get()) > 0:
#     #             result_listbox.insert(tk.END, row)




# ------------------- UI SETUP ------------------- #

canvas = tk.Canvas(root, width=300, height=300, bg="white")
canvas.pack(pady=20)

#Load the padlock image
PADLOCK_IMG = Path(__file__).parent / "padlock.png"
padlock_image = Image.open(PADLOCK_IMG)
padlock_image = padlock_image.resize((300,300))
padlock_image = ImageTk.PhotoImage(padlock_image)

#Load image to Canvas
canvas.create_image(150, 0, anchor=tk.N, image=padlock_image)
canvas.img = padlock_image

#Controls Frame
controls_frame = Frame(root)
controls_frame.pack(side="top", fill="both", anchor="center", expand=True)
# weight=1 ise bu demek oluyor ki o kolon esneyebilsin. o kolondan ve sağdan ne kadar boşluk varsa eşit esnesin
# 0 olursa sabit kalsın, esnemesin.
# biz hayali 3 kolon var gibi düşünüyoruz.
# 0 ve 2 numaralı kolonlar esneyebilecek. 1 numaralı kolonda da bizim kontrollerimiz olacak.
# Sadece ortadaki kolonumuz sabit kalacak. O yüzden weight=0 olacak
controls_frame.grid_columnconfigure(0, weight=1) # sol boşluk (esner)
controls_frame.grid_columnconfigure(1, weight=1) # sol boşluk (esner)
controls_frame.grid_columnconfigure(2, weight=0) # Label
controls_frame.grid_columnconfigure(3, weight=0) # Entry
controls_frame.grid_columnconfigure(4, weight=0) # Generate button
controls_frame.grid_columnconfigure(5, weight=1) # sağ boşluk (esner)
controls_frame.grid_columnconfigure(6, weight=1) # sağ boşluk (esner)

#Website
website_label = tk.Label(controls_frame, text="Website:")
website_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)
website_entry = tk.Entry(controls_frame, textvariable=website_var, width=35, bg=field_bg, bd=1,
    highlightthickness=0,
    relief="solid")
website_entry.insert(0, "www.example.com")
website_entry.grid(row=0, column=3)
website_entry.focus()

#Username
username_label = tk.Label(controls_frame, text="Email/Username:")
username_label.grid(row=1, column=2, sticky="e", padx=5, pady=5)
username_entry = tk.Entry(controls_frame, textvariable=username_var, width=35, bg=field_bg, bd=1,
    highlightthickness=0,
    relief="solid")
username_entry.insert(0, "name@example.com")
username_entry.grid(row=1, column=3)

#Password
password_label = tk.Label(controls_frame, text="Password:")
password_label.grid(row=2, column=2, sticky="e", padx=5, pady=5)
password_entry = tk.Entry(controls_frame, textvariable=password_var, width=35, bg=field_bg, bd=1,
    highlightthickness=0,
    relief="solid")
password_entry.grid(row=2, column=3)

#Generate button
generate_button = ttk.Button(controls_frame,
    text="Generate Password",
    command=generate_password,
    width=15)
generate_button.grid(row=1, column=4, sticky="W", padx=5, pady=5)

#Add button
add_button = ttk.Button(controls_frame, text="Add Password", command=save_password, width= 15, state="disabled")
add_button.grid(row=2, column=4, sticky="W", padx=5, pady=5)

#Search button
search_button = ttk.Button(controls_frame,
    text="Search Password",
    command=search_password,
    width=15)
search_button.grid(row=0, column=4, sticky="NE", padx=5, pady=5)

# Search result in Listbox
result_label = tk.Label(controls_frame, text="Search Result:")
result_label.grid(row=4, column=2, sticky="e", padx=5, pady=5)
result_listbox = tk.Listbox(controls_frame, bg=field_bg, height=7, width=35, bd=1,
    highlightthickness=0,
    relief="solid")
result_listbox.grid(row=4, column=3, padx=5, pady=5)



root.mainloop()
