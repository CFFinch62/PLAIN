"""Debug manager for PLAIN IDE - handles communication with the Go runtime debugger"""

import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QProcess


class DebugManager(QObject):
    """Manages debug sessions with the PLAIN runtime"""
    
    # Signals
    stopped = pyqtSignal(int, str, list)  # line, reason, call_stack
    terminated = pyqtSignal()
    variables_received = pyqtSignal(dict)
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        args = ["run", "./cmd/plain/", "--debug", file_path]
        if breakpoints:
            bp_str = ",".join(str(line) for line in sorted(breakpoints))
            args.append(f"--breakpoints={bp_str}")

        # Connect signals - all reading happens in main thread via signals
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

        # Start the process
        self.process.start("go", args)

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
                except json.JSONDecodeError as e:
                    self.error_received.emit(f"JSON parse error: {e} - data: {line[:100]}")

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

