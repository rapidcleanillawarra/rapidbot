# Base process class that all processes inherit from
from abc import ABC, abstractmethod
from utils.audio import beep


class BaseProcess(ABC):
    """Base class for all automation processes."""
    
    # Override in subclass
    PROCESS_NUMBER = 0
    PROCESS_NAME = "Base Process"
    
    def __init__(self, app):
        """
        Initialize the process with reference to main app.
        
        Args:
            app: Reference to ChromeClickerApp instance
        """
        self.app = app
    
    @abstractmethod
    def run(self) -> bool:
        """
        Execute the process.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def play_beep(self) -> None:
        """Play the beep sound for this process."""
        beep(self.PROCESS_NUMBER)
    
    def update_log(self, message: str) -> None:
        """Update the GUI log area."""
        self.app.root.after(0, lambda: self.app.update_log(message))
    
    def update_status(self, status: str, color: str = None) -> None:
        """Update the GUI status indicator."""
        if color is None:
            color = self.app.warning_color
        self.app.root.after(0, lambda: self.app.update_status(status, color))
    
    def log_start(self) -> None:
        """Log process start to console."""
        print(f"\n=== PROCESS {self.PROCESS_NUMBER}: {self.PROCESS_NAME} ===", flush=True)
    
    def log_complete(self) -> None:
        """Log process completion to console."""
        print(f"=== PROCESS {self.PROCESS_NUMBER} COMPLETE ===\n", flush=True)
    
    def log_failed(self) -> None:
        """Log process failure to console."""
        print(f"=== PROCESS {self.PROCESS_NUMBER} FAILED ===\n", flush=True)
