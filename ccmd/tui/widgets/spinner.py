"""Named spinner widget."""

from __future__ import annotations

from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Static

from ccmd.tui.ascii import SPINNER_FRAMES


class Spinner(Static):
    """Braille spinner with status label."""

    label: reactive[str] = reactive("loading…")
    active: reactive[bool] = reactive(True)
    _frame: int = 0
    _timer: Timer | None = None

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        if not self.active:
            self.update("")
            return
        frame = SPINNER_FRAMES[self._frame % len(SPINNER_FRAMES)]
        self._frame += 1
        self.update(f"{frame}  {self.label}")

    def stop(self, final: str = "") -> None:
        self.active = False
        self.update(final)
