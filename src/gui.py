import tkinter as tk
from tkinter import messagebox, filedialog
import configparser
import subprocess
from pathlib import Path
import threading
import sys

try:
    import pkg_resources
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
    import pkg_resources

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JIRA Issue Downloader")
        self.geometry("600x750")

        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / 'config.ini'
        self.config = configparser.ConfigParser()

        self.create_widgets()
        self.load_config()
        self.check_requirements()

    def create_widgets(self):
        # Frame for settings
        settings_frame = tk.LabelFrame(self, text="Configuration", padx=10, pady=10)
        settings_frame.pack(padx=10, pady=10, fill="x", expand=False)

        self.entries = {}
        settings = [
            "project_name",
            "excel_file",
            "gerrit_username",
            "gerrit_password",
            "sharp_name",
            "fih_name"
        ]

        for i, setting in enumerate(settings):
            label = tk.Label(settings_frame, text=f"{setting.replace('_', ' ').title()}:")
            label.grid(row=i, column=0, sticky="w", pady=2)

            if setting == "excel_file":
                excel_frame = tk.Frame(settings_frame)
                excel_frame.grid(row=i, column=1, sticky="ew", pady=2)
                excel_frame.columnconfigure(0, weight=1)

                entry = tk.Entry(excel_frame, width=50)
                entry.grid(row=0, column=0, sticky="ew")

                browse_button = tk.Button(excel_frame, text="Browse...", command=self.browse_excel_file)
                browse_button.grid(row=0, column=1, padx=(5, 0))
                self.entries[setting] = entry
            elif setting == "gerrit_password":
                password_frame = tk.Frame(settings_frame)
                password_frame.grid(row=i, column=1, sticky="ew", pady=2)
                password_frame.columnconfigure(0, weight=1)

                entry = tk.Entry(password_frame, width=50, show="*")
                entry.grid(row=0, column=0, sticky="ew")
                self.entries[setting] = entry

                self.show_password_var = tk.BooleanVar()
                show_password_check = tk.Checkbutton(
                    password_frame,
                    text="Show",
                    variable=self.show_password_var,
                    command=self.toggle_password_visibility
                )
                show_password_check.grid(row=0, column=1, padx=(5, 0))
            else:
                entry = tk.Entry(settings_frame, width=60)
                entry.grid(row=i, column=1, sticky="ew", pady=2)
                self.entries[setting] = entry

        settings_frame.columnconfigure(1, weight=1)

        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(padx=10, pady=(0, 10), fill="x")

        self.save_button = tk.Button(button_frame, text="Save Config", command=self.save_config)
        self.save_button.pack(side="left", padx=5)

        self.run_button = tk.Button(
            button_frame,
            text="Run Downloader",
            command=self.run_script_thread,
            bg="lightblue",
            font=("Helvetica", 10, "bold")
        )
        self.run_button.pack(side="right", padx=5)

        # Frame for requirements
        self.req_frame = tk.LabelFrame(self, text="Requirements Status", padx=10, pady=10)
        self.req_frame.pack(padx=10, pady=10, fill="x", expand=False)

        # Frame for output
        output_frame = tk.LabelFrame(self, text="Output", padx=10, pady=10)
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill="both", expand=True)

    def load_config(self):
        if not self.config_file.exists():
            messagebox.showwarning("Warning", f"config.ini not found at {self.config_file}.\nA default one will be created on save.")
            return

        self.config.read(self.config_file)
        if 'settings' in self.config:
            for key, entry in self.entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, self.config['settings'].get(key, ''))

    def save_config(self):
        if 'settings' not in self.config:
            self.config.add_section('settings')

        for key, entry in self.entries.items():
            self.config.set('settings', key, entry.get())

        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config.ini:\n{e}")

    def check_requirements(self):
        # Clear existing widgets in the frame
        for widget in self.req_frame.winfo_children():
            widget.destroy()

        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            label = tk.Label(self.req_frame, text="requirements.txt not found.", fg="red")
            label.pack()
            return

        with open(requirements_file, 'r') as f:
            requirements = f.readlines()

        for i, req in enumerate(requirements):
            req = req.strip()
            if not req or req.startswith('#'):
                continue

            try:
                pkg_resources.get_distribution(req.split('>=')[0])
                status = "Installed"
                status_color = "green"
                has_install_button = False
            except pkg_resources.DistributionNotFound:
                status = "Missing"
                status_color = "red"
                has_install_button = True

            req_frame_inner = tk.Frame(self.req_frame)
            req_frame_inner.pack(fill='x')

            label = tk.Label(req_frame_inner, text=req)
            label.pack(side="left", padx=5)

            status_label = tk.Label(req_frame_inner, text=status, fg=status_color)
            status_label.pack(side="right", padx=5)

            if has_install_button:
                install_button = tk.Button(
                    req_frame_inner,
                    text="Install",
                    command=lambda r=req: self.install_package_thread(r)
                )
                install_button.pack(side="right")

    def install_package_thread(self, package_name):
        thread = threading.Thread(target=self.install_package, args=(package_name,))
        thread.daemon = True
        thread.start()

    def install_package(self, package_name):
        self.run_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.log_output(f"Installing {package_name}...\n")
        try:
            python_executable = sys.executable
            process = subprocess.Popen(
                [python_executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            for line in iter(process.stdout.readline, ''):
                self.log_output(line)
            process.stdout.close()
            process.wait()
            self.log_output(f"\nFinished installing {package_name}.\n")
        except Exception as e:
            self.log_output(f"An error occurred during installation: {e}\n")
        finally:
            self.after(0, self.check_requirements)
            self.enable_buttons()

    def toggle_password_visibility(self):
        password_entry = self.entries.get("gerrit_password")
        if password_entry:
            if self.show_password_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="*")

    def browse_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if file_path:
            self.entries["excel_file"].delete(0, tk.END)
            self.entries["excel_file"].insert(0, file_path)

    def run_script_thread(self):
        # Show a warning messagebox before running the script
        if not messagebox.askokcancel("Ready to Run?", "Please make sure all Firefox windows are closed before proceeding."):
            return # Stop if the user clicks Cancel

        self.run_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_script)
        thread.daemon = True
        thread.start()

    def run_script(self):
        main_script_path = self.project_root / "src" / "main.py"
        if not main_script_path.exists():
            self.log_output(f"Error: main.py not found at {main_script_path}")
            self.enable_buttons()
            return

        try:
            # Ensure the command uses the same Python interpreter that's running the GUI
            python_executable = sys.executable
            process = subprocess.Popen(
                [python_executable, str(main_script_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.project_root
            )

            # Send a newline character to the process's stdin to bypass the input prompt
            process.stdin.write('\n')
            process.stdin.flush()

            for line in iter(process.stdout.readline, ''):
                self.log_output(line)

            process.stdout.close()
            process.wait()

        except Exception as e:
            self.log_output(f"An error occurred while running the script:\n{e}")
        finally:
            self.after(0, self.show_completion_message)
            self.enable_buttons()

    def show_completion_message(self):
        project_name = self.entries["project_name"].get()
        if not project_name:
            messagebox.showinfo("Download Complete", "Download process finished.")
            return

        output_folder = self.project_root / "output" / project_name
        if messagebox.askyesno(
            "Download Complete",
            f"Download process finished.\nOutput folder: {output_folder}\n\nDo you want to open the output folder?"
        ):
            self.open_folder(output_folder)

    def open_folder(self, path):
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", str(path)])
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", str(path)])
            else:  # Linux
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            self.log_output(f"Failed to open folder: {e}\n")

    def log_output(self, message):
        def append():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, message)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.after(0, append)

    def enable_buttons(self):
        def enable():
            self.run_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
        self.after(0, enable)

if __name__ == "__main__":
    app = App()
    app.mainloop()
