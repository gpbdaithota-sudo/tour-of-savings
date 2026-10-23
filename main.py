import hashlib
import os
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw, ImageFilter, ImageFont


APP_ROOT = Path(__file__).resolve().parent
ASSET_DIR = APP_ROOT / "assets"
LOGO_PATH = ASSET_DIR / "logo.png"
DB_PATH = APP_ROOT / "tour_of_savings.db"


def ensure_assets_dir():
    ASSET_DIR.mkdir(exist_ok=True)


def draw_logo(path: Path):
    ensure_assets_dir()
    width, height = 1200, 1200
    img = Image.new("RGBA", (width, height), (16, 22, 30, 255))
    draw = ImageDraw.Draw(img)

    # Outer gold ring
    outer = (80, 80, 1120, 1120)
    ring_margin = 35
    ring_outer = (outer[0] + ring_margin, outer[1] + ring_margin, outer[2] - ring_margin, outer[3] - ring_margin)
    draw.ellipse(ring_outer, outline=(212, 175, 55, 255), width=26)
    draw.ellipse((120, 120, 1080, 1080), outline=(212, 175, 55, 180), width=10)

    # Inner navy circle
    inner_circle = (200, 200, 1000, 1000)
    draw.ellipse(inner_circle, fill=(18, 26, 38, 255), outline=(212, 175, 55, 255), width=8)

    # Character icon: hand holding savings bag
    bag_x1, bag_y1 = 440, 350
    bag_x2, bag_y2 = 770, 710
    draw.rounded_rectangle((bag_x1, bag_y1, bag_x2, bag_y2), radius=40, fill=(212, 175, 55, 255), outline=(212, 175, 55, 255))
    draw.rounded_rectangle((470, 300, 740, 390), radius=24, fill=(212, 175, 55, 255))
    draw.ellipse((540, 470, 670, 610), fill=(18, 26, 38, 255), outline=(18, 26, 38, 255))
    draw.text((590, 495), "$", fill=(212, 175, 55, 255), anchor="mm", font=ImageFont.truetype("DejaVuSans-Bold.ttf", 90))

    # hand shape
    hand_points = [
        (310, 540), (430, 500), (520, 550), (640, 615), (770, 650), (870, 655), (880, 760), (700, 820), (490, 790), (330, 700), (300, 610)
    ]
    draw.polygon(hand_points, fill=(212, 175, 55, 255))
    draw.line((300, 640, 480, 700), fill=(212, 175, 55, 255), width=18)

    # growth bars
    bar_positions = [(860, 740, 915, 610), (930, 740, 985, 660), (1000, 740, 1055, 580), (1070, 740, 1125, 500)]
    for x1, y1, x2, y2 in bar_positions:
        draw.rectangle((x1, y1, x2, y2), fill=(212, 175, 55, 255))
    draw.line((845, 720, 980, 630), fill=(212, 175, 55, 255), width=16)
    draw.line((980, 630, 1105, 510), fill=(212, 175, 55, 255), width=16)
    draw.polygon([(980, 630), (1035, 575), (1090, 630)], fill=(212, 175, 55, 255))

    # decorative separators
    draw.line((400, 860, 800, 860), fill=(212, 175, 55, 255), width=8)
    draw.line((430, 900, 770, 900), fill=(212, 175, 55, 255), width=4)

    # Text: SMART SAVE
    try:
        text_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 130)
        small_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    except OSError:
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    text = "SMART SAVE"
    bbox = draw.textbbox((0, 0), text, font=text_font)
    text_w = bbox[2] - bbox[0]
    text_x = (width - text_w) / 2
    draw.text((text_x, 930), text, fill=(245, 245, 245, 255), font=text_font)

    tagline = "SAVE SMART TODAY,"
    tagline2 = "LIVE RICH TOMORROW"
    tag_w1 = draw.textbbox((0, 0), tagline, font=small_font)[2]
    tag_w2 = draw.textbbox((0, 0), tagline2, font=small_font)[2]
    draw.text(((width - tag_w1) / 2, 1090), tagline, fill=(212, 175, 55, 255), font=small_font)
    draw.text(((width - tag_w2) / 2, 1135), tagline2, fill=(212, 175, 55, 255), font=small_font)

    # Add blur glow effect on gold ring
    glow = img.filter(ImageFilter.GaussianBlur(2))
    img.paste(glow, (0, 0))
    img.save(path)


def ensure_logo():
    if not LOGO_PATH.exists():
        draw_logo(LOGO_PATH)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def register_user(username, password, full_name, email=None):
    conn = get_connection()
    try:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if user:
            raise ValueError("Username already exists.")
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
            (username.strip(), hash_password(password), full_name.strip(), email.strip() if email else None),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None


def hash_password(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), b"tour-of-savings", 100000).hex()


class TourOfSavingsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tour of Savings")
        self.geometry("1100x760")
        self.minsize(950, 650)
        self.configure(bg="#0b111a")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0b111a")
        style.configure("TLabel", background="#0b111a", foreground="#edf3ff")
        style.configure("TLabelframe", background="#0b111a")
        style.configure("TLabelframe.Label", background="#0b111a", foreground="#edf3ff")
        style.configure("Card.TFrame", background="#111d2d")
        style.configure("Gold.TButton", background="#d4af37", foreground="#07131b", font=("Segoe UI", 11, "bold"))
        style.map("Gold.TButton", background=[("active", "#c79e2d")])

        self.container = ttk.Frame(self, padding=18)
        self.container.pack(fill="both", expand=True)

        self.auth_frame = AuthFrame(self.container, self)
        self.auth_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        for child in self.container.winfo_children():
            child.destroy()
        dashboard = ttk.Frame(self.container, padding=30)
        dashboard.pack(fill="both", expand=True)
        ttk.Label(dashboard, text="Dashboard", font=("Segoe UI", 28, "bold"), foreground="#d4af37").pack(anchor="w")
        ttk.Label(dashboard, text="Welcome to Tour of Savings", font=("Segoe UI", 16)).pack(anchor="w", pady=(10, 0))


class AuthFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(style="Card.TFrame")
        self.pack(fill="both", expand=True)
        self.build_ui()

    def build_ui(self):
        ensure_logo()
        main_panel = ttk.Frame(self, padding=26)
        main_panel.pack(fill="both", expand=True)

        left = ttk.Frame(main_panel, padding=20)
        left.pack(side="left", fill="both", expand=True)

        logo_img = tk.PhotoImage(file=str(LOGO_PATH))
        logo_label = ttk.Label(left, image=logo_img, compound="top")
        logo_label.image = logo_img
        logo_label.pack(pady=(10, 12))

        title = ttk.Label(left, text="TOUR OF SAVINGS", font=("Segoe UI", 24, "bold"), foreground="#d4af37")
        title.pack(pady=(10, 5))

        subtitle = ttk.Label(left, text="SAVE SMART TODAY, LIVE RICH TOMORROW", font=("Segoe UI", 12, "bold"), foreground="#e9f1ff")
        subtitle.pack(pady=(0, 18))

        right = ttk.Frame(main_panel, padding=20)
        right.pack(side="right", fill="both", expand=True)

        card = ttk.Frame(right, padding=28, style="Card.TFrame")
        card.pack(fill="both", expand=True)

        notebook = ttk.Notebook(card)
        notebook.pack(fill="both", expand=True)

        login_frame = ttk.Frame(notebook, padding=16)
        register_frame = ttk.Frame(notebook, padding=16)
        notebook.add(login_frame, text="Login")
        notebook.add(register_frame, text="Register")

        ttk.Label(login_frame, text="Username", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.login_username = ttk.Entry(login_frame, width=32)
        self.login_username.pack(fill="x", pady=(0, 10))

        ttk.Label(login_frame, text="Password", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.login_password = ttk.Entry(login_frame, width=32, show="*")
        self.login_password.pack(fill="x", pady=(0, 18))

        login_btn = ttk.Button(login_frame, text="Login", command=self.handle_login, style="Gold.TButton")
        login_btn.pack(fill="x", pady=(0, 8))

        ttk.Label(register_frame, text="Full Name", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.reg_name = ttk.Entry(register_frame, width=32)
        self.reg_name.pack(fill="x", pady=(0, 10))

        ttk.Label(register_frame, text="Username", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.reg_username = ttk.Entry(register_frame, width=32)
        self.reg_username.pack(fill="x", pady=(0, 10))

        ttk.Label(register_frame, text="Email (optional)", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.reg_email = ttk.Entry(register_frame, width=32)
        self.reg_email.pack(fill="x", pady=(0, 10))

        ttk.Label(register_frame, text="Password", foreground="#edf3ff").pack(anchor="w", pady=(8, 4))
        self.reg_password = ttk.Entry(register_frame, width=32, show="*")
        self.reg_password.pack(fill="x", pady=(0, 18))

        reg_btn = ttk.Button(register_frame, text="Create Account", command=self.handle_register, style="Gold.TButton")
        reg_btn.pack(fill="x")

    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        if not username or not password:
            messagebox.showerror("Login Error", "Please type both username and password.")
            return
        user = get_user_by_username(username)
        if not user:
            messagebox.showerror("Login Error", "No account found for this username.")
            return
        if hash_password(password) != user["password_hash"]:
            messagebox.showerror("Login Error", "Incorrect password.")
            return
        self.app.current_user = user
        self.app.show_dashboard()

    def handle_register(self):
        full_name = self.reg_name.get().strip()
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()

        if not full_name or not username or not password:
            messagebox.showerror("Registration Error", "Full name, username and password are required.")
            return
        if len(password) < 6:
            messagebox.showerror("Registration Error", "Password must be at least 6 characters long.")
            return
        try:
            user_id = register_user(username, password, full_name, email)
        except ValueError as exc:
            messagebox.showerror("Registration Error", str(exc))
            return
        self.app.current_user = {"id": user_id, "username": username, "full_name": full_name}
        self.app.show_dashboard()


if __name__ == "__main__":
    init_db()
    app = TourOfSavingsApp()
    app.mainloop()
