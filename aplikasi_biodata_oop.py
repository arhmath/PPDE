import tkinter as tk
from tkinter import messagebox
import datetime
import logging
import re
import os

# Membuat kelas utama aplikasi yang mewarisi dari tk.Tk
class AplikasiBiodata(tk.Tk):
    # Metode __init__ adalah constructor yang akan dijalankan saat objek dibuat
    def __init__(self):
        # Memanggil constructor dari kelas induk (tk.Tk)
        super().__init__()

        # --- Penentuan Path ---
        # Menentukan direktori tempat script ini berjalan
        # __file__ adalah path ke script python yang sedang dieksekusi
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(self.script_dir, 'app.log')

        # Konfigurasi logging untuk menyimpan di direktori script
        # Hapus handler default jika ada, untuk mengkonfigurasi ulang dengan path baru
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=log_file_path,
                            filemode='w')

        # Versi Aplikasi
        self.__version__ = "2.2.2" # Versi update bug fix dan background

        # Mengkonfigurasi window utama
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x900") # Menambah tinggi window untuk field baru
        self.resizable(True, True)
        
        # Mengatur warna background utama
        self.configure(bg="whitesmoke")
        
        # Database user sederhana (dalam aplikasi nyata, ini akan di database)
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456",
            "23106050061": "faisal123"
        }

        # Status login
        self.current_user = None
        self.menu_bar = None
        
        # Atribut untuk manajemen frame
        self.frame_aktif = None
        
        # File untuk fitur "Remember Me" (dengan path lengkap)
        self.remember_file = os.path.join(self.script_dir, "remember_me.txt")

        # Buat semua tampilan (views)
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        # Tampilkan frame login di awal
        self._pindah_ke(self.frame_login)
        
        # Log aplikasi start
        logging.info("Aplikasi dimulai")

    def keluar_aplikasi(self):
        """Keluar dari aplikasi dengan konfirmasi"""
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            logging.info(f"Application closed by user: {self.current_user}")
            self.destroy()

    def _pindah_ke(self, frame_tujuan):
        """Menyembunyikan frame aktif dan menampilkan frame tujuan."""
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()  # Sembunyikan frame yang sedang aktif
        
        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True) # Tampilkan frame tujuan

        # Auto-focus dan aksi tambahan berdasarkan frame yang ditampilkan
        if frame_tujuan == self.frame_login:
            # Aksi saat kembali ke halaman login (logout)
            self.current_user = None
            self._hapus_menu()
            self._update_title_with_user()
            # Jangan hapus username dan password jika "Remember Me" aktif
            if self.var_remember_me.get() == 0:
                self.entry_username.delete(0, tk.END)
                self.entry_password.delete(0, tk.END)

            self._reset_form_biodata()
            self.after(100, lambda: self.entry_username.focus_set())
        elif frame_tujuan == self.frame_biodata:
            # Update label selamat datang dan set focus
            self.label_selamat_datang.config(text=f"Selamat Datang, {self.current_user}!")
            self.after(100, lambda: self.entry_nama.focus_set())

    def _coba_login(self):
        """Method untuk memproses attempt login dengan logging"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        # Log attempt login
        logging.info(f"Login attempt for username: {username}")

        # Handle "Remember Me"
        if self.var_remember_me.get() == 1:
            try:
                with open(self.remember_file, "w") as f:
                    # WARNING: Menyimpan password dalam plain text adalah risiko keamanan.
                    f.write(f"{username}\n{password}")
            except Exception as e:
                logging.error(f"Failed to write remember_me file: {e}")
        else:
            # Hapus file jika "Remember Me" tidak dicentang
            if os.path.exists(self.remember_file):
                os.remove(self.remember_file)

        # Validasi input kosong
        if not username or not password:
            logging.warning(f"Empty credentials attempt for username: {username}")
            messagebox.showwarning("Login Gagal", "Username dan Password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        # Validasi panjang minimum
        if len(username) < 3:
            logging.warning(f"Username too short: {username}")
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        # Cek kredensial di database
        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username
            logging.info(f"Successful login for user: {username}")
            messagebox.showinfo("Login Berhasil", f"Selamat Datang, {username}!")
            self._reset_form_biodata()
            self._update_title_with_user()
            self._buat_menu()
            self._pindah_ke(self.frame_biodata)
            # Bersihkan field password setelah berhasil jika remember me tidak aktif
            if self.var_remember_me.get() == 0:
                self.entry_password.delete(0, tk.END)
        else:
            logging.warning(f"Failed login attempt for username: {username}")
            messagebox.showerror("Login Gagal", "Username atau Password salah.")
            # Bersihkan password dan focus ke username
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    def _logout(self):
        """Method untuk logout dengan logging"""
        if messagebox.askyesno("Logout", f"Apakah {self.current_user} yakin ingin logout?"):
            logging.info(f"User logout: {self.current_user}")
            # Reset status user
            self.current_user = None
            # Update title
            self._update_title_with_user()
            # Bersihkan field password jika remember me tidak aktif
            if self.var_remember_me.get() == 0:
                self.entry_password.delete(0, tk.END)
            # Reset form biodata
            self._reset_form_biodata()
            # Kembali ke halaman login
            self._pindah_ke(self.frame_login)
            # Focus ke username field
            self.entry_username.focus_set()

    def _buat_menu(self):
        """Membuat menu bar untuk aplikasi"""
        if self.menu_bar:
            self.menu_bar.destroy()
            
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Menu File
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Simpan Hasil", command=self.simpan_hasil)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.keluar_aplikasi)
        
        # Menu Help
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _show_about(self):
        """Menampilkan dialog 'About' aplikasi"""
        about_message = (
            f"Aplikasi Biodata Mahasiswa v{self.__version__}\n\n"
            "Dibuat oleh:\n"
            "Hanif Ubaidur Rohman Syah (NIM: 23106050081)\n\n"
            f"Dibuat pada: {datetime.date.today().strftime('%d %B %Y')}\n\n"
            "Aplikasi ini dibuat untuk memenuhi tugas praktikum."
        )
        messagebox.showinfo("Tentang Aplikasi", about_message)
        
    def _hapus_menu(self):
        """Menghapus menu bar dari window."""
        empty_menu = tk.Menu(self)
        self.config(menu=empty_menu)
        self.menu_bar = None
            
    def _reset_form_biodata(self):
        """Mereset semua field pada form biodata ke keadaan awal."""
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.var_email.set("")
        self.var_telepon.set("")
        self.var_tgllahir.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")
        # State tombol submit akan otomatis ter-update oleh trace
        self.validate_form()

    def _update_title_with_user(self):
        """Update judul window dengan nama user yang login"""
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa") # Judul default

    def _toggle_password_visibility(self):
        """Mengubah visibilitas password pada entry field."""
        if self.entry_password.cget('show') == '*':
            self.entry_password.config(show='')
            self.btn_show_hide.config(text='Hide')
        else:
            self.entry_password.config(show='*')
            self.btn_show_hide.config(text='Show')

    def _buat_tampilan_login(self):
        """Membuat semua widget untuk tampilan login."""
        self.frame_login = tk.Frame(master=self, padx=20, pady=100, bg="whitesmoke")
        
        self.frame_login.columnconfigure(0, weight=1)
        self.frame_login.columnconfigure(1, weight=2)
        
        tk.Label(
            self.frame_login,
            text="HALAMAN LOGIN",
            font=("Arial", 16, "bold"),
            bg="whitesmoke"
        ).grid(row=0, column=0, columnspan=3, pady=20)

        tk.Label(
            self.frame_login,
            text="Username:",
            font=("Arial", 12),
            bg="whitesmoke"
        ).grid(row=1, column=0, sticky="W", pady=5)

        self.entry_username = tk.Entry(self.frame_login, font=("Arial", 12))
        self.entry_username.grid(row=1, column=1, columnspan=2, pady=5, sticky="EW")
        
        tk.Label(
            self.frame_login, 
            text="Password:", 
            font=("Arial", 12),
            bg="whitesmoke"
        ).grid(row=2, column=0, sticky="W", pady=5)
        
        self.entry_password = tk.Entry(
            self.frame_login, 
            font=("Arial", 12), 
            show="*"
        )
        self.entry_password.grid(row=2, column=1, pady=5, sticky="EW")
        
        # Inisialisasi var_remember_me sebelum digunakan
        self.var_remember_me = tk.IntVar(value=0)
        
        # Baca username dan password terakhir jika ada
        try:
            if os.path.exists(self.remember_file):
                with open(self.remember_file, "r") as f:
                    lines = f.read().splitlines()
                    if len(lines) >= 2:
                        last_user, last_pass = lines[0], lines[1]
                        self.entry_username.insert(0, last_user)
                        self.entry_password.insert(0, last_pass)
                        self.var_remember_me.set(1)
        except Exception as e:
            logging.error(f"Could not read remember_me file: {e}")


        self.btn_show_hide = tk.Button(
            self.frame_login,
            text="Show",
            command=self._toggle_password_visibility
        )
        self.btn_show_hide.grid(row=2, column=2, padx=(5,0), sticky="W")
        
        # Checkbox "Remember Me"
        self.check_remember = tk.Checkbutton(
            self.frame_login,
            text="Remember Me",
            variable=self.var_remember_me,
            font=("Arial", 10),
            bg="whitesmoke"
        )
        self.check_remember.grid(row=3, column=1, columnspan=2, sticky="W")

        self.btn_login = tk.Button(
            self.frame_login, 
            text="Login", 
            font=("Arial", 12, "bold"),
            command=self._coba_login
        )
        self.btn_login.grid(row=4, column=0, columnspan=3, pady=20, sticky="EW")

        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus_set())
        self.entry_password.bind("<Return>", lambda e: self._coba_login())

        info_text = (
            "Info: Username yang tersedia:\n"
            "admin (password: 123)\n"
            "user1 (password: password1)\n"
            "mahasiswa (password: 123456)\n"
            "23106050061 (password: faisal123)"
        )
        info_label = tk.Label(
            self.frame_login,
            text=info_text,
            font=("Arial", 9),
            fg="gray",
            justify=tk.LEFT,
            bg="whitesmoke"
        )
        info_label.grid(row=5, column=0, columnspan=3, pady=10)


    def _buat_tampilan_biodata(self):
        """Membuat semua widget untuk tampilan biodata."""
        # --- Variabel Kontrol Tkinter ---
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telepon = tk.StringVar()
        self.var_tgllahir = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        # --- Frame Biodata ---
        self.frame_biodata = tk.Frame(master=self, padx=20, pady=20, bg="whitesmoke")
        self.frame_biodata.columnconfigure(0, weight=1)
        self.frame_biodata.columnconfigure(1, weight=1)

        # Aktifkan trace untuk validasi real-time
        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_jurusan.trace_add("write", self.validate_form)
        self.var_email.trace_add("write", self.validate_form)
        self.var_telepon.trace_add("write", self.validate_form)

        # Label Selamat Datang
        self.label_selamat_datang = tk.Label(
            master=self.frame_biodata,
            text="", # Teks akan diupdate saat pindah frame
            font=("Arial", 12, "italic"),
            bg="whitesmoke"
        )
        self.label_selamat_datang.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="W")

        # Judul
        self.label_judul = tk.Label(
            master=self.frame_biodata, 
            text="FORM BIODATA MAHASISWA", 
            font=("Arial", 16, "bold"),
            bg="whitesmoke"
        )
        self.label_judul.grid(row=1, column=0, columnspan=2, pady=10)

        # Frame khusus untuk input dengan border
        self.frame_input = tk.Frame(
            master=self.frame_biodata, 
            relief=tk.GROOVE, 
            borderwidth=2, 
            padx=10, 
            pady=10,
            bg="whitesmoke"
        )
        self.frame_input.grid(row=2, column=0, columnspan=2, sticky="EW")
        self.frame_input.columnconfigure(1, weight=1)

        # --- Input Fields ---
        row_num = 0
        tk.Label(master=self.frame_input, text="Nama Lengkap:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_nama = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_nama)
        self.entry_nama.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1

        tk.Label(master=self.frame_input, text="NIM:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_nim = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_nim)
        self.entry_nim.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1

        tk.Label(master=self.frame_input, text="Jurusan:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_jurusan = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_jurusan)
        self.entry_jurusan.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1
        
        tk.Label(master=self.frame_input, text="Email:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_email = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_email)
        self.entry_email.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1
        
        tk.Label(master=self.frame_input, text="Telepon:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_telepon = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_telepon)
        self.entry_telepon.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1
        
        tk.Label(master=self.frame_input, text="Tgl Lahir (DD-MM-YYYY):", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        self.entry_tgllahir = tk.Entry(master=self.frame_input, font=("Arial", 12), textvariable=self.var_tgllahir)
        self.entry_tgllahir.grid(row=row_num, column=1, pady=2, sticky="EW")
        row_num += 1

        # Alamat
        tk.Label(master=self.frame_input, text="Alamat:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="NW", pady=2)
        frame_alamat = tk.Frame(master=self.frame_input, relief=tk.SUNKEN, borderwidth=1)
        frame_alamat.grid(row=row_num, column=1, pady=2, sticky="EW")
        scrollbar_alamat = tk.Scrollbar(master=frame_alamat)
        scrollbar_alamat.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_alamat = tk.Text(master=frame_alamat, height=4, width=28, font=("Arial", 12))
        self.text_alamat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_alamat.config(command=self.text_alamat.yview)
        self.text_alamat.config(yscrollcommand=scrollbar_alamat.set)
        row_num += 1
        
        # Jenis Kelamin
        tk.Label(master=self.frame_input, text="Jenis Kelamin:", font=("Arial", 12), bg="whitesmoke").grid(row=row_num, column=0, sticky="W", pady=2)
        frame_jk = tk.Frame(master=self.frame_input, bg="whitesmoke")
        frame_jk.grid(row=row_num, column=1, sticky="W")
        tk.Radiobutton(master=frame_jk, text="Pria", variable=self.var_jk, value="Pria", bg="whitesmoke").pack(side=tk.LEFT)
        tk.Radiobutton(master=frame_jk, text="Wanita", variable=self.var_jk, value="Wanita", bg="whitesmoke").pack(side=tk.LEFT)
        row_num += 1

        # Checkbox persetujuan
        self.check_setuju = tk.Checkbutton(
            master=self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            font=("Arial", 10),
            command=self.validate_form,
            bg="whitesmoke"
        )
        self.check_setuju.grid(row=row_num, column=0, columnspan=2, pady=10, sticky="W")
        
        # Frame untuk tombol-tombol
        frame_tombol = tk.Frame(master=self.frame_biodata, bg="whitesmoke")
        frame_tombol.grid(row=3, column=0, columnspan=2, pady=10, sticky="EW")
        frame_tombol.columnconfigure(0, weight=1)
        frame_tombol.columnconfigure(1, weight=1)
        frame_tombol.columnconfigure(2, weight=1)

        # Tombol submit
        self.btn_submit = tk.Button(master=frame_tombol, text="Submit Biodata", font=("Arial", 12, "bold"), command=self.submit_data, state=tk.DISABLED)
        self.btn_submit.grid(row=0, column=0, padx=5, sticky="EW")

        # Tombol Reset
        self.btn_reset = tk.Button(master=frame_tombol, text="Reset Form", font=("Arial", 12), command=self._reset_form_biodata)
        self.btn_reset.grid(row=0, column=1, padx=5, sticky="EW")

        # Tombol Simpan
        self.btn_simpan = tk.Button(master=frame_tombol, text="Simpan Hasil", font=("Arial", 12), command=self.simpan_hasil)
        self.btn_simpan.grid(row=0, column=2, padx=5, sticky="EW")

        # Event bindings
        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)
        self.entry_jurusan.bind("<Return>", self.submit_shortcut)
        
        # Label hasil
        self.label_hasil = tk.Label(master=self.frame_biodata, text="", font=("Arial", 12, "italic"), justify=tk.LEFT, wraplength=550, bg="whitesmoke")
        self.label_hasil.grid(row=4, column=0, columnspan=2, sticky="W", padx=10, pady=10)
        
        tk.Button(master=self.frame_biodata, text="< Logout", command=self._logout).grid(row=5, column=0, columnspan=2, pady=10, sticky="EW")

    def simpan_hasil(self):
        """Simpan hasil biodata ke file dengan error handling"""
        try:
            hasil_tersimpan = self.label_hasil.cget("text")
            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan. Mohon submit terlebih dahulu.")
                return
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{self.current_user}_{timestamp}.txt"
            # Gabungkan direktori script dengan nama file
            full_path = os.path.join(self.script_dir, filename)
            
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(f"Data disimpan oleh: {self.current_user}\n")
                file.write(f"Waktu penyimpanan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)
            
            messagebox.showinfo("Info", f"Data berhasil disimpan ke file '{filename}'.")
            logging.info(f"Data saved to {full_path} by user {self.current_user}")
        except PermissionError:
            logging.error(f"Permission denied to save file for user {self.current_user}")
            messagebox.showerror("Error", "Tidak memiliki izin untuk menyimpan file di lokasi ini.")
        except Exception as e:
            logging.error(f"Error saving file for user {self.current_user}: {e}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan file:\n{str(e)}")


    def submit_data(self):
        """Submit data biodata dengan validasi lengkap"""
        try:
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Peringatan", "Anda harus menyetujui pengumpulan data!")
                return
            
            # Ambil data dari form
            nama = self.var_nama.get().strip()
            nim = self.var_nim.get().strip()
            jurusan = self.var_jurusan.get().strip()
            email = self.var_email.get().strip()
            telepon = self.var_telepon.get().strip()
            tgl_lahir = self.var_tgllahir.get().strip()
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            jenis_kelamin = self.var_jk.get()

            # Validasi field wajib
            if not all([nama, nim, jurusan, email, telepon]):
                messagebox.showwarning("Input Kosong", "Nama, NIM, Jurusan, Email, dan Telepon harus diisi!")
                return

            if nama.isdigit():
                messagebox.showwarning("Format Nama Salah", "Nama tidak boleh hanya berupa angka!")
                self.entry_nama.focus_set()
                return

            if not nim.isdigit() or len(nim) < 8:
                messagebox.showwarning("Format NIM Salah", "NIM harus berupa angka minimal 8 digit!")
                self.entry_nim.focus_set()
                return
            
            # Validasi Email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messagebox.showwarning("Format Email Salah", "Format email tidak valid. Contoh: nama@domain.com")
                self.entry_email.focus_set()
                return

            # Validasi Telepon (Format Indonesia)
            if not re.match(r'^(08|\+62[ ]?)\d{8,13}$', telepon):
                messagebox.showwarning("Format Telepon Salah", "Format nomor telepon Indonesia tidak valid. Contoh: 08... atau +62...")
                self.entry_telepon.focus_set()
                return
                
            # Validasi Tanggal Lahir (opsional, tapi jika diisi, format harus benar)
            if tgl_lahir:
                try:
                    datetime.datetime.strptime(tgl_lahir, '%d-%m-%Y')
                except ValueError:
                    messagebox.showwarning("Format Tanggal Salah", "Format tanggal lahir harus DD-MM-YYYY. Contoh: 31-12-2000")
                    self.entry_tgllahir.focus_set()
                    return

            # Tampilkan hasil
            hasil = (f"Nama: {nama}\nNIM: {nim}\nJurusan: {jurusan}\nEmail: {email}\n"
                     f"Telepon: {telepon}\nTanggal Lahir: {tgl_lahir or 'Tidak diisi'}\nAlamat: {alamat or 'Tidak diisi'}\n"
                     f"Jenis Kelamin: {jenis_kelamin}")
            messagebox.showinfo("Data Tersimpan", hasil)
            
            logging.info(f"Data submitted by user: {self.current_user} - NIM: {nim}")

            hasil_lengkap = f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user}\n\n{hasil}"
            self.label_hasil.config(text=hasil_lengkap)
        except Exception as e:
            logging.error(f"Error in submit_data by {self.current_user}: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data:\n{str(e)}")

    def validate_form(self, *args):
        """Memvalidasi form secara real-time untuk mengaktifkan/menonaktifkan tombol submit."""
        nama_valid = self.var_nama.get().strip() != ""
        nim_valid = self.var_nim.get().strip() != ""
        jurusan_valid = self.var_jurusan.get().strip() != ""
        email_valid = self.var_email.get().strip() != ""
        telepon_valid = self.var_telepon.get().strip() != ""
        setuju_valid = self.var_setuju.get() == 1

        if all([nama_valid, nim_valid, jurusan_valid, email_valid, telepon_valid, setuju_valid]):
            self.btn_submit.config(state=tk.NORMAL)
        else:
            self.btn_submit.config(state=tk.DISABLED)

    def on_enter(self, event):
        if self.btn_submit['state'] == tk.NORMAL:
            self.btn_submit.config(bg="lightblue")

    def on_leave(self, event):
        self.btn_submit.config(bg="SystemButtonFace")

    def submit_shortcut(self, event=None):
        if self.btn_submit['state'] == tk.NORMAL:
            self.submit_data()
            
# Blok berikut hanya akan dieksekusi jika file ini dijalankan secara langsung
if __name__ == "__main__":
    # Membuat instance dari kelas aplikasi kita
    app = AplikasiBiodata()
    # Menjalankan mainloop dari instance tersebut
    app.mainloop()
