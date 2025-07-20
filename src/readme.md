# Smart Hospital Predictive System

A time and energy optimization demo for hospital equipment management using predictive analytics.

## Project Structure

The application is modularized into the following files:

### Core Files

- **`gui.py`** - Main application file containing the GUI interface and application logic
- **`simulation.py`** - Core simulation engine with Equipment, Room, Actor, and HospitalSimulation classes
- **`models.py`** - Data models, enums, and type definitions
- **`metrics.py`** - Logging, metrics tracking, and performance analysis

### File Descriptions

#### `models.py`
Contains the fundamental data structures:
- `RoomType` - Enum for different hospital room types
- `ActorType` - Enum for different actor types (Staff, Doctor, Patient)
- `EquipmentState` - Enum for equipment states (Off, Starting, Ready, etc.)
- `Position` - Dataclass for actor positions

#### `simulation.py`
Core simulation logic:
- `Equipment` - Individual medical equipment with power management and state transitions
- `Room` - Hospital rooms containing equipment and managing occupancy
- `Actor` - People moving through the hospital (staff, doctors, patients)
- `PredictionEngine` - Machine learning-like prediction of movement patterns
- `HospitalSimulation` - Main simulation coordinator

#### `metrics.py`
Performance tracking and analysis:
- `ActivityLogger` - Handles all activity logging with timestamps
- `MetricsTracker` - Tracks performance metrics and movement data
- `PerformanceAnalyzer` - Advanced analysis and recommendations

#### `gui.py`
Main application interface:
- `HospitalGUI` - Complete graphical user interface
- Real-time visualization of hospital layout and equipment
- Interactive drag-and-drop actor movement
- Performance metrics dashboard
- Activity logging display

## How to Run

1. **Prerequisites**: Ensure you have Python 3.7+ with tkinter installed

2. **Run the application**:
   ```bash
   python gui.py
   ```