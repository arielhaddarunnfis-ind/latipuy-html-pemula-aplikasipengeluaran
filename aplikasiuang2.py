"""
================================================================================
Aplikasi: LATIPUY - Smart Monthly Income & Expense Manager
Deskripsi: Aplikasi pencatat & penghitung pemasukan dan pengeluaran bulanan
           dengan desain modern berbasis Python Tkinter.
================================================================================
"""

import os
import json
import csv
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Nama File Penyimpanan Data
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latipuy_data.json")
WEB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latipuy_web.html")

# ==============================================================================
# PALET WARNA MODERN (DARK THEME ELEGAN)
# ==============================================================================
THEME = {
    "bg_root": "#0B0F19",        # Hitam kebiruan sangat gelap (latar utama)
    "bg_sidebar": "#111827",     # Abu gelap kebiruan (sidebar)
    "bg_card": "#1E293B",        # Card container
    "bg_card_hover": "#26354A",  # Card hover
    "bg_input": "#0F172A",       # Input field background
    "border": "#334155",         # Garis tepi halus
    "border_light": "#475569",   # Garis tepi terang
    
    "primary": "#6366F1",        # Indigo modern (warna aksen brand)
    "primary_hover": "#4F46E5",  # Indigo gelap
    "income": "#10B981",         # Emerald Green (Pemasukan)
    "income_light": "#D1FAE5",
    "expense": "#F43F5E",        # Rose Red (Pengeluaran)
    "expense_light": "#FFE4E6",
    "balance": "#38BDF8",        # Sky Blue (Saldo)
    "warning": "#F59E0B",        # Amber
    
    "text_primary": "#F8FAFC",   # Putih terang
    "text_secondary": "#94A3B8", # Abu muda
    "text_muted": "#64748B",     # Abu redup
    "row_odd": "#172033",        # Warna baris tabel 1
    "row_even": "#1E293B",       # Warna baris tabel 2
}

# Daftar Kategori Default
KATEGORI_PEMASUKAN = [
    "Gaji Pokok",
    "Bisnis & Usaha",
    "Freelance / Side Job",
    "Investasi & Dividen",
    "Bonus & THR",
    "Hadiah / Hibah",
    "Penjualan Barang",
    "Lain-lain"
]

KATEGORI_PENGELUARAN = [
    "Makanan & Minuman",
    "Transportasi & Bensin",
    "Belanja Bulanan",
    "Tagihan & Listrik / Air",
    "Sewa / Kost / Rumah",
    "Hiburan & Liburan",
    "Kesehatan & Obat",
    "Pendidikan & Kursus",
    "Cicilan & Utang",
    "Keluarga & Donasi",
    "Lain-lain"
]

NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

CHART_COLORS = [
    "#6366F1", "#10B981", "#F43F5E", "#F59E0B", "#38BDF8",
    "#EC4899", "#8B5CF6", "#14B8A6", "#F97316", "#84CC16"
]


