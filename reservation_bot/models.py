from dataclasses import dataclass
from enum import Enum


class ReservationPeriod(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"


@dataclass(frozen=True, slots=True)
class User:
    name: str
    email: str
    student_id: str


@dataclass(frozen=True, slots=True)
class Slot:
    date: str
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int

    @property
    def start_time(self) -> str:
        return (
            f"{self.start_hour:02d}:"
            f"{self.start_minute:02d}"
        )

    @property
    def end_time(self) -> str:
        return (
            f"{self.end_hour:02d}:"
            f"{self.end_minute:02d}"
        )

    @property
    def label(self) -> str:
        return f"{self.start_time}-{self.end_time}"


@dataclass(slots=True)
class ReservationResult:
    user: User
    period: ReservationPeriod
    success: bool
    message: str
    screenshot_path: str | None = None