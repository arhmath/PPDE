import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from datetime import datetime

class InteractiveDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Dashboard - Real-time Updates")
        self.root.configure(bg='#0f1419')
        # Menghapus pengaturan ukuran jendela tetap agar bisa diubah ukurannya
        # self.root.geometry("1200x1000")

        # Data variables
        self.is_running = False
        self.cpu_data = []
        self.memory_data = []
        self.network_data = []
        self.max_data_points = 50

        # Metrics
        self.current_cpu = 0
        self.current_memory = 0
        self.current_network = 0
        self.total_requests = 0
        self.active_users = 0

        self._setup_styles()
        self._buat_interface()

    def _setup_styles(self):
        self.style = ttk.Style()

        # Dashboard theme
        self.style.configure('Dashboard.TFrame',
                            background='#1e2328',
                            relief='flat')

        self.style.configure('Card.TFrame',
                            background='#252a31',
                            relief='raised',
                            borderwidth=1)

        self.style.configure('Dashboard.TLabel',
                            background='#1e2328',
                            foreground='#ffffff',
                            font=('Arial', 10))

        self.style.configure('Title.TLabel',
                            background='#1e2328',
                            foreground='#00d4ff',
                            font=('Arial', 14, 'bold'))

        self.style.configure('Metric.TLabel',
                            background='#252a31',
                            foreground='#00ff88',
                            font=('Arial', 20, 'bold'))

        self.style.configure('MetricLabel.TLabel',
                            background='#252a31',
                            foreground='#ffffff',
                            font=('Arial', 9))

        self.style.configure('Control.TButton',
                            background='#00d4ff',
                            foreground='#0f1419',
                            borderwidth=0,
                            padding=(15, 8),
                            font=('Arial', 10, 'bold'))
        
    def _buat_interface(self):
        # Main container menggunakan grid
        self.main_frame = ttk.Frame(self.root, style='Dashboard.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Konfigurasi baris dan kolom agar dapat diperluas
        self.main_frame.grid_columnconfigure(0, weight=1)
        for i in range(5): # Ada 5 baris utama (header, metrik, stat, chart, kontrol)
            self.main_frame.grid_rowconfigure(i, weight=1 if i == 3 else 0)

        # Header
        header_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        header_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 20))

        ttk.Label(header_frame, text="📊 System Dashboard",
                  style='Title.TLabel').pack(side='left')

        self.status_label = ttk.Label(header_frame, text="● Stopped",
                                      style='Dashboard.TLabel')
        self.status_label.pack(side='right')

        self.time_label = ttk.Label(header_frame, text="",
                                    style='Dashboard.TLabel')
        self.time_label.pack(side='right', padx=(0, 20))

        # Metrics cards row (menggunakan grid)
        metrics_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        metrics_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        metrics_frame.grid_columnconfigure(2, weight=1)

        # CPU Card
        self.cpu_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.cpu_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        ttk.Label(self.cpu_card, text="CPU Usage", style='MetricLabel.TLabel').pack()
        self.cpu_metric = ttk.Label(self.cpu_card, text="0%", style='Metric.TLabel')
        self.cpu_metric.pack(pady=(5, 0))
        self.cpu_progress = ttk.Progressbar(self.cpu_card, mode='determinate', length=200)
        self.cpu_progress.pack(pady=(10, 0), fill='x')

        # Memory Card
        self.memory_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.memory_card.grid(row=0, column=1, sticky='nsew', padx=(5, 5))
        ttk.Label(self.memory_card, text="Memory Usage", style='MetricLabel.TLabel').pack()
        self.memory_metric = ttk.Label(self.memory_card, text="0%", style='Metric.TLabel')
        self.memory_metric.pack(pady=(5, 0))
        self.memory_progress = ttk.Progressbar(self.memory_card, mode='determinate', length=200)
        self.memory_progress.pack(pady=(10, 0), fill='x')

        # Network Card
        self.network_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding="15")
        self.network_card.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        ttk.Label(self.network_card, text="Network I/O", style='MetricLabel.TLabel').pack()
        self.network_metric = ttk.Label(self.network_card, text="0 MB/s", style='Metric.TLabel')
        self.network_metric.pack(pady=(5, 0))
        self.network_progress = ttk.Progressbar(self.network_card, mode='determinate', length=200)
        self.network_progress.pack(pady=(10, 0), fill='x')

        # Statistics row (menggunakan grid)
        stats_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        stats_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 20))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        # Requests Card
        requests_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        requests_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        ttk.Label(requests_card, text="Total Requests", style='MetricLabel.TLabel').pack()
        self.requests_metric = ttk.Label(requests_card, text="0", style='Metric.TLabel')
        self.requests_metric.pack(pady=(5, 0))

        # Users Card
        users_card = ttk.Frame(stats_frame, style='Card.TFrame', padding="15")
        users_card.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        ttk.Label(users_card, text="Active Users", style='MetricLabel.TLabel').pack()
        self.users_metric = ttk.Label(users_card, text="0", style='Metric.TLabel')
        self.users_metric.pack(pady=(5, 0))

        # Chart area (menggunakan grid)
        chart_frame = ttk.LabelFrame(self.main_frame, text="Real-time Monitoring", padding="15")
        chart_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 20))
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        self.chart_text = tk.Text(chart_frame, height=15, bg='#0f1419', fg='#00ff88',
                                  font=('Consolas', 9), state='disabled')
        self.chart_text.grid(row=0, column=0, sticky='nsew')

        # Scrollbar untuk chart
        chart_scroll = ttk.Scrollbar(chart_frame, orient="vertical", command=self.chart_text.yview)
        chart_scroll.grid(row=0, column=1, sticky='ns')
        self.chart_text.configure(yscrollcommand=chart_scroll.set)

        # Control buttons (menggunakan grid)
        control_frame = ttk.Frame(self.main_frame, style='Dashboard.TFrame')
        control_frame.grid(row=4, column=0, sticky='ew')

        ttk.Button(control_frame, text="▶ Start Monitoring",
                   style='Control.TButton', command=self.start_monitoring).pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="⏸ Stop Monitoring",
                   style='Control.TButton', command=self.stop_monitoring).pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="🗑 Clear Data",
                   style='Control.TButton', command=self.clear_data).pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="📊 Generate Report",
                   style='Control.TButton', command=self.generate_report).pack(side='right')

        # Start time updates
        self._update_time()

    def _update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)

    def start_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="● Running", foreground='#00ff88')
            threading.Thread(target=self._monitoring_loop, daemon=True).start()

    def stop_monitoring(self):
        self.is_running = False
        self.status_label.config(text="● Stopped", foreground='#ff4444')

    def _monitoring_loop(self):
        while self.is_running:
            # Generate random data
            self.current_cpu = random.randint(10, 90)
            self.current_memory = random.randint(20, 80)
            self.current_network = random.uniform(0.1, 10.0)

            # Update requests and users
            self.total_requests += random.randint(1, 5)
            self.active_users = random.randint(50, 200)

            # Store data for chart
            self.cpu_data.append(self.current_cpu)
            self.memory_data.append(self.current_memory)
            self.network_data.append(self.current_network)

            # Limit data points
            if len(self.cpu_data) > self.max_data_points:
                self.cpu_data.pop(0)
                self.memory_data.pop(0)
                self.network_data.pop(0)

            # Update UI
            self.root.after(0, self._update_metrics)
            self.root.after(0, self._update_chart)

            time.sleep(1)  # Update every second

    def _update_metrics(self):
        # Update metric displays
        self.cpu_metric.config(text=f"{self.current_cpu}%")
        self.cpu_progress['value'] = self.current_cpu

        self.memory_metric.config(text=f"{self.current_memory}%")
        self.memory_progress['value'] = self.current_memory

        self.network_metric.config(text=f"{self.current_network:.1f} MB/s")
        self.network_progress['value'] = min(self.current_network * 10, 100)

        self.requests_metric.config(text=str(self.total_requests))
        self.users_metric.config(text=str(self.active_users))

    def _update_chart(self):
        if not self.cpu_data:
            return

        self.chart_text.config(state='normal')

        # Create simple ASCII chart
        timestamp = datetime.now().strftime("%H:%M:%S")
        cpu_bar = "█" * (self.current_cpu // 5)
        memory_bar = "█" * (self.current_memory // 5)
        network_bar = "█" * min(int(self.current_network), 20)

        chart_line = f"[{timestamp}] CPU: {cpu_bar:<20} {self.current_cpu}% | "
        chart_line += f"MEM: {memory_bar:<20} {self.current_memory}% | "
        chart_line += f"NET: {network_bar:<20} {self.current_network:.1f}MB/s\n"

        self.chart_text.insert('end', chart_line)
        self.chart_text.see('end')
        self.chart_text.config(state='disabled')

    def clear_data(self):
        self.cpu_data.clear()
        self.memory_data.clear()
        self.network_data.clear()
        self.total_requests = 0

        self.chart_text.config(state='normal')
        self.chart_text.delete('1.0', 'end')
        self.chart_text.config(state='disabled')

        # Reset metrics
        self.cpu_metric.config(text="0%")
        self.memory_metric.config(text="0%")
        self.network_metric.config(text="0 MB/s")
        self.requests_metric.config(text="0")
        self.users_metric.config(text="0")

        self.cpu_progress['value'] = 0
        self.memory_progress['value'] = 0
        self.network_progress['value'] = 0

    def generate_report(self):
        if not self.cpu_data:
            return

        # Generate summary report
        avg_cpu = sum(self.cpu_data) / len(self.cpu_data)
        avg_memory = sum(self.memory_data) / len(self.memory_data)
        avg_network = sum(self.network_data) / len(self.network_data)

        report = f"\n{'='*60}\n"
        report += f"SYSTEM PERFORMANCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*60}\n"
        report += f"Average CPU Usage: {avg_cpu:.1f}%\n"
        report += f"Average Memory Usage: {avg_memory:.1f}%\n"
        report += f"Average Network I/O: {avg_network:.1f} MB/s\n"
        report += f"Total Requests: {self.total_requests}\n"
        report += f"Current Active Users: {self.active_users}\n"
        report += f"Data Points Collected: {len(self.cpu_data)}\n"
        report += f"{'='*60}\n\n"

        self.chart_text.config(state='normal')
        self.chart_text.insert('end', report)
        self.chart_text.see('end')
        self.chart_text.config(state='disabled')

    def run(self):
        self.root.mainloop()

# Jalankan aplikasi
if __name__ == "__main__":
    app = InteractiveDashboard()
    app.run()
