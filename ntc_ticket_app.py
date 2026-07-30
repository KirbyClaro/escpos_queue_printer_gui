import tkinter as tk
from tkinter import ttk, messagebox
from escpos.printer import Win32Raw
from datetime import datetime
import os

class NTCTicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NTC-NCR Ticket Generator Pro")
        self.root.geometry("450x760")
        self.root.resizable(False, False)

        # Main Variables
        self.printer_name_var = tk.StringVar(value="XP-58C-Licensing")
        self.header_1_var = tk.StringVar(value="NTC - NCR")
        self.header_2_var = tk.StringVar(value="Licensing")
        self.bold_var = tk.BooleanVar(value=True)
        
        # Logo Variables
        self.logo_var = tk.BooleanVar(value=False)
        self.logo_path_var = tk.StringVar(value="ntc.png")

        # Footer Variables
        self.footer_1_var = tk.StringVar(value="Please wait for your number")
        self.footer_2_var = tk.StringVar(value="Prepare your valid ID")

        # Number Variables
        self.ticket_num_var = tk.IntVar(value=1)
        self.auto_increment_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # 1. Header & Logo Frame
        header_frame = ttk.LabelFrame(self.root, text=" 1. Printer & Header Settings ", padding=10)
        header_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(header_frame, text="Printer Name:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(header_frame, textvariable=self.printer_name_var, width=28).grid(row=0, column=1, pady=2)

        ttk.Label(header_frame, text="Header Line 1:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(header_frame, textvariable=self.header_1_var, width=28).grid(row=1, column=1, pady=2)

        ttk.Label(header_frame, text="Header Line 2:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(header_frame, textvariable=self.header_2_var, width=28).grid(row=2, column=1, pady=2)

        ttk.Checkbutton(header_frame, text="Bold Headers", variable=self.bold_var).grid(row=3, column=0, sticky="w", pady=4)
        
        # Logo sub-frame
        logo_frame = ttk.Frame(header_frame)
        logo_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=4)
        ttk.Checkbutton(logo_frame, text="Print Logo", variable=self.logo_var).pack(side="left")
        ttk.Label(logo_frame, text=" File:").pack(side="left")
        ttk.Entry(logo_frame, textvariable=self.logo_path_var, width=15).pack(side="left", padx=5)

        # 2. Footer Settings Frame
        footer_frame = ttk.LabelFrame(self.root, text=" 2. Footer Instructions ", padding=10)
        footer_frame.pack(fill="x", padx=15, pady=5)

        ttk.Entry(footer_frame, textvariable=self.footer_1_var, width=45).pack(pady=2)
        ttk.Entry(footer_frame, textvariable=self.footer_2_var, width=45).pack(pady=2)

        # 3. Number Control Frame
        num_frame = ttk.LabelFrame(self.root, text=" 3. Ticket Control ", padding=10)
        num_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(num_frame, text="Current Number:").grid(row=0, column=0, sticky="w", pady=4)
        
        spin_btn_frame = ttk.Frame(num_frame)
        spin_btn_frame.grid(row=0, column=1, pady=4, sticky="w")

        ttk.Button(spin_btn_frame, text="-", width=3, command=self.decrement_num).pack(side="left", padx=2)
        ttk.Entry(spin_btn_frame, textvariable=self.ticket_num_var, width=6, justify="center").pack(side="left", padx=2)
        ttk.Button(spin_btn_frame, text="+", width=3, command=self.increment_num).pack(side="left", padx=2)
        
        # New Reset Button
        ttk.Button(spin_btn_frame, text="↺ Reset to 001", command=self.reset_num).pack(side="left", padx=10)

        ttk.Checkbutton(num_frame, text="Auto-increment after printing", variable=self.auto_increment_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=6)

        # 4. Action Buttons
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=15)

        print_btn = tk.Button(
            btn_frame, 
            text="🖨️ PRINT TICKET", 
            bg="#0078D4", 
            fg="white", 
            font=("Arial", 12, "bold"), 
            pady=12, 
            command=self.print_ticket
        )
        print_btn.pack(fill="x")

        # 5. Live Text Preview
        preview_frame = ttk.LabelFrame(self.root, text=" Layout Preview (Monospace) ", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.preview_text = tk.Text(preview_frame, height=13, width=34, font=("Consolas", 9), bg="#F4F4F4")
        self.preview_text.pack(fill="both", expand=True)

        # Triggers
        for var in [self.header_1_var, self.header_2_var, self.footer_1_var, self.footer_2_var, self.ticket_num_var]:
            var.trace_add("write", self.update_preview)
        
        self.logo_var.trace_add("write", self.update_preview)
        self.update_preview()

    # --- Button Logic ---
    def increment_num(self):
        self.ticket_num_var.set(self.ticket_num_var.get() + 1)

    def decrement_num(self):
        if self.ticket_num_var.get() > 1:
            self.ticket_num_var.set(self.ticket_num_var.get() - 1)
            
    def reset_num(self):
        self.ticket_num_var.set(1)

    # --- Preview Logic ---
    def generate_ticket_text(self):
        w = 32
        thick = "=" * w
        thin = "-" * w
        
        h1 = self.header_1_var.get().strip().center(w)
        h2 = self.header_2_var.get().strip().center(w)
        f1 = self.footer_1_var.get().strip().center(w)
        f2 = self.footer_2_var.get().strip().center(w)
        
        logo_placeholder = "[ LOGO IMAGE ]".center(w) if self.logo_var.get() else ""
        date_str = datetime.now().strftime("%b %d, %Y %I:%M %p").center(w)
        num_str = f"{self.ticket_num_var.get():03d}".center(w)

        lines = [thick]
        if logo_placeholder:
            lines.extend([logo_placeholder, ""])
        lines.extend([
            h1, 
            h2, 
            thin, 
            date_str, 
            thin, 
            "QUEUE NO.".center(w), 
            "", 
            num_str, 
            "", 
            thin, 
            f1, 
            f2, 
            thick
        ])
        return "\n".join(lines)

    def update_preview(self, *args):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, self.generate_ticket_text())
        self.preview_text.config(state="disabled")

    # --- Print Logic ---
    def print_ticket(self):
        printer_name = self.printer_name_var.get().strip()
        h1 = self.header_1_var.get().strip()
        h2 = self.header_2_var.get().strip()
        f1 = self.footer_1_var.get().strip()
        f2 = self.footer_2_var.get().strip()
        num_str = f"{self.ticket_num_var.get():03d}"
        now_str = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")

        try:
            # 1. Initialize ESC/POS Byte Commands
            ESC = b"\x1b"
            GS = b"\x1d"

            # Reset printer
            INIT = ESC + b"@"
            # Alignments
            ALIGN_CENTER = ESC + b"a\x01"
            # Font Styles
            BOLD_ON = ESC + b"E\x01"
            BOLD_OFF = ESC + b"E\x00"
            # Text Sizing
            SIZE_NORMAL = GS + b"!\x00"
            SIZE_DOUBLE = GS + b"!\x11"  # Double height + Double width
            # Cut command
            CUT = GS + b"V\x01"

            # 2. Build Payload
            buf = bytearray()
            buf += INIT
            buf += ALIGN_CENTER

            # Top Border
            buf += (("=" * 32) + "\n").encode('ascii')

            # Headers
            if self.bold_var.get():
                buf += BOLD_ON
            if h1:
                buf += (h1 + "\n").encode('ascii', errors='replace')
            if h2:
                buf += (h2 + "\n").encode('ascii', errors='replace')
            buf += BOLD_OFF

            # Date Line
            buf += (("-" * 32) + "\n").encode('ascii')
            buf += (now_str + "\n").encode('ascii')
            buf += (("-" * 32) + "\n").encode('ascii')

            # Queue Number Label
            buf += b"QUEUE NO.\n\n"

            # Large Ticket Number
            buf += SIZE_DOUBLE
            buf += BOLD_ON
            buf += (num_str + "\n\n").encode('ascii')

            # Reset Size & Footers
            buf += SIZE_NORMAL
            buf += BOLD_OFF
            buf += (("-" * 32) + "\n").encode('ascii')
            if f1:
                buf += (f1 + "\n").encode('ascii', errors='replace')
            if f2:
                buf += (f2 + "\n").encode('ascii', errors='replace')
            buf += (("=" * 32) + "\n").encode('ascii')

            # Feed lines & Cut
            buf += b"\n\n\n"
            buf += CUT

            # 3. Send Directly to Windows Spooler via win32print
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("NTC Ticket", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, bytes(buf))
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)

            # Auto Increment
            if self.auto_increment_var.get():
                self.increment_num()

        except Exception as e:
            messagebox.showerror("Printing Error", f"Failed to send print job to '{printer_name}'.\n\nDetails: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NTCTicketApp(root)
    root.mainloop()