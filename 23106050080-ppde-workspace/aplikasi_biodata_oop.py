import tkinter as tk
from tkinter import messagebox
import datetime
import logging
import os

# Setup logging
logging.basicConfig(
    filename='aplikasi_biodata.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class AplikasiBiodata(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x750")
        self.resizable(True, True)

        # Database user sederhana
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456"
        }

        # Status login
        self.current_user = None
        self.show_password = False

        # Frame aktif
        self.frame_aktif = None

        # Buat tampilan
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        # Tampilkan frame login pertama kali
        self._pindah_ke(self.frame_login)

        logging.info("Aplikasi dimulai")

    # -------------------------
    # Manajemen Frame
    # -------------------------
    def _pindah_ke(self, frame_tujuan):
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()

        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

        if frame_tujuan == self.frame_login:
            self.after(100, lambda: self.entry_username.focus_set())
            self._hapus_menu()
        elif frame_tujuan == self.frame_biodata:
            self.after(100, lambda: self.entry_nama.focus_set())
            self._buat_menu()

    # -------------------------
    # Tampilan Login
    # -------------------------
    def _buat_tampilan_login(self):
        self.frame_login = tk.Frame(self, padx=20, pady=100)
        self.frame_login.grid_columnconfigure(0, weight=1)
        self.frame_login.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # Username
        tk.Label(self.frame_login, text="Username:", font=("Arial", 12)).grid(row=1, column=0, sticky="W", pady=5)
        self.entry_username = tk.Entry(self.frame_login, font=("Arial", 12))
        self.entry_username.grid(row=1, column=1, pady=5, sticky="EW")

        # Password + show/hide
        tk.Label(self.frame_login, text="Password:", font=("Arial", 12)).grid(row=2, column=0, sticky="W", pady=5)
        frame_pass = tk.Frame(self.frame_login)
        frame_pass.grid(row=2, column=1, sticky="ew")
        frame_pass.grid_columnconfigure(0, weight=1)
        self.entry_password = tk.Entry(frame_pass, font=("Arial", 12), show="*")
        self.entry_password.grid(row=0, column=0, sticky="ew")
        self.btn_toggle_pass = tk.Button(frame_pass, text="Show", command=self._toggle_password)
        self.btn_toggle_pass.grid(row=0, column=1, padx=5)

        # Remember me
        self.var_remember = tk.IntVar()
        self.chk_remember = tk.Checkbutton(self.frame_login, text="Remember Me", variable=self.var_remember)
        self.chk_remember.grid(row=3, column=0, columnspan=2, sticky="w")

        # Tombol login
        self.btn_login = tk.Button(
            self.frame_login,
            text="Login",
            font=("Arial", 12, "bold"),
            command=self._coba_login
        )
        self.btn_login.grid(row=4, column=0, columnspan=2, pady=20, sticky="EW")

        # Shortcuts
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self._coba_login())

        # Info akun
        tk.Label(
            self.frame_login,
            text="Info Akun:\nadmin (123)\nuser1 (password1)\nmahasiswa (123456)",
            font=("Arial", 9),
            fg="gray",
            justify="left"
        ).grid(row=5, column=0, columnspan=2, pady=10)

        # Load remembered username
        self._load_remembered_username()

    def _toggle_password(self):
        if self.show_password:
            self.entry_password.config(show="*")
            self.btn_toggle_pass.config(text="Show")
        else:
            self.entry_password.config(show="")
            self.btn_toggle_pass.config(text="Hide")
        self.show_password = not self.show_password

    def _save_remembered_username(self, username):
        if self.var_remember.get() == 1:
            with open("remember_me.txt", "w") as f:
                f.write(username)
        else:
            if os.path.exists("remember_me.txt"):
                os.remove("remember_me.txt")

    def _load_remembered_username(self):
        if os.path.exists("remember_me.txt"):
            with open("remember_me.txt", "r") as f:
                remembered = f.read().strip()
                if remembered:
                    self.entry_username.insert(0, remembered)
                    self.var_remember.set(1)

    def _coba_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        logging.info(f"Login attempt for username: {username}")

        if not username or not password:
            logging.warning(f"Empty credentials attempt: {username}")
            messagebox.showwarning("Login Gagal", "Username dan Password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        if len(username) < 3:
            logging.warning(f"Username too short: {username}")
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username
            logging.info(f"Successful login: {username}")
            messagebox.showinfo("Login Berhasil", f"Selamat Datang, {username}!")
            self._reset_form_biodata()
            self._update_title_with_user()
            self._pindah_ke(self.frame_biodata)
            self._save_remembered_username(username)
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
        else:
            logging.warning(f"Failed login attempt: {username}")
            messagebox.showerror("Login Gagal", "Username atau Password salah.")
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    # -------------------------
    # Tampilan Biodata
    # -------------------------
    def _buat_tampilan_biodata(self):
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_jurusan.trace_add("write", self.validate_form)

        self.frame_biodata = tk.Frame(self, padx=20, pady=20)
        self.frame_biodata.columnconfigure(1, weight=1)

        tk.Label(
            self.frame_biodata,
            text="FORM BIODATA MAHASISWA",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # Input nama
        tk.Label(self.frame_biodata, text="Nama Lengkap:", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
        self.entry_nama = tk.Entry(self.frame_biodata, textvariable=self.var_nama, font=("Arial", 12))
        self.entry_nama.grid(row=1, column=1, pady=5, sticky="ew")

        # Input NIM
        tk.Label(self.frame_biodata, text="NIM:", font=("Arial", 12)).grid(row=2, column=0, sticky="w")
        self.entry_nim = tk.Entry(self.frame_biodata, textvariable=self.var_nim, font=("Arial", 12))
        self.entry_nim.grid(row=2, column=1, pady=5, sticky="ew")

        # Input jurusan
        tk.Label(self.frame_biodata, text="Jurusan:", font=("Arial", 12)).grid(row=3, column=0, sticky="w")
        self.entry_jurusan = tk.Entry(self.frame_biodata, textvariable=self.var_jurusan, font=("Arial", 12))
        self.entry_jurusan.grid(row=3, column=1, pady=5, sticky="ew")

        # Input alamat
        tk.Label(self.frame_biodata, text="Alamat:", font=("Arial", 12)).grid(row=4, column=0, sticky="nw")
        self.text_alamat = tk.Text(self.frame_biodata, height=5, width=30, font=("Arial", 12))
        self.text_alamat.grid(row=4, column=1, pady=5, sticky="ew")

        # Tambahan: Email
        tk.Label(self.frame_biodata, text="Email:", font=("Arial", 12)).grid(row=5, column=0, sticky="w")
        self.entry_email = tk.Entry(self.frame_biodata, font=("Arial", 12))
        self.entry_email.grid(row=5, column=1, pady=5, sticky="ew")

        # Tambahan: Telepon
        tk.Label(self.frame_biodata, text="Telepon:", font=("Arial", 12)).grid(row=6, column=0, sticky="w")
        self.entry_telepon = tk.Entry(self.frame_biodata, font=("Arial", 12))
        self.entry_telepon.grid(row=6, column=1, pady=5, sticky="ew")

        # Tambahan: Tanggal Lahir
        tk.Label(self.frame_biodata, text="Tanggal Lahir (DD-MM-YYYY):", font=("Arial", 12)).grid(row=7, column=0, sticky="w")
        self.entry_tanggal = tk.Entry(self.frame_biodata, font=("Arial", 12))
        self.entry_tanggal.grid(row=7, column=1, pady=5, sticky="ew")

        # Jenis kelamin
        tk.Label(self.frame_biodata, text="Jenis Kelamin:", font=("Arial", 12)).grid(row=8, column=0, sticky="w")
        frame_jk = tk.Frame(self.frame_biodata)
        frame_jk.grid(row=8, column=1, sticky="w")
        tk.Radiobutton(frame_jk, text="Pria", variable=self.var_jk, value="Pria").pack(side=tk.LEFT)
        tk.Radiobutton(frame_jk, text="Wanita", variable=self.var_jk, value="Wanita").pack(side=tk.LEFT)

        # Checkbox persetujuan
        self.checkbox_setuju = tk.Checkbutton(
            self.frame_biodata,
            text="Saya menyetujui pengumpulan data",
            variable=self.var_setuju,
            command=self.validate_form
        )
        self.checkbox_setuju.grid(row=9, column=0, columnspan=2, pady=10)

        # Tombol Submit & Reset
        self.btn_reset = tk.Button(
            self.frame_biodata,
            text="Reset Form",
            command=self._reset_form_biodata,
            bg="lightgray"
        )
        self.btn_reset.grid(row=10, column=0, pady=15, padx=(30, 15), sticky="ew")

        self.btn_submit = tk.Button(
            self.frame_biodata,
            text="Submit",
            command=self.submit_data,
            state=tk.DISABLED,
            bg="lightgreen"
        )
        self.btn_submit.grid(row=10, column=1, pady=15, padx=(15, 30), sticky="ew")
        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)

        # Label hasil
        self.label_hasil = tk.Label(self.frame_biodata, text="", font=("Arial", 12), justify="left")
        self.label_hasil.grid(row=11, column=0, columnspan=2, pady=10, sticky="w")

    # -------------------------
    # Method Biodata
    # -------------------------
    def submit_data(self):
        try:
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Peringatan", "Anda harus menyetujui pengumpulan data!")
                return

            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            jurusan = self.entry_jurusan.get().strip()
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            email = self.entry_email.get().strip()
            telepon = self.entry_telepon.get().strip()
            tanggal_lahir = self.entry_tanggal.get().strip()
            jenis_kelamin = self.var_jk.get()

            # Validasi wajib isi
            if not nama or not nim or not jurusan:
                messagebox.showwarning("Input Kosong", "Nama, NIM, dan Jurusan harus diisi!")
                return

            # Validasi NIM
            if not nim.isdigit() or len(nim) < 8:
                messagebox.showwarning("Format NIM Salah", "NIM harus berupa angka minimal 8 digit!")
                self.entry_nim.focus_set()
                return

            # Validasi Nama
            if nama.isdigit():
                messagebox.showwarning("Format Nama Salah", "Nama tidak boleh hanya angka!")
                self.entry_nama.focus_set()
                return

            # Validasi Email
            if "@" not in email or "." not in email.split("@")[-1]:
                messagebox.showwarning("Format Email Salah", "Masukkan email yang valid!")
                self.entry_email.focus_set()
                return

            # Validasi Telepon Indonesia
            if not telepon.isdigit() or not telepon.startswith("08") or not (10 <= len(telepon) <= 13):
                messagebox.showwarning("Format Telepon Salah", "Nomor telepon harus diawali 08 dan panjang 10-13 digit.")
                self.entry_telepon.focus_set()
                return

            # Validasi Tanggal Lahir
            try:
                datetime.datetime.strptime(tanggal_lahir, "%d-%m-%Y")
            except ValueError:
                messagebox.showwarning("Format Tanggal Salah", "Tanggal lahir harus dalam format DD-MM-YYYY.")
                self.entry_tanggal.focus_set()
                return

            # Jika validasi lolos
            hasil = (
                f"Nama: {nama}\nNIM: {nim}\nJurusan: {jurusan}\n"
                f"Alamat: {alamat}\nEmail: {email}\nTelepon: {telepon}\n"
                f"Tanggal Lahir: {tanggal_lahir}\nJenis Kelamin: {jenis_kelamin}"
            )
            messagebox.showinfo("Data Tersimpan", hasil)

            hasil_lengkap = f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user}\n\n{hasil}"
            self.label_hasil.config(text=hasil_lengkap)

            logging.info(f"User '{self.current_user}' menyimpan biodata: {hasil.replace(chr(10), ' | ')}")
        except Exception as e:
            logging.error(f"Error submit_data oleh {self.current_user}: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")

    def validate_form(self, *args):
        nama_valid = self.var_nama.get().strip() != ""
        nim_valid = self.var_nim.get().strip() != ""
        jurusan_valid = self.var_jurusan.get().strip() != ""
        setuju_valid = self.var_setuju.get() == 1

        if nama_valid and nim_valid and jurusan_valid and setuju_valid:
            self.btn_submit.config(state=tk.NORMAL)
        else:
            self.btn_submit.config(state=tk.DISABLED)

    def simpan_hasil(self):
        try:
            hasil_tersimpan = self.label_hasil.cget("text")
            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan.")
                return

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{self.current_user}_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"Data disimpan oleh: {self.current_user}\n")
                file.write(f"Waktu: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)

            messagebox.showinfo("Info", f"Data berhasil disimpan ke '{filename}'")
            logging.info(f"User '{self.current_user}' simpan ke file {filename}")
        except Exception as e:
            logging.error(f"Error simpan file: {str(e)}")
            messagebox.showerror("Error", f"Kesalahan saat simpan:\n{str(e)}")

    # -------------------------
    # Helpers
    # -------------------------
    def _reset_form_biodata(self):
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telepon.delete(0, tk.END)
        self.entry_tanggal.delete(0, tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")
        self.btn_submit.config(state=tk.DISABLED)

    def _update_title_with_user(self):
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    def _buat_menu(self):
        self.menu_bar = tk.Menu(self)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Simpan Data", command=self.simpan_hasil)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Keluar", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=self.menu_bar)

    def _hapus_menu(self):
        self.config(menu="")

    def logout(self):
        logging.info(f"User '{self.current_user}' logout")
        self.current_user = None
        self._update_title_with_user()
        self._pindah_ke(self.frame_login)

    def on_enter(self, e):
        self.btn_submit.config(bg="green", fg="white")

    def on_leave(self, e):
        self.btn_submit.config(bg="lightgreen", fg="black")


if __name__ == "__main__":
    app = AplikasiBiodata()
    app.mainloop()
