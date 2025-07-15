# -*- coding: utf-8 -*-
"""
Manages running background processes for Alexia.

This module provides a ProcessManager class that can start commands in separate
threads, capture their output in real-time, and manage their lifecycle.
"""

import subprocess
import threading
import time
from typing import Dict, Optional, List

from queue import Queue, Empty

class ManagedProcess:
    """Represents a single managed background process."""
    def __init__(self, command: str):
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.output_queue: Queue = Queue()
        self.is_running = False
        self.pid: Optional[int] = None

    def _reader_thread(self):
        """Reads output from the process and puts it into a queue."""
        if self.process and self.process.stdout:
            for line in iter(self.process.stdout.readline, ''):
                self.output_queue.put(line)
            self.process.stdout.close()
        self.is_running = False

    def start(self):
        """Starts the process and the thread to read its output."""
        if self.is_running:
            return

        # Using PIPE to capture output
        self.process = subprocess.Popen(
            self.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Combine stdout and stderr
            text=True,
            bufsize=1,  # Line-buffered
            universal_newlines=True
        )
        self.pid = self.process.pid
        self.is_running = True
        self.thread = threading.Thread(target=self._reader_thread)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stops the running process."""
        if self.process and self.is_running:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.is_running = False

    def read_output(self) -> List[str]:
        """Reads all available lines from the output queue."""
        lines = []
        while not self.output_queue.empty():
            try:
                lines.append(self.output_queue.get_nowait())
            except Empty:
                break
        return lines

class ProcessManager:
    """A singleton class to manage all background processes."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessManager, cls).__new__(cls)
            cls._instance.processes: Dict[int, ManagedProcess] = {}
        return cls._instance

    def start_process(self, command: str) -> Optional[int]:
        """Starts a new managed process and returns its PID."""
        process = ManagedProcess(command)
        process.start()
        if process.pid:
            self.processes[process.pid] = process
            return process.pid
        return None

    def stop_process(self, pid: int) -> bool:
        """Stops a process by its PID."""
        if pid in self.processes:
            self.processes[pid].stop()
            del self.processes[pid]
            return True
        return False

    def get_output(self, pid: int, wait_for_output_seconds: float = 0) -> Optional[List[str]]:
        """Gets the output of a process by its PID, with an optional wait."""
        if pid in self.processes:
            if wait_for_output_seconds > 0:
                time.sleep(wait_for_output_seconds)
            return self.processes[pid].read_output()
        return None

    def list_pids(self) -> List[int]:
        """Lists the PIDs of all managed processes."""
        return list(self.processes.keys())

