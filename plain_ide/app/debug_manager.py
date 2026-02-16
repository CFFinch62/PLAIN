"""Debug manager for PLAIN IDE - handles communication with the Go runtime debugger"""

import shutil
import sys
import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QProcess

from plain_ide.app.settings import SettingsManager


class DebugManager(QObject):
    """Manages debug sessions with the PLAIN runtime"""
    
    # Signals
    stopped = pyqtSignal(int, str, list)  # line, reason, call_stack
    terminated = pyqtSignal()
    variables_received = pyqtSignal(dict)
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    
    def __init__(self, parent=None, settings_manager: SettingsManager = None):
        super().__init__(parent)
        self.settings = settings_manager
        self.process: QProcess = None
        self._debugging = False
        self._buffer = ""  # Buffer for partial JSON messages

    def start_debug(self, file_path: str, breakpoints: set = None):
        """Start debugging a PLAIN file"""
        if self._debugging:
            self.stop_debug()

        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(Path(__file__).parent.parent.parent))

        # Build command arguments
        # Determine interpreter to use
        interpreter = self._find_plain_interpreter()
        if not interpreter:
            self.error_received.emit("PLAIN interpreter not found. Please configure it in settings.")
            return False

        # Build command arguments
        # If we found the 'plain' executable, use it directly
        if interpreter.endswith("plain") or interpreter.endswith("plain.exe"):
             args = []

             # Add --project-root flag if configured
             if self.settings and self.settings.settings.project_root_path:
                 args.extend(["--project-root", self.settings.settings.project_root_path])

             args.extend(["--debug", file_path])
             program = interpreter
        else:
            # Fallback for dev environment (go run)
            args = ["run", "./cmd/plain/", "--debug", file_path]
            program = "go"

        if breakpoints:
             bp_str = ",".join(str(line) for line in sorted(breakpoints))
             args.append(f"--breakpoints={bp_str}")
        else:
             # Stop on entry (line 1) if no breakpoints
             args.append("--breakpoints=1")

        # Message is now constructed earlier, remove old append logic
        # if breakpoints:
        #     bp_str = ",".join(str(line) for line in sorted(breakpoints))
        #     args.append(f"--breakpoints={bp_str}")

        # Connect signals - all reading happens in main thread via signals
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

        # Start the process
        self.process.start(program, args)

        if not self.process.waitForStarted(5000):
            self.error_received.emit("Failed to start debug process")
            return False

        self._debugging = True
        self._buffer = ""

        return True

    def stop_debug(self):
        """Stop the current debug session"""
        self._debugging = False

        if self.process:
            self.send_command({"command": "quit"})
            self.process.waitForFinished(1000)
            if self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()
            self.process = None
            
    def send_command(self, command: dict):
        """Send a debug command to the runtime"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            json_str = json.dumps(command) + "\n"
            self.process.write(json_str.encode('utf-8'))
    
    def continue_execution(self):
        """Continue execution"""
        self.send_command({"command": "continue"})
        
    def step_into(self):
        """Step into the next statement"""
        self.send_command({"command": "step_into"})
        
    def step_over(self):
        """Step over the next statement"""
        self.send_command({"command": "step_over"})
        
    def step_out(self):
        """Step out of the current function"""
        self.send_command({"command": "step_out"})
        
    def get_variables(self):
        """Request current variables"""
        self.send_command({"command": "get_variables"})
        
    def set_breakpoints(self, breakpoints: list):
        """Update breakpoints during debug session"""
        self.send_command({"command": "set_breakpoints", "breakpoints": breakpoints})
        
    def _on_stdout(self):
        """Handle stdout from process - called in main thread via signal"""
        if not self.process:
            return

        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        self._buffer += data

        # Process complete lines (JSON events are newline-delimited)
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            line = line.strip()
            if line:
                try:
                    event = json.loads(line)
                    self._handle_event(event)
                except json.JSONDecodeError:
                    # Not a JSON event, treat as standard program output
                    # Restore newline that was stripped
                    self.output_received.emit(line + "\n")

    def _handle_event(self, event: dict):
        """Handle debug event from runtime"""
        event_type = event.get("event", "")

        if event_type == "stopped":
            line = event.get("line", 0)
            reason = event.get("reason", "unknown")
            call_stack = event.get("call_stack", [])
            self.stopped.emit(line, reason, call_stack)
            # Auto-request variables when stopped
            self.get_variables()

        elif event_type == "terminated":
            self.terminated.emit()
            self._debugging = False

        elif event_type == "variables":
            variables = event.get("variables", {})
            self.variables_received.emit(variables)

        elif event_type == "output":
            output = event.get("output", "")
            self.output_received.emit(output)

    def _on_stderr(self):
        """Handle stderr from process"""
        if self.process:
            data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
            self.error_received.emit(data)

    def _on_finished(self, exit_code, exit_status):
        """Handle process completion"""
        self._debugging = False
        self.terminated.emit()

    @property
    def is_debugging(self) -> bool:
        """Check if debugging is active"""
        return self._debugging


    def _find_plain_interpreter(self) -> str:
        """Find the PLAIN interpreter"""
        # Strategy 1: Check settings for configured path
        if self.settings and self.settings.settings.plain_interpreter_path:
            path = Path(self.settings.settings.plain_interpreter_path)
            if path.exists():
                return str(path)
        
        # Strategy 2: Check same directory as IDE executable (frozen)
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            plain_exe = exe_dir / "plain"
            if plain_exe.exists():
                return str(plain_exe)
        else:
            # Strategy 3: Check development build location
            # If running from source, look in project root/plain
            dev_plain = Path(__file__).parent.parent.parent / "plain"
            if dev_plain.exists():
                return str(dev_plain)

        # Strategy 4: Check PATH
        plain_in_path = shutil.which("plain")
        if plain_in_path:
            return plain_in_path

        # Fallback to 'go run' only if we are in source dev mode and go is available
        # This preserves old behavior for development if 'plain' binary is missing
        if not getattr(sys, 'frozen', False) and shutil.which("go"):
            return "go" 

        return None
