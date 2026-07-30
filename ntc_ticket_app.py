import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import win32print

class NTCTicketAppPro:
    def __init__(self, root):
        self.root = root
        self.root.title("NTC-NCR Ticket Generator Pro")
        self.root.geometry("480x780")
        self.root.resizable(False, False)

        # Variables
        self.printer_name_var = tk.StringVar(value="XP-58C-Licensing")
        self.header_1_var = tk.StringVar(value="NTC - NCR")
        self.header_2_var = tk.StringVar(value="Licensing")
        self.bold_var = tk.BooleanVar(value=True)
        self.logo_enabled_var = tk.BooleanVar(value=False)
        self.logo_file_var = tk.StringVar(value="ntc.png")

        self.footer_1_var = tk.StringVar(value="Please wait for your number")
        self.footer_2_var = tk.StringVar(value="Prepare your valid ID")

        self.ticket_num_var = tk.IntVar(value=1)
        self.auto_increment_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # 1. Printer & Header Settings
        f1 = ttk.LabelFrame(self.root, text=" 1. Printer & Header Settings ", padding=10)
        f1.pack(fill="x", padx=15, pady=5)

        ttk.Label(f1, text="Printer Name:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(f1, textvariable=self.printer_name_var, width=28).grid(row=0, column=1, pady=2)

        ttk.Label(f1, text="Header Line 1:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(f1, textvariable=self.header_1_var, width=28).grid(row=1, column=1, pady=2)

        ttk.Label(f1, text="Header Line 2:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(f1, textvariable=self.header_2_var, width=28).grid(row=2, column=1, pady=2)

        ttk.Checkbutton(f1, text="Bold Headers", variable=self.bold_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=4)

        logo_frame = ttk.Frame(f1)
        logo_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(logo_frame, text="Print Logo  File:", variable=self.logo_enabled_var).pack(side="left")
        ttk.Entry(logo_frame, textvariable=self.logo_file_var, width=15).pack(side="left", padx=5)

        # 2. Footer Instructions
        f2 = ttk.LabelFrame(self.root, text=" 2. Footer Instructions ", padding=10)
        f2.pack(fill="x", padx=15, pady=5)

        ttk.Entry(f2, textvariable=self.footer_1_var, width=40).pack(pady=2)
        ttk.Entry(f2, textvariable=self.footer_2_var, width=40).pack(pady=2)

        # 3. Ticket Control
        f3 = ttk.LabelFrame(self.root, text=" 3. Ticket Control ", padding=10)
        f3.pack(fill="x", padx=15, pady=5)

        ctrl_sub = ttk.Frame(f3)
        ctrl_sub.pack(fill="x", pady=2)

        ttk.Label(ctrl_sub, text="Current Number:").pack(side="left")
        ttk.Button(ctrl_sub, text="-", width=3, command=self.decrement_num).pack(side="left", padx=4)
        ttk.Entry(ctrl_sub, textvariable=self.ticket_num_var, width=6, justify="center").pack(side="left")
        ttk.Button(ctrl_sub, text="+", width=3, command=self.increment_num).pack(side="left", padx=4)
        ttk.Button(ctrl_sub, text="↺ Reset to 001", command=self.reset_num).pack(side="left", padx=10)

        ttk.Checkbutton(f3, text="Auto-increment after printing", variable=self.auto_increment_var).pack(anchor="w", pady=4)

        # Print Button
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=15, pady=5)
        
        print_btn = tk.Button(
            btn_frame, 
            text="🖨️   PRINT TICKET", 
            bg="#0078D4", 
            fg="white", 
            font=("Arial", 12, "bold"), 
            pady=8, 
            command=self.print_ticket
        )
        print_btn.pack(fill="x")

        # Preview Frame
        f4 = ttk.LabelFrame(self.root, text=" Layout Preview (Monospace) ", padding=10)
        f4.pack(fill="both", expand=True, padx=15, pady=5)

        self.preview_text = tk.Text(f4, height=14, width=34, font=("Consolas", 9), bg="#F8F9FA")
        self.preview_text.pack(fill="both", expand=True)

        # Triggers
        for var in [self.header_1_var, self.header_2_var, self.footer_1_var, self.footer_2_var, 
                    self.ticket_num_var, self.logo_enabled_var, self.logo_file_var]:
            var.trace_add("write", self.update_preview)

        self.update_preview()

    def increment_num(self):
        self.ticket_num_var.set(self.ticket_num_var.get() + 1)

    def decrement_num(self):
        if self.ticket_num_var.get() > 1:
            self.ticket_num_var.set(self.ticket_num_var.get() - 1)

    def reset_num(self):
        self.ticket_num_var.set(1)

    def generate_preview_text(self):
        w = 32
        border_top = "=" * w
        border_dashed = "-" * w
        now_str = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
        num_str = f"{self.ticket_num_var.get():03d}"

        lines = [border_top]
        if self.logo_enabled_var.get():
            lines.append("[ LOGO PREVIEW (TEXT ONLY) ]".center(w))
            lines.append("")

        if self.header_1_var.get():
            lines.append(self.header_1_var.get().center(w))
        if self.header_2_var.get():
            lines.append(self.header_2_var.get().center(w))

        lines.append(border_dashed)
        lines.append(now_str.center(w))
        lines.append(border_dashed)
        lines.append("QUEUE NO.".center(w))
        lines.append("")
        lines.append(num_str.center(w))
        lines.append("")
        lines.append(border_dashed)

        if self.footer_1_var.get():
            lines.append(self.footer_1_var.get().center(w))
        if self.footer_2_var.get():
            lines.append(self.footer_2_var.get().center(w))

        lines.append(border_top)
        return "\n".join(lines)

    def update_preview(self, *args):
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, self.generate_preview_text())
        self.preview_text.config(state="disabled")

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

            INIT = ESC + b"@"
            ALIGN_CENTER = ESC + b"a\x01"
            BOLD_ON = ESC + b"E\x01"
            BOLD_OFF = ESC + b"E\x00"
            SIZE_NORMAL = GS + b"!\x00"
            SIZE_DOUBLE = GS + b"!\x11"  # Double height + Double width
            CUT = GS + b"V\x01"

            # 2. Build Raw Payload
            buf = bytearray()
            buf += INIT
            buf += ALIGN_CENTER

            # Top Border
            buf += (("=" * 32) + "\n").encode('ascii')

            # Logo Warning (Images in raw byte mode can cause corruption on basic drivers)
            if self.logo_enabled_var.get():
                 buf += b"[ LOGO OMITTED IN RAW MODE ]\n\n"

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
    app = NTCTicketAppPro(root)
    root.mainloop()