# ==============================================================================
# DATA MANAGER (JSON STORAGE)
# ==============================================================================
class DataManager:
    @staticmethod
    def load_data():
        default_data = {
            "initial_balance": 0,
            "budget": 0,
            "transactions": []
        }
        if not os.path.exists(DATA_FILE):
            DataManager.save_data(default_data)
            return default_data
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data

    @staticmethod
    def save_data(data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def format_rupiah(nominal):
    """Format angka menjadi string mata uang Rupiah (contoh: Rp 1.500.000)."""
    try:
        nominal = float(nominal)
        tanda = "-" if nominal < 0 else ""
        nominal_abs = abs(nominal)
        formatted = f"{nominal_abs:,.0f}".replace(",", ".")
        return f"{tanda}Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"


# ==============================================================================
# APLIKASI UTAMA: LATIPUY
# ==============================================================================
class LatipuyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Latipuy - Pengelola Keuangan & Pengeluaran Bulanan")
        self.geometry("1120x740")
        self.minsize(980, 640)
        self.configure(bg=THEME["bg_root"])

        # Load data
        self.data = DataManager.load_data()

        # State filter aktif
        now = datetime.now()
        self.filter_bulan = tk.StringVar(value=str(now.month))
        self.filter_tahun = tk.StringVar(value=str(now.year))
        self.filter_tipe = tk.StringVar(value="Semua")
        self.search_query = tk.StringVar(value="")

        # Setup custom styles untuk ttk
        self.setup_styles()

        # Layout Utama: Sidebar (kiri) + Konten (kanan)
        self.setup_layout()

        # Tampilkan dashboard pertama kali
        self.navigasi_ke("dashboard")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Style Combobox
        style.configure("TCombobox",
                        fieldbackground=THEME["bg_input"],
                        background=THEME["bg_card"],
                        foreground=THEME["text_primary"],
                        arrowcolor=THEME["text_secondary"],
                        bordercolor=THEME["border"],
                        darkcolor=THEME["bg_input"],
                        lightcolor=THEME["bg_input"])
        self.option_add("*TCombobox*Listbox.background", THEME["bg_card"])
        self.option_add("*TCombobox*Listbox.foreground", THEME["text_primary"])
        self.option_add("*TCombobox*Listbox.selectBackground", THEME["primary"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

        # Style Treeview (Tabel Transaksi)
        style.configure("Treeview",
                        background=THEME["row_even"],
                        foreground=THEME["text_primary"],
                        fieldbackground=THEME["bg_card"],
                        rowheight=34,
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=THEME["bg_sidebar"],
                        foreground=THEME["text_secondary"],
                        relief="flat",
                        font=("Segoe UI", 10, "bold"),
                        padding=(10, 8))
        style.map("Treeview",
                  background=[("selected", THEME["primary"])],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Treeview.Heading",
                  background=[("active", THEME["bg_card_hover"])])

        # Style Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=THEME["bg_sidebar"],
                        troughcolor=THEME["bg_root"],
                        bordercolor=THEME["bg_root"],
                        arrowcolor=THEME["text_muted"])

    def setup_layout(self):
        # 1. SIDEBAR (Kiri)
        self.sidebar = tk.Frame(self, bg=THEME["bg_sidebar"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Logo / Title
        brand_frame = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"], pady=24, padx=16)
        brand_frame.pack(fill="x")

        logo_lbl = tk.Label(brand_frame, text="✨ LATIPUY", font=("Segoe UI", 18, "bold"),
                            bg=THEME["bg_sidebar"], fg=THEME["primary"])
        logo_lbl.pack(anchor="w")

        sub_lbl = tk.Label(brand_frame, text="Smart Money Tracker", font=("Segoe UI", 9),
                           bg=THEME["bg_sidebar"], fg=THEME["text_muted"])
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Separator halus
        sep = tk.Frame(self.sidebar, bg=THEME["border"], height=1)
        sep.pack(fill="x", padx=16, pady=(0, 16))

        # Navigasi Menu
        self.nav_buttons = {}
        menu_items = [
            ("dashboard", "📊  Dashboard Ringkasan"),
            ("catat",     "➕  Catat Transaksi"),
            ("riwayat",   "📜  Riwayat & Laporan"),
            ("analisis",  "📈  Grafik & Analisis"),
            ("anggaran",  "🎯  Target & Anggaran"),
        ]

        for view_name, label_text in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                padx=16,
                pady=10,
                bg=THEME["bg_sidebar"],
                fg=THEME["text_secondary"],
                activebackground=THEME["bg_card_hover"],
                activeforeground=THEME["text_primary"],
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda vn=view_name: self.navigasi_ke(vn)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[view_name] = btn

        # Tombol Buka Web Companion di bagian bawah
        bottom_box = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"], padx=14, pady=16)
        bottom_box.pack(side="bottom", fill="x")

        # Mini card Saldo di Sidebar
        self.side_balance_card = tk.Frame(bottom_box, bg=THEME["bg_card"], padx=12, pady=10,
                                          highlightbackground=THEME["border"], highlightthickness=1)
        self.side_balance_card.pack(fill="x", pady=(0, 12))

        lbl_s = tk.Label(self.side_balance_card, text="TOTAL SALDO", font=("Segoe UI", 8, "bold"),
                         bg=THEME["bg_card"], fg=THEME["text_muted"])
        lbl_s.pack(anchor="w")

        self.side_balance_val = tk.Label(self.side_balance_card, text="Rp 0", font=("Segoe UI", 12, "bold"),
                                         bg=THEME["bg_card"], fg=THEME["balance"])
        self.side_balance_val.pack(anchor="w", pady=(2, 0))

        # Tombol web preview
        btn_web = tk.Button(
            bottom_box,
            text="🌐 Buka Versi Web Latipuy",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            pady=8,
            cursor="hand2",
            command=self.buka_versi_web
        )
        btn_web.pack(fill="x")

        # 2. CONTAINER KONTEN (Kanan)
        self.content_area = tk.Frame(self, bg=THEME["bg_root"], padx=24, pady=20)
        self.content_area.pack(side="right", fill="both", expand=True)

        self.current_frame = None

    def navigasi_ke(self, view_name):
        # Update warna tombol navigasi aktif
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(bg=THEME["primary"], fg="#FFFFFF")
            else:
                btn.configure(bg=THEME["bg_sidebar"], fg=THEME["text_secondary"])

        # Hancurkan frame lama jika ada
        if self.current_frame is not None:
            self.current_frame.destroy()

        # Update mini saldo di sidebar
        self.update_sidebar_balance()

        # Render view baru
        if view_name == "dashboard":
            self.current_frame = DashboardView(self.content_area, self)
        elif view_name == "catat":
            self.current_frame = CatatView(self.content_area, self)
        elif view_name == "riwayat":
            self.current_frame = RiwayatView(self.content_area, self)
        elif view_name == "analisis":
            self.current_frame = AnalisisView(self.content_area, self)
        elif view_name == "anggaran":
            self.current_frame = AnggaranView(self.content_area, self)

        self.current_frame.pack(fill="both", expand=True)

    def update_sidebar_balance(self):
        initial = self.data.get("initial_balance", 0)
        total_pemasukan = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "pemasukan")
        total_pengeluaran = sum(t["amount"] for t in self.data["transactions"] if t["type"] == "pengeluaran")
        saldo = initial + total_pemasukan - total_pengeluaran
        self.side_balance_val.configure(text=format_rupiah(saldo))
        if saldo >= 0:
            self.side_balance_val.configure(fg=THEME["balance"])
        else:
            self.side_balance_val.configure(fg=THEME["expense"])

    def buka_versi_web(self):
        if os.path.exists(WEB_FILE):
            webbrowser.open(f"file:///{WEB_FILE}")
        else:
            messagebox.showinfo("Latipuy Web", f"File latipuy_web.html akan segera dibuat di:\n{WEB_FILE}")

    def refresh_semua(self):
        self.data = DataManager.load_data()
        self.update_sidebar_balance()


# ==============================================================================
# VIEW 1: DASHBOARD
# ==============================================================================
class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_root"])
        self.controller = controller
        self.render()

    def get_monthly_summary(self, month, year):
        txs = self.controller.data["transactions"]
        pemasukan = 0
        pengeluaran = 0

        for t in txs:
            try:
                dt = datetime.strptime(t["date"], "%Y-%m-%d")
                if dt.month == int(month) and dt.year == int(year):
                    if t["type"] == "pemasukan":
                        pemasukan += t["amount"]
                    else:
                        pengeluaran += t["amount"]
            except Exception:
                continue

        saldo = pemasukan - pengeluaran
        return pemasukan, pengeluaran, saldo

    def render(self):
        # Header + Filter Bar
        header = tk.Frame(self, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 16))

        title_box = tk.Frame(header, bg=THEME["bg_root"])
        title_box.pack(side="left")

        lbl_t = tk.Label(title_box, text="Ringkasan Finansial Bulanan", font=("Segoe UI", 18, "bold"),
                         bg=THEME["bg_root"], fg=THEME["text_primary"])
        lbl_t.pack(anchor="w")

        lbl_s = tk.Label(title_box, text="Pantau arus kas, pengeluaran, dan kesehatan finansial Anda",
                         font=("Segoe UI", 9), bg=THEME["bg_root"], fg=THEME["text_muted"])
        lbl_s.pack(anchor="w", pady=(2, 0))

        # Filter Bulan & Tahun
        filter_box = tk.Frame(header, bg=THEME["bg_root"])
        filter_box.pack(side="right")

        tk.Label(filter_box, text="Bulan:", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_secondary"]).pack(side="left", padx=(0, 4))
        
        bulan_cb = ttk.Combobox(filter_box, width=12, state="readonly",
                                values=[f"{i+1} - {m}" for i, m in enumerate(NAMA_BULAN)])
        bulan_idx = int(self.controller.filter_bulan.get()) - 1
        bulan_cb.current(max(0, min(bulan_idx, 11)))
        bulan_cb.pack(side="left", padx=(0, 8))

        tk.Label(filter_box, text="Tahun:", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_secondary"]).pack(side="left", padx=(0, 4))
        
        years = [str(y) for y in range(datetime.now().year - 3, datetime.now().year + 3)]
        tahun_cb = ttk.Combobox(filter_box, width=7, state="readonly", values=years)
        if self.controller.filter_tahun.get() in years:
            tahun_cb.set(self.controller.filter_tahun.get())
        else:
            tahun_cb.set(str(datetime.now().year))
        tahun_cb.pack(side="left", padx=(0, 8))

        def on_filter_change(event=None):
            val_b = bulan_cb.get().split(" - ")[0]
            self.controller.filter_bulan.set(val_b)
            self.controller.filter_tahun.set(tahun_cb.get())
            self.destroy()
            self.__init__(self.master, self.controller)
            self.pack(fill="both", expand=True)

        bulan_cb.bind("<<ComboboxSelected>>", on_filter_change)
        tahun_cb.bind("<<ComboboxSelected>>", on_filter_change)

        # Hitung angka bulan terpilih
        m = self.controller.filter_bulan.get()
        y = self.controller.filter_tahun.get()
        pemasukan, pengeluaran, saldo = self.get_monthly_summary(m, y)
        budget = self.controller.data.get("budget", 3000000)

        # 3 KARTU STATISTIK MODERN
        cards_frame = tk.Frame(self, bg=THEME["bg_root"])
        cards_frame.pack(fill="x", pady=(0, 16))
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="card")

        # Card 1: Pemasukan
        self.create_stat_card(cards_frame, 0, "TOTAL PEMASUKAN", format_rupiah(pemasukan),
                              "🟢 Pemasukan Bulan Ini", THEME["income"], "📈")
        # Card 2: Pengeluaran
        self.create_stat_card(cards_frame, 1, "TOTAL PENGELUARAN", format_rupiah(pengeluaran),
                              "🔴 Pengeluaran Bulan Ini", THEME["expense"], "📉")
        # Card 3: Saldo
        saldo_col = THEME["balance"] if saldo >= 0 else THEME["expense"]
        self.create_stat_card(cards_frame, 2, "SISA SALDO BERSIH", format_rupiah(saldo),
                              "💎 Saldo Akhir Periode", saldo_col, "💰")

        # BUDGET PROGRESS BAR & STATUS FINANSIAL
        budget_card = tk.Frame(self, bg=THEME["bg_card"], padx=18, pady=14,
                               highlightbackground=THEME["border"], highlightthickness=1)
        budget_card.pack(fill="x", pady=(0, 16))

        b_head = tk.Frame(budget_card, bg=THEME["bg_card"])
        b_head.pack(fill="x")

        tk.Label(b_head, text="🎯 Penggunaan Anggaran Bulanan", font=("Segoe UI", 11, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left")

        persen_pakai = (pengeluaran / budget * 100) if budget > 0 else 0
        status_txt = f"{persen_pakai:.1f}% dari Target {format_rupiah(budget)}"
        status_color = THEME["income"] if persen_pakai < 70 else (THEME["warning"] if persen_pakai <= 100 else THEME["expense"])
        
        tk.Label(b_head, text=status_txt, font=("Segoe UI", 10, "bold"),
                 bg=THEME["bg_card"], fg=status_color).pack(side="right")

        # Canvas Progress Bar Modern
        pb_canvas = tk.Canvas(budget_card, height=14, bg=THEME["bg_input"], bd=0, highlightthickness=0)
        pb_canvas.pack(fill="x", pady=(10, 6))

        def draw_progress(event):
            w = event.width
            fill_w = min(w, max(0, int(w * (persen_pakai / 100))))
            pb_canvas.delete("all")
            # Background bar
            pb_canvas.create_rectangle(0, 0, w, 14, fill=THEME["bg_input"], outline="")
            # Filled bar
            if fill_w > 0:
                pb_canvas.create_rectangle(0, 0, fill_w, 14, fill=status_color, outline="")

        pb_canvas.bind("<Configure>", draw_progress)

        # BAGIAN BAWAH: 2 KOLOM (5 Transaksi Terakhir & Tips Finansial)
        bottom_grid = tk.Frame(self, bg=THEME["bg_root"])
        bottom_grid.pack(fill="both", expand=True)
        bottom_grid.columnconfigure(0, weight=3)
        bottom_grid.columnconfigure(1, weight=2)

        # Kolom Kiri: 5 Transaksi Terakhir
        tx_box = tk.Frame(bottom_grid, bg=THEME["bg_card"], padx=16, pady=14,
                          highlightbackground=THEME["border"], highlightthickness=1)
        tx_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tx_head = tk.Frame(tx_box, bg=THEME["bg_card"])
        tx_head.pack(fill="x", pady=(0, 10))

        tk.Label(tx_head, text="⏱️ Transaksi Terkini", font=("Segoe UI", 11, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left")

        btn_more = tk.Button(tx_head, text="Lihat Semua →", font=("Segoe UI", 8, "bold"),
                             bg=THEME["bg_card"], fg=THEME["primary"], bd=0, relief="flat", cursor="hand2",
                             command=lambda: self.controller.navigasi_ke("riwayat"))
        btn_more.pack(side="right")

        recent_txs = sorted(self.controller.data["transactions"], key=lambda x: x.get("date", ""), reverse=True)[:5]

        if not recent_txs:
            tk.Label(tx_box, text="Belum ada transaksi yang dicatat.\nKlik tombol 'Catat Transaksi' untuk memulai!",
                     font=("Segoe UI", 9), bg=THEME["bg_card"], fg=THEME["text_muted"], pady=30).pack()
        else:
            for item in recent_txs:
                row = tk.Frame(tx_box, bg=THEME["bg_card"], pady=6)
                row.pack(fill="x")

                icon = "🟢" if item["type"] == "pemasukan" else "🔴"
                cat = item.get("category", "Lainnya")
                desc = item.get("description") or cat
                date = item.get("date", "")
                amt = item.get("amount", 0)

                left_info = tk.Frame(row, bg=THEME["bg_card"])
                left_info.pack(side="left")

                tk.Label(left_info, text=f"{icon}  {desc}", font=("Segoe UI", 9, "bold"),
                         bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w")
                tk.Label(left_info, text=f"{cat} • {date}", font=("Segoe UI", 8),
                         bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w")

                val_color = THEME["income"] if item["type"] == "pemasukan" else THEME["expense"]
                sign = "+" if item["type"] == "pemasukan" else "-"
                tk.Label(row, text=f"{sign}{format_rupiah(amt)}", font=("Segoe UI", 9, "bold"),
                         bg=THEME["bg_card"], fg=val_color).pack(side="right")

                sep_r = tk.Frame(tx_box, bg=THEME["border"], height=1)
                sep_r.pack(fill="x", pady=2)

        # Kolom Kanan: Status & Tips
        tips_box = tk.Frame(bottom_grid, bg=THEME["bg_card"], padx=16, pady=14,
                            highlightbackground=THEME["border"], highlightthickness=1)
        tips_box.grid(row=0, column=1, sticky="nsew")

        tk.Label(tips_box, text="💡 Analisis Finansial Cepat", font=("Segoe UI", 11, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w", pady=(0, 10))

        # Analisis rasio tabungan
        if pemasukan > 0:
            rasio_tabung = ((pemasukan - pengeluaran) / pemasukan) * 100
            if rasio_tabung >= 30:
                kondisi = "🌟 Sangat Sehat (Tabungan > 30%)"
                pesan = "Pertahankan! Anda berhasil menyisihkan sebagian besar pemasukan Anda untuk masa depan."
            elif rasio_tabung > 0:
                kondisi = "👍 Cukup Baik"
                pesan = "Pengeluaran masih di bawah pemasukan. Coba kurangi pengeluaran tersier agar tabungan bertambah."
            else:
                kondisi = "⚠️ Defisit (Pengeluaran > Pemasukan)"
                pesan = "Waspada! Pengeluaran Anda melebihi pemasukan bulan ini. Segera evaluasi kebutuhan pokok."
        else:
            kondisi = "ℹ️ Belum Ada Pemasukan"
            pesan = "Silakan catat pemasukan Anda bulan ini untuk melihat rasio tabungan yang akurat."

        card_k = tk.Frame(tips_box, bg=THEME["bg_input"], padx=12, pady=10,
                          highlightbackground=THEME["border"], highlightthickness=1)
        card_k.pack(fill="x", pady=(0, 10))

        tk.Label(card_k, text="Status Arus Kas:", font=("Segoe UI", 8, "bold"),
                 bg=THEME["bg_input"], fg=THEME["text_muted"]).pack(anchor="w")
        tk.Label(card_k, text=kondisi, font=("Segoe UI", 10, "bold"),
                 bg=THEME["bg_input"], fg=THEME["primary"]).pack(anchor="w", pady=(2, 0))

        tk.Label(tips_box, text=pesan, font=("Segoe UI", 9), wraplength=260, justify="left",
                 bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(anchor="w", pady=(0, 14))

        # Tombol aksi cepat
        btn_quick_add = tk.Button(tips_box, text="⚡ Catat Pengeluaran Baru", font=("Segoe UI", 9, "bold"),
                                  bg=THEME["primary"], fg="#FFFFFF", bd=0, relief="flat", pady=8, cursor="hand2",
                                  command=lambda: self.controller.navigasi_ke("catat"))
        btn_quick_add.pack(fill="x", pady=(6, 0))

    def create_stat_card(self, parent, col, title, value, subtext, color, icon):
        card = tk.Frame(parent, bg=THEME["bg_card"], padx=16, pady=16,
                        highlightbackground=THEME["border"], highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        head = tk.Frame(card, bg=THEME["bg_card"])
        head.pack(fill="x")

        tk.Label(head, text=title, font=("Segoe UI", 8, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(side="left")
        tk.Label(head, text=icon, font=("Segoe UI", 12),
                 bg=THEME["bg_card"]).pack(side="right")

        val_lbl = tk.Label(card, text=value, font=("Segoe UI", 16, "bold"),
                           bg=THEME["bg_card"], fg=color)
        val_lbl.pack(anchor="w", pady=(8, 2))

        sub_lbl = tk.Label(card, text=subtext, font=("Segoe UI", 8),
                           bg=THEME["bg_card"], fg=THEME["text_secondary"])
        sub_lbl.pack(anchor="w")


# ==============================================================================
# VIEW 2: CATAT TRANSAKSI BARU
# ==============================================================================
class CatatView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_root"])
        self.controller = controller

        self.tipe_transaksi = tk.StringVar(value="pengeluaran")
        self.render()

    def render(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 16))

        tk.Label(header, text="Catat Transaksi Finansial", font=("Segoe UI", 18, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(header, text="Masukkan detail pemasukan atau pengeluaran secara teratur",
                 font=("Segoe UI", 9), bg=THEME["bg_root"], fg=THEME["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Card Form Utama
        form_card = tk.Frame(self, bg=THEME["bg_card"], padx=28, pady=24,
                             highlightbackground=THEME["border"], highlightthickness=1)
        form_card.pack(fill="x", pady=(0, 16))

        # 1. Pilihan Tipe: Pemasukan / Pengeluaran (Toggle Modern)
        tk.Label(form_card, text="PILIH JENIS TRANSAKSI", font=("Segoe UI", 8, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 8))

        toggle_box = tk.Frame(form_card, bg=THEME["bg_card"])
        toggle_box.pack(fill="x", pady=(0, 18))

        self.btn_toggle_exp = tk.Button(
            toggle_box,
            text="🔴 Pengeluaran (Uang Keluar)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["expense"],
            fg="#FFFFFF",
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self.set_tipe("pengeluaran")
        )
        self.btn_toggle_exp.pack(side="left", padx=(0, 12))

        self.btn_toggle_inc = tk.Button(
            toggle_box,
            text="🟢 Pemasukan (Uang Masuk)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME["bg_input"],
            fg=THEME["text_secondary"],
            bd=0,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self.set_tipe("pemasukan")
        )
        self.btn_toggle_inc.pack(side="left")

        # 2. Input Fields Grid
        grid_f = tk.Frame(form_card, bg=THEME["bg_card"])
        grid_f.pack(fill="x")
        grid_f.columnconfigure((0, 1), weight=1, uniform="input_col")

        # Nominal (Rp)
        f_nom = tk.Frame(grid_f, bg=THEME["bg_card"])
        f_nom.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=8)
        tk.Label(f_nom, text="Nominal / Jumlah (Rp)*", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_nominal = tk.Entry(f_nom, font=("Segoe UI", 12), bg=THEME["bg_input"],
                                    fg=THEME["text_primary"], insertbackground=THEME["text_primary"],
                                    bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        self.ent_nominal.pack(fill="x", ipady=8, padx=1)
        self.ent_nominal.focus_set()

        # Kategori
        f_kat = tk.Frame(grid_f, bg=THEME["bg_card"])
        f_kat.grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=8)
        tk.Label(f_kat, text="Kategori*", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.cb_kategori = ttk.Combobox(f_kat, font=("Segoe UI", 11), state="readonly")
        self.cb_kategori.pack(fill="x", ipady=6)
        self.update_kategori_list()

        # Tanggal (YYYY-MM-DD)
        f_tgl = tk.Frame(grid_f, bg=THEME["bg_card"])
        f_tgl.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=8)
        
        tgl_head = tk.Frame(f_tgl, bg=THEME["bg_card"])
        tgl_head.pack(fill="x")
        tk.Label(tgl_head, text="Tanggal (YYYY-MM-DD)*", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left", pady=(0, 4))
        
        btn_hari_ini = tk.Button(tgl_head, text="Hari Ini", font=("Segoe UI", 7, "bold"),
                                 bg=THEME["primary"], fg="#FFFFFF", bd=0, relief="flat", cursor="hand2",
                                 command=self.set_hari_ini)
        btn_hari_ini.pack(side="right")

        self.ent_tanggal = tk.Entry(f_tgl, font=("Segoe UI", 11), bg=THEME["bg_input"],
                                    fg=THEME["text_primary"], insertbackground=THEME["text_primary"],
                                    bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        self.ent_tanggal.pack(fill="x", ipady=8, padx=1)
        self.set_hari_ini()

        # Catatan / Deskripsi
        f_desk = tk.Frame(grid_f, bg=THEME["bg_card"])
        f_desk.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=8)
        tk.Label(f_desk, text="Keterangan / Deskripsi (Opsional)", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w", pady=(0, 4))
        self.ent_deskripsi = tk.Entry(f_desk, font=("Segoe UI", 11), bg=THEME["bg_input"],
                                      fg=THEME["text_primary"], insertbackground=THEME["text_primary"],
                                      bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        self.ent_deskripsi.pack(fill="x", ipady=8, padx=1)

        # Tombol Simpan & Reset
        btn_box = tk.Frame(form_card, bg=THEME["bg_card"])
        btn_box.pack(fill="x", pady=(20, 6))

        btn_simpan = tk.Button(
            btn_box,
            text="💾  Simpan Transaksi ke Latipuy",
            font=("Segoe UI", 11, "bold"),
            bg=THEME["primary"],
            fg="#FFFFFF",
            activebackground=THEME["primary_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            padx=24,
            pady=12,
            cursor="hand2",
            command=self.simpan_transaksi
        )
        btn_simpan.pack(side="left", padx=(0, 10))

        btn_reset = tk.Button(
            btn_box,
            text="🔄  Reset Input",
            font=("Segoe UI", 10),
            bg=THEME["bg_input"],
            fg=THEME["text_secondary"],
            bd=0,
            relief="flat",
            padx=16,
            pady=12,
            cursor="hand2",
            command=self.reset_form
        )
        btn_reset.pack(side="left")

        # Pesan status feedback
        self.lbl_status = tk.Label(form_card, text="", font=("Segoe UI", 9, "bold"),
                                   bg=THEME["bg_card"], fg=THEME["income"])
        self.lbl_status.pack(anchor="w", pady=(10, 0))

    def set_tipe(self, tipe):
        self.tipe_transaksi.set(tipe)
        if tipe == "pengeluaran":
            self.btn_toggle_exp.configure(bg=THEME["expense"], fg="#FFFFFF")
            self.btn_toggle_inc.configure(bg=THEME["bg_input"], fg=THEME["text_secondary"])
        else:
            self.btn_toggle_inc.configure(bg=THEME["income"], fg="#FFFFFF")
            self.btn_toggle_exp.configure(bg=THEME["bg_input"], fg=THEME["text_secondary"])
        self.update_kategori_list()

    def update_kategori_list(self):
        if self.tipe_transaksi.get() == "pemasukan":
            self.cb_kategori.configure(values=KATEGORI_PEMASUKAN)
            self.cb_kategori.current(0)
        else:
            self.cb_kategori.configure(values=KATEGORI_PENGELUARAN)
            self.cb_kategori.current(0)

    def set_hari_ini(self):
        self.ent_tanggal.delete(0, tk.END)
        self.ent_tanggal.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def reset_form(self):
        self.ent_nominal.delete(0, tk.END)
        self.ent_deskripsi.delete(0, tk.END)
        self.set_hari_ini()
        self.update_kategori_list()
        self.lbl_status.configure(text="")

    def simpan_transaksi(self):
        raw_nominal = self.ent_nominal.get().strip().replace(".", "").replace(",", "")
        kategori = self.cb_kategori.get().strip()
        tanggal = self.ent_tanggal.get().strip()
        deskripsi = self.ent_deskripsi.get().strip()
        tipe = self.tipe_transaksi.get()

        # Validasi Nominal
        if not raw_nominal:
            messagebox.showwarning("Peringatan", "Harap isi nominal uang!")
            self.ent_nominal.focus_set()
            return

        try:
            nominal = float(raw_nominal)
            if nominal <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Peringatan", "Nominal harus berupa angka positif!")
            self.ent_nominal.focus_set()
            return

        # Validasi Tanggal
        try:
            dt = datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Peringatan", "Format tanggal harus YYYY-MM-DD (contoh: 2026-11-09)!")
            self.ent_tanggal.focus_set()
            return

        # Buat objek transaksi
        new_tx = {
            "id": f"tx_{int(datetime.now().timestamp()*1000)}",
            "type": tipe,
            "category": kategori,
            "amount": nominal,
            "date": tanggal,
            "description": deskripsi or kategori,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.controller.data["transactions"].append(new_tx)
        DataManager.save_data(self.controller.data)
        self.controller.refresh_semua()

        # Update status feedback
        tipe_teks = "Pemasukan" if tipe == "pemasukan" else "Pengeluaran"
        self.lbl_status.configure(
            text=f"✅ Berhasil! {tipe_teks} sebesar {format_rupiah(nominal)} untuk '{kategori}' tersimpan.",
            fg=THEME["income"] if tipe == "pemasukan" else THEME["warning"]
        )

        # Reset field nominal & deskripsi
        self.ent_nominal.delete(0, tk.END)
        self.ent_deskripsi.delete(0, tk.END)
        self.ent_nominal.focus_set()


# ==============================================================================
# VIEW 3: RIWAYAT & LAPORAN TRANSAKSI
# ==============================================================================
class RiwayatView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_root"])
        self.controller = controller
        self.render()

    def render(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 14))

        title_box = tk.Frame(header, bg=THEME["bg_root"])
        title_box.pack(side="left")

        tk.Label(title_box, text="Riwayat Transaksi & Laporan", font=("Segoe UI", 18, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(title_box, text="Cari, filter, hapus, atau ekspor data keuangan Anda",
                 font=("Segoe UI", 9), bg=THEME["bg_root"], fg=THEME["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Tombol Ekspor CSV
        btn_ekspor = tk.Button(
            header,
            text="📥  Ekspor ke CSV",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            activebackground=THEME["bg_card_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            highlightbackground=THEME["border"],
            highlightthickness=1,
            command=self.ekspor_csv
        )
        btn_ekspor.pack(side="right")

        # FILTER BAR
        filter_card = tk.Frame(self, bg=THEME["bg_card"], padx=14, pady=10,
                               highlightbackground=THEME["border"], highlightthickness=1)
        filter_card.pack(fill="x", pady=(0, 12))

        # Cari
        tk.Label(filter_card, text="🔍", font=("Segoe UI", 10),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(side="left", padx=(0, 4))
        
        ent_search = tk.Entry(filter_card, textvariable=self.controller.search_query,
                              font=("Segoe UI", 10), bg=THEME["bg_input"], fg=THEME["text_primary"],
                              insertbackground=THEME["text_primary"], width=22, bd=0,
                              highlightbackground=THEME["border"], highlightthickness=1)
        ent_search.pack(side="left", ipady=4, padx=(0, 14))
        ent_search.bind("<KeyRelease>", lambda e: self.muat_tabel())

        # Filter Tipe
        tk.Label(filter_card, text="Tipe:", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(side="left", padx=(0, 4))
        
        cb_tipe = ttk.Combobox(filter_card, width=11, state="readonly", values=["Semua", "Pemasukan", "Pengeluaran"])
        cb_tipe.set(self.controller.filter_tipe.get())
        cb_tipe.pack(side="left", padx=(0, 14))
        cb_tipe.bind("<<ComboboxSelected>>", lambda e: self.on_tipe_changed(cb_tipe.get()))

        # Filter Bulan
        tk.Label(filter_card, text="Bulan:", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(side="left", padx=(0, 4))
        
        cb_bulan = ttk.Combobox(filter_card, width=13, state="readonly",
                                values=["Semua Bulan"] + [f"{i+1} - {m}" for i, m in enumerate(NAMA_BULAN)])
        cb_bulan.set(f"{self.controller.filter_bulan.get()} - {NAMA_BULAN[int(self.controller.filter_bulan.get())-1]}")
        cb_bulan.pack(side="left", padx=(0, 14))

        # Filter Tahun
        tk.Label(filter_card, text="Tahun:", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(side="left", padx=(0, 4))
        
        years = ["Semua Tahun"] + [str(y) for y in range(datetime.now().year - 3, datetime.now().year + 3)]
        cb_tahun = ttk.Combobox(filter_card, width=11, state="readonly", values=years)
        cb_tahun.set(self.controller.filter_tahun.get())
        cb_tahun.pack(side="left", padx=(0, 14))

        def on_date_filter_change(event=None):
            b_val = cb_bulan.get()
            t_val = cb_tahun.get()
            if b_val == "Semua Bulan":
                self.controller.filter_bulan.set("semua")
            else:
                self.controller.filter_bulan.set(b_val.split(" - ")[0])
            self.controller.filter_tahun.set(t_val)
            self.muat_tabel()

        cb_bulan.bind("<<ComboboxSelected>>", on_date_filter_change)
        cb_tahun.bind("<<ComboboxSelected>>", on_date_filter_change)

        # TABEL TREEVIEW MODERN
        table_frame = tk.Frame(self, bg=THEME["bg_card"],
                               highlightbackground=THEME["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "tanggal", "tipe", "kategori", "deskripsi", "nominal")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("tipe", text="Tipe")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("deskripsi", text="Keterangan / Deskripsi")
        self.tree.heading("nominal", text="Nominal")

        self.tree.column("id", width=0, stretch=False)
        self.tree.column("tanggal", width=100, anchor="center")
        self.tree.column("tipe", width=110, anchor="center")
        self.tree.column("kategori", width=160, anchor="w")
        self.tree.column("deskripsi", width=280, anchor="w")
        self.tree.column("nominal", width=150, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tags untuk warna baris pemasukan/pengeluaran
        self.tree.tag_configure("inc_row", foreground=THEME["income"])
        self.tree.tag_configure("exp_row", foreground=THEME["expense"])

        # BOTTOM BAR (Total & Action Hapus)
        bottom_bar = tk.Frame(self, bg=THEME["bg_root"], pady=10)
        bottom_bar.pack(fill="x")

        btn_hapus = tk.Button(
            bottom_bar,
            text="🗑️  Hapus Transaksi Terpilih",
            font=("Segoe UI", 9, "bold"),
            bg="#991B1B",
            fg="#FFFFFF",
            activebackground="#7F1D1D",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.hapus_transaksi
        )
        btn_hapus.pack(side="left")

        self.lbl_total_filter = tk.Label(
            bottom_bar,
            text="Total Ditemukan: 0 Transaksi",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["text_secondary"]
        )
        self.lbl_total_filter.pack(side="right")

        # Muat isi tabel awal
        self.muat_tabel()

    def on_tipe_changed(self, val):
        self.controller.filter_tipe.set(val)
        self.muat_tabel()

    def muat_tabel(self):
        # Bersihkan tabel
        for item in self.tree.get_children():
            self.tree.delete(item)

        txs = self.controller.data["transactions"]
        query = self.controller.search_query.get().strip().lower()
        tipe_filter = self.controller.filter_tipe.get()
        bulan_filter = self.controller.filter_bulan.get()
        tahun_filter = self.controller.filter_tahun.get()

        filtered_count = 0
        total_p = 0
        total_e = 0

        # Urutkan dari yang terbaru
        sorted_txs = sorted(txs, key=lambda x: x.get("date", ""), reverse=True)

        for t in sorted_txs:
            # Filter Tipe
            if tipe_filter == "Pemasukan" and t["type"] != "pemasukan":
                continue
            if tipe_filter == "Pengeluaran" and t["type"] != "pengeluaran":
                continue

            # Filter Tanggal
            tgl = t.get("date", "")
            try:
                dt = datetime.strptime(tgl, "%Y-%m-%d")
                if bulan_filter != "semua" and dt.month != int(bulan_filter):
                    continue
                if tahun_filter != "Semua Tahun" and dt.year != int(tahun_filter):
                    continue
            except Exception:
                pass

            # Filter Kata Kunci
            desk = t.get("description", "").lower()
            kat = t.get("category", "").lower()
            if query and (query not in desk and query not in kat):
                continue

            filtered_count += 1
            amt = t.get("amount", 0)
            if t["type"] == "pemasukan":
                total_p += amt
                tipe_str = "🟢 Pemasukan"
                nominal_str = f"+ {format_rupiah(amt)}"
                tag = "inc_row"
            else:
                total_e += amt
                tipe_str = "🔴 Pengeluaran"
                nominal_str = f"- {format_rupiah(amt)}"
                tag = "exp_row"

            self.tree.insert(
                "",
                "end",
                values=(t.get("id"), tgl, tipe_str, t.get("category"), t.get("description"), nominal_str),
                tags=(tag,)
            )

        self.lbl_total_filter.configure(
            text=f"Total: {filtered_count} Transaksi  |  + {format_rupiah(total_p)}  |  - {format_rupiah(total_e)}  |  Net: {format_rupiah(total_p - total_e)}"
        )

    def hapus_transaksi(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus terlebih dahulu!")
            return

        item = self.tree.item(selected[0])
        tx_id = item["values"][0]
        desc = item["values"][4]
        nom = item["values"][5]

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus transaksi ini?\n\nKeterangan: {desc}\nNominal: {nom}"
        )
        if konfirmasi:
            self.controller.data["transactions"] = [
                t for t in self.controller.data["transactions"] if t.get("id") != tx_id
            ]
            DataManager.save_data(self.controller.data)
            self.controller.refresh_semua()
            self.muat_tabel()
            messagebox.showinfo("Berhasil", "Transaksi berhasil dihapus dari Latipuy.")

    def ekspor_csv(self):
        txs = self.controller.data["transactions"]
        if not txs:
            messagebox.showwarning("Perhatian", "Belum ada transaksi untuk diekspor!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Semua File", "*.*")],
            title="Simpan Laporan Transaksi Latipuy"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Tanggal", "Tipe", "Kategori", "Deskripsi", "Nominal (Rp)", "Dibuat Pada"])
                for t in txs:
                    writer.writerow([
                        t.get("id"),
                        t.get("date"),
                        t.get("type"),
                        t.get("category"),
                        t.get("description"),
                        t.get("amount"),
                        t.get("created_at")
                    ])
            messagebox.showinfo("Sukses", f"Data transaksi berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor file: {e}")


# ==============================================================================
# VIEW 4: ANALISIS & GRAFIK (CANVAS VISUALIZATION)
# ==============================================================================
class AnalisisView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_root"])
        self.controller = controller
        self.render()

    def render(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 14))

        tk.Label(header, text="Visualisasi Grafik & Analisis", font=("Segoe UI", 18, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(header, text="Distribusi pengeluaran per kategori & tren arus kas",
                 font=("Segoe UI", 9), bg=THEME["bg_root"], fg=THEME["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Kontainer 2 Kolom Grafik
        charts_container = tk.Frame(self, bg=THEME["bg_root"])
        charts_container.pack(fill="both", expand=True)
        charts_container.columnconfigure((0, 1), weight=1, uniform="charts")

        # 1. Kolom Kiri: Donut / Pie Chart Pengeluaran Per Kategori
        box_pie = tk.Frame(charts_container, bg=THEME["bg_card"], padx=16, pady=14,
                           highlightbackground=THEME["border"], highlightthickness=1)
        box_pie.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(box_pie, text="📊 Pengeluaran per Kategori", font=("Segoe UI", 11, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(box_pie, text="Lihat pos pengeluaran terbesar Anda", font=("Segoe UI", 8),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 8))

        self.canvas_pie = tk.Canvas(box_pie, bg=THEME["bg_card"], bd=0, highlightthickness=0)
        self.canvas_pie.pack(fill="both", expand=True)
        self.canvas_pie.bind("<Configure>", lambda e: self.draw_pie_chart())

        # 2. Kolom Kanan: Bar Chart Pemasukan vs Pengeluaran 6 Bulan Terakhir
        box_bar = tk.Frame(charts_container, bg=THEME["bg_card"], padx=16, pady=14,
                           highlightbackground=THEME["border"], highlightthickness=1)
        box_bar.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(box_bar, text="📈 Perbandingan 6 Bulan Terakhir", font=("Segoe UI", 11, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(box_bar, text="🟢 Pemasukan vs 🔴 Pengeluaran bulanan", font=("Segoe UI", 8),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w", pady=(0, 8))

        self.canvas_bar = tk.Canvas(box_bar, bg=THEME["bg_card"], bd=0, highlightthickness=0)
        self.canvas_bar.pack(fill="both", expand=True)
        self.canvas_bar.bind("<Configure>", lambda e: self.draw_bar_chart())

    def draw_pie_chart(self):
        self.canvas_pie.delete("all")
        w = self.canvas_pie.winfo_width()
        h = self.canvas_pie.winfo_height()
        if w < 50 or h < 50:
            return

        # Hitung total pengeluaran per kategori
        kategori_totals = {}
        for t in self.controller.data["transactions"]:
            if t["type"] == "pengeluaran":
                kat = t.get("category", "Lainnya")
                kategori_totals[kat] = kategori_totals.get(kat, 0) + t.get("amount", 0)

        total_pengeluaran = sum(kategori_totals.values())

        if total_pengeluaran == 0:
            self.canvas_pie.create_text(
                w / 2, h / 2,
                text="Belum ada data pengeluaran\nuntuk divisualisasikan",
                fill=THEME["text_muted"],
                font=("Segoe UI", 10),
                justify="center"
            )
            return

        # Donut Chart parameters
        cx = w * 0.35
        cy = h * 0.5
        radius = min(cx * 0.8, cy * 0.8, 110)
        inner_radius = radius * 0.55

        start_angle = 0
        sorted_kats = sorted(kategori_totals.items(), key=lambda x: x[1], reverse=True)

        legend_y = 20
        legend_x = w * 0.65

        for idx, (kat, amt) in enumerate(sorted_kats):
            persen = (amt / total_pengeluaran) * 100
            extent = (amt / total_pengeluaran) * 360
            color = CHART_COLORS[idx % len(CHART_COLORS)]

            # Gambar slice luar
            self.canvas_pie.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_angle, extent=extent,
                fill=color, outline=THEME["bg_card"], width=2
            )
            start_angle += extent

            # Gambar legenda di samping kanan jika masih muat
            if legend_y + 18 < h:
                self.canvas_pie.create_oval(
                    legend_x, legend_y + 2, legend_x + 10, legend_y + 12,
                    fill=color, outline=""
                )
                self.canvas_pie.create_text(
                    legend_x + 16, legend_y + 6,
                    text=f"{kat} ({persen:.1f}%)",
                    fill=THEME["text_secondary"],
                    font=("Segoe UI", 8),
                    anchor="w"
                )
                legend_y += 20

        # Donut hole (lingkaran tengah)
        self.canvas_pie.create_oval(
            cx - inner_radius, cy - inner_radius, cx + inner_radius, cy + inner_radius,
            fill=THEME["bg_card"], outline=""
        )
        self.canvas_pie.create_text(
            cx, cy - 8,
            text="TOTAL",
            fill=THEME["text_muted"],
            font=("Segoe UI", 7, "bold")
        )
        self.canvas_pie.create_text(
            cx, cy + 8,
            text=format_rupiah(total_pengeluaran),
            fill=THEME["text_primary"],
            font=("Segoe UI", 8, "bold")
        )

    def draw_bar_chart(self):
        self.canvas_bar.delete("all")
        w = self.canvas_bar.winfo_width()
        h = self.canvas_bar.winfo_height()
        if w < 50 or h < 50:
            return

        # 6 Bulan Terakhir
        now = datetime.now()
        months = []
        for i in range(5, -1, -1):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            months.append((m, y))

        data_per_month = []
        max_val = 1000

        for m, y in months:
            inc = 0
            exp = 0
            for t in self.controller.data["transactions"]:
                try:
                    dt = datetime.strptime(t.get("date", ""), "%Y-%m-%d")
                    if dt.month == m and dt.year == y:
                        if t["type"] == "pemasukan":
                            inc += t["amount"]
                        else:
                            exp += t["amount"]
                except Exception:
                    pass
            data_per_month.append((f"{NAMA_BULAN[m-1][:3]}", inc, exp))
            max_val = max(max_val, inc, exp)

        # Gambar Batang Grafik
        margin_b = 30
        margin_t = 20
        margin_l = 20
        margin_r = 20
        chart_h = h - margin_b - margin_t
        slot_w = (w - margin_l - margin_r) / len(data_per_month)
        bar_w = slot_w * 0.32

        # Baseline horizontal
        self.canvas_bar.create_line(
            margin_l, h - margin_b, w - margin_r, h - margin_b,
            fill=THEME["border"], width=1
        )

        for i, (label, inc, exp) in enumerate(data_per_month):
            cx = margin_l + (i + 0.5) * slot_w

            # Bar Pemasukan (Hijau)
            h_inc = (inc / max_val) * (chart_h - 10) if max_val > 0 else 0
            x1_inc = cx - bar_w - 2
            y1_inc = (h - margin_b) - h_inc
            x2_inc = cx - 2
            y2_inc = h - margin_b
            self.canvas_bar.create_rectangle(
                x1_inc, y1_inc, x2_inc, y2_inc,
                fill=THEME["income"], outline=""
            )

            # Bar Pengeluaran (Merah)
            h_exp = (exp / max_val) * (chart_h - 10) if max_val > 0 else 0
            x1_exp = cx + 2
            y1_exp = (h - margin_b) - h_exp
            x2_exp = cx + bar_w + 2
            y2_exp = h - margin_b
            self.canvas_bar.create_rectangle(
                x1_exp, y1_exp, x2_exp, y2_exp,
                fill=THEME["expense"], outline=""
            )

            # Label Nama Bulan di Bawah
            self.canvas_bar.create_text(
                cx, h - margin_b + 14,
                text=label,
                fill=THEME["text_secondary"],
                font=("Segoe UI", 8)
            )


# ==============================================================================
# VIEW 5: TARGET ANGGARAN & PENGATURAN
# ==============================================================================
class AnggaranView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME["bg_root"])
        self.controller = controller
        self.render()

    def render(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 16))

        tk.Label(header, text="Target Anggaran & Pengaturan", font=("Segoe UI", 18, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(header, text="Tentukan batas pengeluaran bulanan dan kelola data aplikasi",
                 font=("Segoe UI", 9), bg=THEME["bg_root"], fg=THEME["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Card Saldo Awal
        card_init = tk.Frame(self, bg=THEME["bg_card"], padx=24, pady=20,
                             highlightbackground=THEME["border"], highlightthickness=1)
        card_init.pack(fill="x", pady=(0, 16))

        tk.Label(card_init, text="💵 SALDO AWAL (MODAL / UANG SAAT INI)", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["balance"]).pack(anchor="w")
        tk.Label(card_init, text="Tentukan saldo uang awal di rekening/dompet Anda sebelum mulai mencatat.",
                 font=("Segoe UI", 8), bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(anchor="w", pady=(2, 12))

        f_init_in = tk.Frame(card_init, bg=THEME["bg_card"])
        f_init_in.pack(fill="x")

        tk.Label(f_init_in, text="Saldo Awal Rekening (Rp):", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left", padx=(0, 10))

        current_init = self.controller.data.get("initial_balance", 0)
        self.ent_initial = tk.Entry(f_init_in, font=("Segoe UI", 11), bg=THEME["bg_input"],
                                    fg=THEME["text_primary"], insertbackground=THEME["text_primary"],
                                    width=18, bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        self.ent_initial.insert(0, f"{int(current_init):,}".replace(",", ".") if current_init else "0")
        self.ent_initial.pack(side="left", ipady=6, padx=(0, 12))

        btn_save_init = tk.Button(
            f_init_in,
            text="Simpan Saldo Awal",
            font=("Segoe UI", 9, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.simpan_saldo_awal
        )
        btn_save_init.pack(side="left")

        # Card Target Anggaran
        card_b = tk.Frame(self, bg=THEME["bg_card"], padx=24, pady=20,
                          highlightbackground=THEME["border"], highlightthickness=1)
        card_b.pack(fill="x", pady=(0, 16))

        tk.Label(card_b, text="🎯 TARGET ANGGARAN PENGELUARAN BULANAN", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["primary"]).pack(anchor="w")
        tk.Label(card_b, text="Latipuy akan mengingatkan Anda jika pengeluaran bulanan mendekati atau melebihi batas ini.",
                 font=("Segoe UI", 8), bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(anchor="w", pady=(2, 12))

        f_input = tk.Frame(card_b, bg=THEME["bg_card"])
        f_input.pack(fill="x")

        tk.Label(f_input, text="Batas Maksimal Pengeluaran (Rp):", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left", padx=(0, 10))

        current_budget = self.controller.data.get("budget", 3000000)
        self.ent_budget = tk.Entry(f_input, font=("Segoe UI", 11), bg=THEME["bg_input"],
                                   fg=THEME["text_primary"], insertbackground=THEME["text_primary"],
                                   width=18, bd=0, highlightbackground=THEME["border"], highlightthickness=1)
        self.ent_budget.insert(0, f"{int(current_budget):,}".replace(",", "."))
        self.ent_budget.pack(side="left", ipady=6, padx=(0, 12))

        btn_save_b = tk.Button(
            f_input,
            text="Simpan Anggaran",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["primary"],
            fg="#FFFFFF",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.simpan_anggaran
        )
        btn_save_b.pack(side="left")

        # Card Pengaturan Data & Reset
        card_d = tk.Frame(self, bg=THEME["bg_card"], padx=24, pady=20,
                          highlightbackground=THEME["border"], highlightthickness=1)
        card_d.pack(fill="x")

        tk.Label(card_d, text="⚙️ MANAJEMEN DATA", font=("Segoe UI", 9, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(anchor="w")
        
        info_txt = f"Lokasi Penyimpanan File: {DATA_FILE}\nJumlah Transaksi Tercatat: {len(self.controller.data['transactions'])}"
        tk.Label(card_d, text=info_txt, font=("Segoe UI", 8), justify="left",
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(anchor="w", pady=(4, 14))

        btn_box = tk.Frame(card_d, bg=THEME["bg_card"])
        btn_box.pack(fill="x")

        btn_contoh = tk.Button(
            btn_box,
            text="📥 Muat Data Contoh (Demo)",
            font=("Segoe UI", 9, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            bd=0,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.muat_data_contoh
        )
        btn_contoh.pack(side="left", padx=(0, 10))

        btn_reset_all = tk.Button(
            btn_box,
            text="⚠️ Hapus Semua Data",
            font=("Segoe UI", 9, "bold"),
            bg="#991B1B",
            fg="#FFFFFF",
            bd=0,
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.reset_semua_data
        )
        btn_reset_all.pack(side="left")

    def simpan_saldo_awal(self):
        raw = self.ent_initial.get().strip().replace(".", "").replace(",", "")
        try:
            val = float(raw) if raw else 0
            if val < 0:
                raise ValueError()
            self.controller.data["initial_balance"] = val
            DataManager.save_data(self.controller.data)
            self.controller.refresh_semua()
            messagebox.showinfo("Berhasil", f"Saldo awal berhasil diperbarui menjadi {format_rupiah(val)}!")
        except ValueError:
            messagebox.showwarning("Peringatan", "Harap masukkan angka saldo awal yang valid!")

    def simpan_anggaran(self):
        raw = self.ent_budget.get().strip().replace(".", "").replace(",", "")
        try:
            val = float(raw)
            if val <= 0:
                raise ValueError()
            self.controller.data["budget"] = val
            DataManager.save_data(self.controller.data)
            messagebox.showinfo("Berhasil", f"Target anggaran bulanan berhasil diperbarui menjadi {format_rupiah(val)}!")
        except ValueError:
            messagebox.showwarning("Peringatan", "Harap masukkan angka anggaran yang valid!")

    def muat_data_contoh(self):
        konfirmasi = messagebox.askyesno(
            "Muat Data Demo",
            "Apakah Anda ingin menambahkan data contoh transaksi untuk simulasi Latipuy?"
        )
        if not konfirmasi:
            return

        today = datetime.now()
        sample_txs = [
            {"id": "tx_sample_1", "type": "pemasukan", "category": "Gaji Pokok", "amount": 7500000,
             "date": today.strftime("%Y-%m-01"), "description": "Gaji Bulanan", "created_at": str(today)},
            {"id": "tx_sample_2", "type": "pemasukan", "category": "Freelance / Side Job", "amount": 1800000,
             "date": today.strftime("%Y-%m-05"), "description": "Desain UI Proyek", "created_at": str(today)},
            {"id": "tx_sample_3", "type": "pengeluaran", "category": "Sewa / Kost / Rumah", "amount": 1750000,
             "date": today.strftime("%Y-%m-02"), "description": "Bayar Kost Bulanan", "created_at": str(today)},
            {"id": "tx_sample_4", "type": "pengeluaran", "category": "Makanan & Minuman", "amount": 650000,
             "date": today.strftime("%Y-%m-03"), "description": "Belanja Mingguan & Makan", "created_at": str(today)},
            {"id": "tx_sample_5", "type": "pengeluaran", "category": "Tagihan & Listrik / Air", "amount": 350000,
             "date": today.strftime("%Y-%m-04"), "description": "Token Listrik & WiFi", "created_at": str(today)},
            {"id": "tx_sample_6", "type": "pengeluaran", "category": "Transportasi & Bensin", "amount": 200000,
             "date": today.strftime("%Y-%m-06"), "description": "Isi Bensin Motor & Kereta", "created_at": str(today)},
            {"id": "tx_sample_7", "type": "pengeluaran", "category": "Hiburan & Liburan", "amount": 250000,
             "date": today.strftime("%Y-%m-07"), "description": "Nonton Bioskop & Kopi", "created_at": str(today)},
        ]

        self.controller.data["transactions"].extend(sample_txs)
        DataManager.save_data(self.controller.data)
        self.controller.refresh_semua()
        messagebox.showinfo("Sukses", "Data contoh berhasil ditambahkan! Silakan cek menu Dashboard.")

    def reset_semua_data(self):
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus Semua",
            "⚠️ PERHATIAN:\nSemua riwayat transaksi akan dihapus permanen. Lanjutkan?"
        )
        if konfirmasi:
            self.controller.data = {"budget": 3000000, "transactions": []}
            DataManager.save_data(self.controller.data)
            self.controller.refresh_semua()
            messagebox.showinfo("Selesai", "Semua data transaksi Latipuy telah direset.")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = LatipuyApp()
    app.mainloop()

