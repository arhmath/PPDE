import tkinter as tk
from tkinter import ttk

class ResponsiveApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Responsive Design dengan ttk")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)

        # Variabel untuk tracking ukuran window
        self.current_width = 800
        self.current_height = 600

        self._setup_styles()
        self._buat_interface()
        self._bind_events()

    def _setup_styles(self):
        self.style = ttk.Style()

        # Style untuk desktop (default)
        self.style.configure('Desktop.TLabel',
                            font=('Arial', 12),
                            padding=(10, 5))

        # Style untuk tablet
        self.style.configure('Tablet.TLabel',
                            font=('Arial', 10),
                            padding=(8, 4))

        # Style untuk mobile
        self.style.configure('Mobile.TLabel',
                            font=('Arial', 9),
                            padding=(5, 3))

        # Button styles
        self.style.configure('Desktop.TButton',
                            padding=(15, 8),
                            font=('Arial', 11))

        self.style.configure('Tablet.TButton',
                            padding=(12, 6),
                            font=('Arial', 10))

        self.style.configure('Mobile.TButton',
                            padding=(8, 4),
                            font=('Arial', 9))

    def _buat_interface(self):
        # Main container menggunakan grid
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header section
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.grid(row=0, column=0, sticky='ew')

        self.title_label = ttk.Label(self.header_frame, text="Responsive Design Demo",
                                     style='Desktop.TLabel')
        self.title_label.pack()

        self.size_label = ttk.Label(self.header_frame, text=f"Window Size: {self.current_width}x{self.current_height}",
                                   style='Desktop.TLabel')
        self.size_label.pack(pady=(5,0))

        # Content grid yang akan berubah layout
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky='nsew', pady=(20, 0))
        # Mengizinkan baris ini untuk diperluas
        self.main_frame.grid_rowconfigure(1, weight=1) 

        # Cards yang akan di-reposition berdasarkan ukuran window
        self.cards = []
        for i in range(6):
            card = ttk.LabelFrame(self.content_frame, text=f"Card {i+1}", padding="15")
            ttk.Label(card, text=f"Konten untuk card {i+1}",
                      style='Desktop.TLabel').pack()
            ttk.Button(card, text=f"Aksi {i+1}",
                       style='Desktop.TButton').pack(pady=(10,0))
            self.cards.append(card)

        # Control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="15")
        self.control_frame.grid(row=2, column=0, sticky='ew', pady=(20,0))

        ttk.Button(self.control_frame, text="Simulasi Mobile (400x600)",
                   command=lambda: self.resize_window(400, 600),
                   style='Desktop.TButton').pack(side='left', padx=(0,10))

        ttk.Button(self.control_frame, text="Simulasi Tablet (600x800)",
                   command=lambda: self.resize_window(600, 800),
                   style='Desktop.TButton').pack(side='left', padx=(0,10))

        ttk.Button(self.control_frame, text="Simulasi Desktop (800x600)",
                   command=lambda: self.resize_window(800, 600),
                   style='Desktop.TButton').pack(side='left')

        # Initial layout
        self._update_layout()

    def _bind_events(self):
        self.root.bind('<Configure>', self._on_window_resize)

    def _on_window_resize(self, event):
        if event.widget == self.root:
            self.current_width = self.root.winfo_width()
            self.current_height = self.root.winfo_height()
            self.size_label.config(text=f"Window Size: {self.current_width}x{self.current_height}")
            self._update_layout()

    def _update_layout(self):
        # Hapus layout grid yang lama
        for card in self.cards:
            card.grid_forget()

        # Tentukan layout berdasarkan lebar jendela
        if self.current_width < 500:  # Mobile: 1 kolom
            self._apply_layout(columns=1)
            self._update_styles('Mobile')
        elif self.current_width < 700:  # Tablet: 2 kolom
            self._apply_layout(columns=2)
            self._update_styles('Tablet')
        else:  # Desktop: 3 kolom
            self._apply_layout(columns=3)
            self._update_styles('Desktop')

    def _apply_layout(self, columns):
        # Konfigurasi kolom agar dapat diperluas secara merata
        for i in range(columns):
            self.content_frame.grid_columnconfigure(i, weight=1)

        # Tempatkan kartu-kartu dalam grid
        for i, card in enumerate(self.cards):
            row = i // columns
            col = i % columns
            padx = 10 if columns > 1 else 0
            pady = 10
            card.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
            
    def _update_styles(self, size):
        style_suffix = f'{size}.TLabel'
        button_style = f'{size}.TButton'

        self.title_label.config(style=style_suffix)
        self.size_label.config(style=style_suffix)

        # Update semua label dan button di dalam kartu
        for card in self.cards:
            for child in card.winfo_children():
                if isinstance(child, ttk.Label):
                    child.config(style=style_suffix)
                elif isinstance(child, ttk.Button):
                    child.config(style=button_style)

    def resize_window(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def run(self):
        self.root.mainloop()

# Jalankan aplikasi
if __name__ == "__main__":
    app = ResponsiveApp()
    app.run()
