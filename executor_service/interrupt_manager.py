import threading
from pynput import keyboard as kb
from rich.console import Console

console = Console()


class InterruptManager:
    """
    Emergency interruption handler.
    
    Listens for ESC key press in a background thread.
    When triggered, sets a threading.Event that the executor checks
    between every action to halt immediately.
    """

    def __init__(self):
        self._interrupted = threading.Event()
        self._listener = None

    def start(self) -> None:
        """Start listening for interrupt signals in the background."""
        self._interrupted.clear()
        self._listener = kb.Listener(on_press=self._on_key_press)
        self._listener.daemon = True
        self._listener.start()
        console.print("  [dim][Interrupt] ESC listener active — press ESC to halt execution.[/dim]")

    def stop(self) -> None:
        """Stop the interrupt listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_key_press(self, key) -> None:
        """Callback: set interrupt flag on ESC."""
        try:
            if key == kb.Key.esc:
                self._interrupted.set()
                console.print("\n  [bold red]⚠ ESC PRESSED — Interrupting execution![/bold red]")
        except Exception:
            pass

    @property
    def is_interrupted(self) -> bool:
        """Check if an interrupt has been signalled."""
        return self._interrupted.is_set()

    def reset(self) -> None:
        """Clear the interrupt flag for a new execution cycle."""
        self._interrupted.clear()

    def request_interrupt(self) -> None:
        """Programmatically trigger an interrupt (e.g., from voice command or timeout)."""
        self._interrupted.set()
        console.print("  [bold red][Interrupt] Programmatic interrupt triggered.[/bold red]")
