import tkinter as tk
from tkinter import ttk, messagebox
from escpos.printer import Win32Raw

class NTCTicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NTC-NCR Ticket Generator")
        self.root.geometry("450x600")  
        self.root.resizable(False, False)

        # Variables
        self.printer_name_var = tk.StringVar(value="XP-58C-Licensing")
        self.header_1_var = tk.StringVar(value="NTC - NCR")
        self.header_2_var = tk.StringVar(value="Licensing")
        self.ticket_num_var = tk.IntVar(value=1)
        self.bold_var = tk.BooleanVar(value=True)
        self.auto_increment_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = ttk.LabelFrame(self.root, text=" Printer & Text Settings ", padding=10)
        header_frame.pack(fill="x", padx=15, pady=10)

        # Printer Name
        ttk.Label(header_frame, text="Printer Name (Windows):").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(header_frame, textvariable=self.printer_name_var, width=25).grid(row=0, column=1, pady=4)

        # Header Line 1
        ttk.Label(header_frame, text="Header Line 1:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(header_frame, textvariable=self.header_1_var, width=25).grid(row=1, column=1, pady=4)

        # Header Line 2
        ttk.Label(header_frame, text="Header Line 2:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(header_frame, textvariable=self.header_2_var, width=25).grid(row=2, column=1, pady=4)

        # Bold Option
        ttk.Checkbutton(header_frame, text="Make Headers Bold", variable=self.bold_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        # Number Control Frame
        num_frame = ttk.LabelFrame(self.root, text=" Ticket Number Control ", padding=10)
        num_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(num_frame, text="Current Number:").grid(row=0, column=0, sticky="w", pady=4)
        
        spin_btn_frame = ttk.Frame(num_frame)
        spin_btn_frame.grid(row=0, column=1, pady=4, sticky="w")

        ttk.Button(spin_btn_frame, text="-", width=3, command=self.decrement_num).pack(side="left", padx=2)
        ttk.Entry(spin_btn_frame, textvariable=self.ticket_num_var, width=8, justify="center").pack(side="left", padx=2)
        ttk.Button(spin_btn_frame, text="+", width=3, command=self.increment_num).pack(side="left", padx=2)

        ttk.Checkbutton(num_frame, text="Auto-increment number after printing", variable=self.auto_increment_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=6)

        # Action Buttons
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=15)

        # Standard tk.Button to properly support standard padding
        print_btn = tk.Button(
            btn_frame, 
            text="🖨️ PRINT TICKET", 
            bg="#0078D4", 
            fg="white", 
            font=("Arial", 12, "bold"), 
            pady=10, 
            command=self.print_ticket
        )
        print_btn.pack(fill="x")

        # Live Text Preview Frame
        preview_frame = ttk.LabelFrame(self.root, text=" Layout Preview (Monospace) ", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.preview_text = tk.Text(preview_frame, height=10, width=34, font=("Consolas", 10), bg="#F4F4F4")
        self.preview_text.pack(fill="both", expand=True)

        # Triggers for Live Preview Updates
        self.header_1_var.trace_add("write", self.update_preview)
        self.header_2_var.trace_add("write", self.update_preview)
        self.ticket_num_var.trace_add("write", self.update_preview)
        self.bold_var.trace_add("write", self.update_preview)

        self.update_preview()

    def increment_num(self):
        self.ticket_num_var.set(self.ticket_num_var.get() + 1)

    def decrement_num(self):
        if self.ticket_num_var.get() > 1:
            self.ticket_num_var.set(self.ticket_num_var.get() - 1)

    def generate_ticket_text(self):
        line_width = 32
        border = "#" * line_width
        
        # Using 28 characters for the inside to account for '# ' and ' #'
        h1 = self.header_1_var.get().strip()[:28].center(28)
        h2 = self.header_2_var.get().strip()[:28].center(28)
        num_str = f"{self.ticket_num_var.get():03d}".center(line_width) # Number formatting in preview
        empty = " " * 28

        lines = [
            border,
            f"# {h1} #",
            f"# {h2} #",
            f"# {empty} #",
            f"{num_str}",
            border
        ]
        return "\n".join(lines)

    def update_preview(self, *args):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, self.generate_ticket_text())
        self.preview_text.config(state="disabled")

    def print_ticket(self):
        printer_name = self.printer_name_var.get().strip()
        h1 = self.header_1_var.get().strip()
        h2 = self.header_2_var.get().strip()
        num_formatted = f"{self.ticket_num_var.get():03d}"
        is_bold = self.bold_var.get()

        try:
            # Initialize Win32Raw Printer connection
            p = Win32Raw(printer_name)
            p.open(job_name="NTC Ticket Print")

            # --- HARDWARE RESET (FIXES STUCK BIG TEXT) ---
            p.text("\x1b\x40")      # ESC @ : Initializes printer (clears all buffers)
            p.text("\x1d\x21\x00")  # GS ! 0 : Forces character size to normal (1x width, 1x height)
            p.text("\x1b\x21\x00")  # ESC ! 0 : Forces standard font mode

            # 58mm standard printable character width is 32 chars
            width = 32
            border_line = "#" * width

            # --- TOP BORDER ---
            p.set(align='center')
            p.text(f"{border_line}\n")

            # --- HEADER LINE 1 ---
            inner1 = h1[:28].center(28)
            p.set(align='center', bold=is_bold)
            p.text(f"# {inner1} #\n")

            # --- HEADER LINE 2 ---
            inner2 = h2[:28].center(28)
            p.set(align='center', bold=is_bold)
            p.text(f"# {inner2} #\n")

            # --- EMPTY SPACER ROW ---
            empty_inner = " " * 28
            p.set(align='center', bold=False)
            p.text(f"# {empty_inner} #\n")

            # --- LARGE TICKET NUMBER ---
            # Turn on double width/height strictly for the number
            p.set(align='center', bold=True, double_height=True, double_width=True)
            p.text(f"{num_formatted}\n")

            # --- BOTTOM BORDER ---
            # Force hardware back to normal size before printing the bottom border
            p.text("\x1d\x21\x00")  # GS ! 0 : Reset character size
            p.set(align='center', bold=False, double_height=False, double_width=False)
            p.text(f"{border_line}\n")

            # --- FEED & CUT ---
            p.text("\n\n")
            p.cut()

            # Close printer handle
            p.close()

            # Auto-increment
            if self.auto_increment_var.get():
                self.increment_num()

        except Exception as e:
            messagebox.showerror("Printing Error", f"Could not print to device '{printer_name}'.\n\nError details: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NTCTicketApp(root)
    root.mainloop()