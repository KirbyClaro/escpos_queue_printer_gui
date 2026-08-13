import os
import datetime
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import win32print
from PIL import Image
from escpos.printer import Dummy

class NTCTicketAppPro:
    def __init__(self, root):
        self.root = root
        self.root.title("NTC Ticket Generator Pro")
        self.root.geometry("480x920")
        self.root.resizable(False, False)

        # Variables
        self.printer_name_var = tk.StringVar(value="XP-58C")
        self.header_1_var = tk.StringVar(value="NTC - NCR")
        self.header_2_var = tk.StringVar(value="Licensing")
        self.bold_var = tk.BooleanVar(value=True)
        self.logo_enabled_var = tk.BooleanVar(value=True)
        self.logo_file_var = tk.StringVar(value="ntc.png")

        self.footer_1_var = tk.StringVar(value="Please wait for your number")
        self.footer_2_var = tk.StringVar(value="Missed numbers require a new ticket.") 

        # --- UPDATED: Shared Queue Memory ---
        # "Regular" handles both Single (S) and Multiple (M). "Priority" handles (P).
        self.counters = {"Regular": 1, "Priority": 1}
        self.last_queue_type = "Regular"

        self.ticket_prefix_var = tk.StringVar(value="S")
        self.ticket_num_var = tk.IntVar(value=self.counters["Regular"])
        self.auto_increment_var = tk.BooleanVar(value=True)

        # Daily Log Storage
        self.print_log = []

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
        header_2_cb = ttk.Combobox(
            f1, 
            textvariable=self.header_2_var, 
            width=25, 
            values=["Licensing", "Cashier", "Releasing"]
        )
        header_2_cb.grid(row=2, column=1, pady=2)

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

        # Transaction Type Prefix Selection
        type_frame = ttk.Frame(f3)
        type_frame.pack(fill="x", pady=4)
        ttk.Label(type_frame, text="Transaction Type:").pack(side="left", padx=(0, 5))
        
        ttk.Radiobutton(type_frame, text="Single (S)", variable=self.ticket_prefix_var, value="S", command=self.on_prefix_change).pack(side="left", padx=2)
        ttk.Radiobutton(type_frame, text="Multiple (M)", variable=self.ticket_prefix_var, value="M", command=self.on_prefix_change).pack(side="left", padx=2)
        ttk.Radiobutton(type_frame, text="Priority (P)", variable=self.ticket_prefix_var, value="P", command=self.on_prefix_change).pack(side="left", padx=2)

        ctrl_sub = ttk.Frame(f3)
        ctrl_sub.pack(fill="x", pady=4)

        ttk.Label(ctrl_sub, text="Current Number:").pack(side="left")
        ttk.Button(ctrl_sub, text="-", width=3, command=self.decrement_num).pack(side="left", padx=4)
        ttk.Entry(ctrl_sub, textvariable=self.ticket_num_var, width=6, justify="center").pack(side="left")
        ttk.Button(ctrl_sub, text="+", width=3, command=self.increment_num).pack(side="left", padx=4)
        ttk.Button(ctrl_sub, text="↺ Reset to 001", command=self.reset_num).pack(side="left", padx=10)

        ttk.Checkbutton(f3, text="Auto-increment after printing", variable=self.auto_increment_var).pack(anchor="w", pady=4)

        # Master Reset Button
        ttk.Button(f3, text="⚠️ Master Reset (End of Day)", command=self.master_reset).pack(fill="x", pady=(5, 0))

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

        self.preview_text = tk.Text(f4, height=12, width=44, font=("Consolas", 9), bg="#F8F9FA")
        self.preview_text.pack(fill="both", expand=True)

        # 5. Recent Logs & Export
        f5 = ttk.LabelFrame(self.root, text=" Recent Prints & Log Export ", padding=10)
        f5.pack(fill="x", padx=15, pady=5)

        self.log_listbox = tk.Listbox(f5, height=5, font=("Consolas", 9), bg="#F8F9FA")
        self.log_listbox.pack(fill="x", pady=(0, 5))

        ttk.Button(f5, text="💾 Export Daily Log (CSV)", command=self.export_csv).pack(fill="x")

        # Triggers
        for var in [self.header_1_var, self.header_2_var, self.footer_1_var, self.footer_2_var, 
                    self.ticket_num_var, self.ticket_prefix_var, self.logo_enabled_var, self.logo_file_var]:
            var.trace_add("write", self.update_preview)

        # Trigger to update Window Title based on Department
        self.header_2_var.trace_add("write", self.update_window_title)

        self.update_window_title()
        self.update_preview()
        self.update_log_display()

    def export_csv(self):
        if not self.print_log:
            messagebox.showinfo("Export Empty", "There are no printed tickets to export yet.")
            return
            
        default_name = f"NTC_Queue_Log_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            title="Save Daily Queue Log",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Ticket Number", "Department", "Transaction Type"])
                    for log in self.print_log:
                        prefix = log['ticket'][0] 
                        trans_type = "Single" if prefix == 'S' else "Multiple" if prefix == 'M' else "Priority"
                        writer.writerow([log['time'], log['ticket'], log['dept'], trans_type])
                        
                messagebox.showinfo("Export Success", f"Log successfully saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save CSV.\n\n{e}")

    def update_log_display(self):
        self.log_listbox.delete(0, tk.END)
        if not self.print_log:
            self.log_listbox.insert(tk.END, " No tickets printed yet...")
            return
            
        recent = list(reversed(self.print_log[-5:]))
        for item in recent:
            self.log_listbox.insert(tk.END, f" ✅ {item['time']} | {item['ticket']} | {item['dept']}")

    def on_prefix_change(self):
        # --- UPDATED: Route S and M to the same "Regular" memory bank ---
        new_prefix = self.ticket_prefix_var.get()
        new_queue_type = "Regular" if new_prefix in ["S", "M"] else "Priority"

        if new_queue_type != self.last_queue_type:
            # Save the current number to the OLD queue type's memory
            self.counters[self.last_queue_type] = self.ticket_num_var.get()
            
            # Update the display to the NEW queue type's saved number
            self.ticket_num_var.set(self.counters[new_queue_type])
            
            # Remember the new queue type
            self.last_queue_type = new_queue_type

    def master_reset(self):
        confirm = messagebox.askyesno(
            "Master Reset", 
            "Are you sure you want to reset ALL queues (Regular and Priority) back to 001?\n\nThis is usually done at the start of a new day."
        )
        if confirm:
            self.counters = {"Regular": 1, "Priority": 1}
            self.ticket_num_var.set(1)

    def update_window_title(self, *args):
        dept = self.header_2_var.get().strip()
        if dept:
            self.root.title(f"NTC Ticket Generator Pro - {dept}")
        else:
            self.root.title("NTC Ticket Generator Pro")

    def increment_num(self):
        self.ticket_num_var.set(self.ticket_num_var.get() + 1)

    def decrement_num(self):
        if self.ticket_num_var.get() > 1:
            self.ticket_num_var.set(self.ticket_num_var.get() - 1)

    def reset_num(self):
        current_prefix = self.ticket_prefix_var.get()
        q_name = "Regular (Single/Multiple)" if current_prefix in ["S", "M"] else "Priority"
        
        confirm = messagebox.askyesno(
            "Reset Current Queue", 
            f"Are you sure you want to reset the {q_name} queue back to 001?"
        )
        if confirm:
            self.ticket_num_var.set(1)

    def generate_preview_text(self):
        w = 42 
        border_top = "=" * w
        border_dashed = "-" * w
        now_str = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
        num_str = f"{self.ticket_prefix_var.get()}-{self.ticket_num_var.get():03d}"

        lines = [border_top]
        if self.logo_enabled_var.get():
            lines.append("[ LOGO PREVIEW ]".center(w))

        if self.header_1_var.get():
            lines.append(self.header_1_var.get().center(w))
        if self.header_2_var.get():
            lines.append(self.header_2_var.get().center(w))

        lines.append(border_dashed)
        lines.append(now_str.center(w))
        lines.append(border_dashed)
        lines.append("QUEUE NO.".center(w))
        lines.append(num_str.center(w))
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
        
        num_str = f"{self.ticket_prefix_var.get()}-{self.ticket_num_var.get():03d}"
        now_str = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")

        try:
            p = Dummy()
            p.set(align='center')
            w = 42 

            if self.logo_enabled_var.get():
                logo_path = self.logo_file_var.get().strip()
                if os.path.exists(logo_path):
                    try:
                        img = Image.open(logo_path)
                        max_width = 110 
                        if img.width > max_width:
                            ratio = max_width / float(img.width)
                            new_height = int(float(img.height) * float(ratio))
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        p.image(img)
                    except Exception as img_err:
                        print(f"Logo resizing/printing error: {img_err}")

            p.set(align='center', font='b', bold=False)
            p.text(("=" * w) + "\n")

            p.set(align='center', font='b', bold=self.bold_var.get())
            if h1: p.text(h1 + "\n")
            if h2: p.text(h2 + "\n")

            p.set(align='center', font='b', bold=False)
            p.text(("-" * w) + "\n")
            p.text(now_str + "\n")
            p.text(("-" * w) + "\n")

            p.text("QUEUE NO.\n")

            p.set(align='center', font='a', bold=True)
            p.text("\x1d!\x22") 
            p.text(num_str + "\n")

            p.text("\x1d!\x00") 
            
            p.set(align='center', font='b', bold=False)
            p.text(("-" * w) + "\n")
            
            if f1: p.text(f1 + "\n")
            if f2: p.text(f2 + "\n")
            
            p.text(("=" * w) + "\n")

            p.text("\n\n")
            p.cut()

            raw_data = p.output

            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("NTC Ticket", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, raw_data)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)

            self.print_log.append({
                'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ticket': num_str,
                'dept': h2
            })
            self.update_log_display()

            if self.auto_increment_var.get():
                self.increment_num()

        except Exception as e:
            messagebox.showerror("Printing Error", f"Failed to send print job to '{printer_name}'.\n\nDetails: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NTCTicketAppPro(root)
    root.mainloop()