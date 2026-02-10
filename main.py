import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Scale, HORIZONTAL, colorchooser, Checkbutton, BooleanVar
from PIL import Image, ImageTk, ImageEnhance, ImageOps

# --- Backend Logic ---
class ASCIIEngine:
    def __init__(self):
        self.RAMPS = {
            "Standard (Detailed)": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
            "Blocks (Solid)": "█▓▒░ ",
            "Binary (Matrix)": "10 ",
            "Minimalist": "@%#*+=-:. ",
            "Custom": "" # Placeholder
        }

    def resize_image(self, img, width):
        # Vertical aspect ratio correction (0.55) for monospace fonts
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio * 0.55)
        return img.resize((width, new_height), Image.Resampling.LANCZOS)

    def get_pixel_data(self, image_path, width, contrast_factor, invert):
        try:
            img = Image.open(image_path)
            img = img.convert("L") # Convert to grayscale
            
            # Contrast enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)
            
            if invert:
                img = ImageOps.invert(img)
                
            img = self.resize_image(img, width)
            return img, None
        except Exception as e:
            return None, str(e)

    def generate_text(self, img, ramp_key, custom_ramp=""):
        pixels = img.getdata()
        
        # Ramp selection logic
        if ramp_key == "Custom" and custom_ramp:
            ramp = custom_ramp
        else:
            ramp = self.RAMPS.get(ramp_key, self.RAMPS["Standard (Detailed)"])
            
        ramp_len = len(ramp)
        ascii_str = ""
        
        for pixel in pixels:
            index = int((pixel / 256) * ramp_len)
            index = min(index, ramp_len - 1)
            ascii_str += ramp[index]
            
        return ascii_str

    def hex_to_rgb(self, hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    def interpolate_color(self, val, color_start, color_end):
        # Linear interpolation (Lerp) between two colors based on brightness (0-255)
        t = val / 255.0
        r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def generate_html(self, img, ramp_key, color_dark, color_light, bg_color):
        pixels = img.getdata()
        width = img.width

        ramp = self.RAMPS.get(ramp_key, self.RAMPS["Standard (Detailed)"])
        ramp_len = len(ramp)
        
        c_start = self.hex_to_rgb(color_dark)
        c_end = self.hex_to_rgb(color_light)
        
        html_content = f"""
        <html>
        <body style="background-color:{bg_color}; font-family: 'Courier New', monospace; font-size: 10px; line-height: 0.6em; white-space: pre;">
        """
        
        current_line = ""
        for i, pixel in enumerate(pixels):
            # Get character
            idx = int((pixel / 256) * ramp_len)
            char = ramp[min(idx, ramp_len - 1)]
            
            # Calculate specific color for character
            color = self.interpolate_color(pixel, c_start, c_end)
            
            # HTML Sanitize
            if char == "<": char = "&lt;"
            if char == ">": char = "&gt;"
            
            current_line += f'<span style="color:{color}">{char}</span>'
            
            if (i + 1) % width == 0:
                html_content += f"<div>{current_line}</div>"
                current_line = ""
                
        html_content += "</body></html>"
        return html_content

# --- Frontend (GUI) ---
class ASCIIApp:
    def __init__(self, root):
        self.engine = ASCIIEngine()
        self.root = root
        self.root.title("ZerxStar HyperASCII v3.0 - Scientific Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg="#121212")

        # State Variables
        self.current_image_path = None
        self.color_dark = "#38005E"   # Dark zones (Deep Purple)
        self.color_light = "#CFB7FF"  # Light zones (Pale Lavender)
        self.bg_color = "#000000"     # Background

        # --- LEFT PANEL: CONTROLS ---
        control_frame = tk.Frame(root, bg="#1e1e1e", width=300, padx=15, pady=15)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Header
        tk.Label(control_frame, text="PARAMETERS", bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 14, "bold")).pack(pady=5)

        # Load
        tk.Button(control_frame, text=" Load Source Image", command=self.load_image, bg="#333", fg="white").pack(fill=tk.X, pady=5)

        # Sliders
        self.create_slider(control_frame, "Resolution (Width)", 50, 400, 100)
        self.width_scale = self.last_scale
        
        self.create_slider(control_frame, "Contrast (Gamma)", 0.5, 3.0, 1.5, 0.1)
        self.contrast_scale = self.last_scale

        # Ramp Selector
        tk.Label(control_frame, text="Mapping Algorithm", bg="#1e1e1e", fg="#aaa").pack(pady=(10,0))
        self.ramp_var = tk.StringVar(value="Standard (Detailed)")
        tk.OptionMenu(control_frame, self.ramp_var, *self.engine.RAMPS.keys(), command=self.trigger_update).pack(fill=tk.X)

        # Custom Ramp
        tk.Label(control_frame, text="Custom Ramp:", bg="#1e1e1e", fg="#aaa").pack(pady=(5,0))
        self.custom_ramp_entry = tk.Entry(control_frame, bg="#2d2d2d", fg="white")
        self.custom_ramp_entry.pack(fill=tk.X)
        self.custom_ramp_entry.bind("<KeyRelease>", self.trigger_update)

        # Checkboxes
        self.invert_var = BooleanVar()
        tk.Checkbutton(control_frame, text="Invert Negative", variable=self.invert_var, bg="#1e1e1e", fg="white", selectcolor="#000", command=self.trigger_update).pack(pady=5, anchor="w")

        # Real-time Control
        self.realtime_var = BooleanVar(value=True)
        tk.Checkbutton(control_frame, text="Real-time Preview", variable=self.realtime_var, bg="#1e1e1e", fg="#00ffcc", selectcolor="#000", command=self.trigger_update).pack(pady=5, anchor="w")
        
        # Manual Update Button
        tk.Button(control_frame, text="↻ Refresh View", command=self.force_update, bg="#444", fg="white").pack(fill=tk.X)

        # --- HTML / COLOR SECTION ---
        tk.Label(control_frame, text="HTML GRADIENT", bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 12, "bold")).pack(pady=(20,5))
        
        color_frame = tk.Frame(control_frame, bg="#1e1e1e")
        color_frame.pack(fill=tk.X)
        
        self.btn_dark = tk.Button(color_frame, text="■ Dark", bg=self.color_dark, fg="white", command=lambda: self.pick_color('dark'))
        self.btn_dark.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.btn_light = tk.Button(color_frame, text="■ Light", bg=self.color_light, fg="black", command=lambda: self.pick_color('light'))
        self.btn_light.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Export Buttons
        tk.Label(control_frame, text="EXPORT", bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 12, "bold")).pack(pady=(20,5))
        tk.Button(control_frame, text="💾 Save .TXT (Plain)", command=self.save_txt, bg="#28a745", fg="white").pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="🌐 Save .HTML (Color)", command=self.save_html, bg="#007acc", fg="white").pack(fill=tk.X, pady=2)

        # --- RIGHT PANEL: VIEWER ---
        self.text_preview = scrolledtext.ScrolledText(root, bg="#000000", fg="#00ff00", font=("Courier New", 6))
        self.text_preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_slider(self, parent, label, min_v, max_v, default, res=1):
        tk.Label(parent, text=label, bg="#1e1e1e", fg="#aaa").pack(pady=(10,0))
        scale = Scale(parent, from_=min_v, to=max_v, resolution=res, orient=HORIZONTAL, bg="#1e1e1e", fg="white", highlightthickness=0)
        scale.set(default)
        scale.pack(fill=tk.X)
        # Generic binding, checks realtime toggle
        scale.bind("<B1-Motion>", self.trigger_update)
        scale.bind("<ButtonRelease-1>", self.trigger_update)
        self.last_scale = scale

    def pick_color(self, target):
        color = colorchooser.askcolor()[1]
        if color:
            if target == 'dark':
                self.color_dark = color
                self.btn_dark.config(bg=color)
            else:
                self.color_light = color
                self.btn_light.config(bg=color)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.webp")])
        if path:
            self.current_image_path = path
            self.force_update()

    def trigger_update(self, event=None):
        # Conditional Logic: Only update if checkbox is active
        if self.realtime_var.get():
            self.update_preview()

    def force_update(self):
        # Force update ignoring checkbox
        self.update_preview()

    def update_preview(self):
        if not self.current_image_path:
            return

        # 1. Get processed image
        img, error = self.engine.get_pixel_data(
            self.current_image_path, 
            self.width_scale.get(), 
            self.contrast_scale.get(), 
            self.invert_var.get()
        )
        
        if error: return

        # 2. Generate Text
        ascii_str = self.engine.generate_text(
            img, 
            self.ramp_var.get(), 
            self.custom_ramp_entry.get()
        )
        
        # 3. Format for display
        width = self.width_scale.get()
        ascii_formatted = "\n".join([ascii_str[i:i+width] for i in range(0, len(ascii_str), width)])

        self.text_preview.delete("1.0", tk.END)
        self.text_preview.insert(tk.END, ascii_formatted)
        
        # Info bar
        info = f"Dimensions: {width}x{img.height} | Characters: {len(ascii_str)}"
        self.root.title(f"ZerxStar HyperASCII v3.0 - {info}")

    def save_txt(self):
        if not self.current_image_path: return
        self.force_update() # Ensure WYSIWYG
        content = self.text_preview.get("1.0", tk.END)
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    def save_html(self):
        if not self.current_image_path: return
        
        # Re-process for export
        img, _ = self.engine.get_pixel_data(
            self.current_image_path, 
            self.width_scale.get(), 
            self.contrast_scale.get(), 
            self.invert_var.get()
        )
        
        html_content = self.engine.generate_html(
            img, 
            self.ramp_var.get(), 
            self.color_dark, 
            self.color_light,
            self.bg_color
        )
        
        path = filedialog.asksaveasfilename(defaultextension=".html")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            messagebox.showinfo("Success", "Chromatic HTML generated successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIApp(root)
    root.mainloop()