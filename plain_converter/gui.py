"""
PLAIN ↔ Python Converter — Standalone tkinter GUI

Launch with:
    python3 -m plain_converter --gui
    python3 plain_converter/gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

from plain_converter import __version__


class ConverterApp(tk.Tk):
    """Minimal standalone GUI for the PLAIN ↔ Python converter."""

    def __init__(self):
        super().__init__()
        self.title(f"PLAIN ↔ Python Converter  v{__version__}")
        self.geometry("820x620")
        self.minsize(600, 400)
        self._source_path: Path | None = None
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self):
        # File picker row
        file_frame = ttk.Frame(self, padding=8)
        file_frame.pack(fill=tk.X)

        ttk.Label(file_frame, text="Source file:").pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse…", command=self._browse).pack(side=tk.RIGHT)
        self._path_var = tk.StringVar()
        self._path_entry = ttk.Entry(file_frame, textvariable=self._path_var)
        self._path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))

        # Direction + convert row
        action_frame = ttk.Frame(self, padding=(8, 0, 8, 4))
        action_frame.pack(fill=tk.X)

        self._dir_var = tk.StringVar(value="(auto-detect)")
        ttk.Label(action_frame, text="Direction:").pack(side=tk.LEFT)
        self._dir_label = ttk.Label(action_frame, textvariable=self._dir_var,
                                     foreground="gray")
        self._dir_label.pack(side=tk.LEFT, padx=(6, 12))
        ttk.Button(action_frame, text="Convert", command=self._convert).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Save Output…", command=self._save).pack(
            side=tk.LEFT, padx=(8, 0))

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=8, pady=4)

        # Output area
        self._output = scrolledtext.ScrolledText(self, wrap=tk.NONE, font=("monospace", 11))
        self._output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # Status bar
        self._status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self._status_var, relief=tk.SUNKEN,
                               anchor=tk.W, padding=(6, 2))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Actions ──────────────────────────────────────────────────────

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select source file",
            filetypes=[
                ("PLAIN files", "*.plain"),
                ("Python files", "*.py"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._path_var.set(path)
            self._source_path = Path(path)
            self._update_direction()

    def _update_direction(self):
        if self._source_path is None:
            self._dir_var.set("(auto-detect)")
            return
        ext = self._source_path.suffix.lower()
        if ext == ".plain":
            self._dir_var.set("PLAIN → Python")
        elif ext == ".py":
            self._dir_var.set("Python → PLAIN")
        else:
            self._dir_var.set("(unknown file type)")

    def _convert(self):
        raw_path = self._path_var.get().strip()
        if not raw_path:
            messagebox.showwarning("No file", "Please select a source file first.")
            return

        src = Path(raw_path)
        if not src.is_file():
            messagebox.showerror("Not found", f"File does not exist:\n{src}")
            return

        ext = src.suffix.lower()
        if ext not in (".plain", ".py"):
            messagebox.showwarning(
                "Unknown type",
                "Can only convert .plain or .py files.\n"
                f"Got: {src.name}",
            )
            return

        self._source_path = src
        self._update_direction()
        self._status_var.set(f"Converting {src.name}…")
        self.update_idletasks()

        try:
            source_code = src.read_text(encoding="utf-8")

            if ext == ".plain":
                from plain_converter.converter.plain_to_python import PlainToPythonConverter
                converter = PlainToPythonConverter(preserve_comments=True)
            else:
                from plain_converter.converter.python_to_plain import PythonToPlainConverter
                converter = PythonToPlainConverter(preserve_comments=True)

            result = converter.convert(source_code)

            self._output.delete("1.0", tk.END)
            self._output.insert(tk.END, result.code)

            parts = [f"Converted {src.name}"]
            if result.errors:
                parts.append(f"{len(result.errors)} error(s)")
            if result.warnings:
                parts.append(f"{len(result.warnings)} warning(s)")
            self._status_var.set("  |  ".join(parts))

            if result.errors:
                detail = "\n".join(result.errors)
                messagebox.showerror("Conversion errors", detail)

        except Exception as exc:
            self._status_var.set("Conversion failed")
            messagebox.showerror("Error", str(exc))

    def _save(self):
        content = self._output.get("1.0", tk.END).rstrip("\n")
        if not content:
            messagebox.showinfo("Nothing to save", "Run a conversion first.")
            return

        # Suggest a filename based on the source
        initial = ""
        if self._source_path:
            ext = ".py" if self._source_path.suffix.lower() == ".plain" else ".plain"
            initial = self._source_path.stem + ext

        path = filedialog.asksaveasfilename(
            title="Save converted file",
            initialfile=initial,
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("PLAIN files", "*.plain"),
                ("All files", "*.*"),
            ],
        )
        if path:
            Path(path).write_text(content + "\n", encoding="utf-8")
            self._status_var.set(f"Saved to {Path(path).name}")


def run_gui():
    """Entry point called from the CLI (--gui) or directly."""
    app = ConverterApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()

