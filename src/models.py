from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class RoomType(Enum):
    LOBBY = "Lobby"
    ICU = "ICU"
    RADIOLOGY = "Radiology Room"
    LAB = "Lab"
    PATIENT_ROOM = "Patient Room"
    EMERGENCY_ROOM = "Emergency Room"

class ActorType(Enum):
    STAFF = "Staff"
    DOCTOR = "Doctor"
    PATIENT = "Patient"

class EquipmentState(Enum):
    OFF = "OFF"
    STARTING = "STARTING"
    PRELOADED = "PRELOADED"
    READY = "READY"
    IN_USE = "IN_USE"
    SLEEP = "SLEEP"
    SHUTTING_DOWN = "SHUTTING_DOWN"

@dataclass
class Position:
    x: int
    y: int
    room: RoomType