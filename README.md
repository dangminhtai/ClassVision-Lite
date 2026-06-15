# ClassVision Student Recognition - Refactored

## Project Structure

```
refactor/
├── config/                 # Configuration
│   └── settings.py        # All application settings
│
├── database/              # Persistent storage
│   ├── students.py        # Student CRUD operations
│   └── attendance.py      # Attendance session management
│
├── state/                 # Runtime memory
│   └── attendance.py      # In-memory attendance records
│
├── face/                  # Face recognition
│   └── recognizer.py      # InsightFace integration
│
├── ui/                    # User interface
│   ├── components.py      # Reusable UI widgets
│   ├── pages.py           # Page layouts
│   └── main_window.py     # Main window assembly
│
├── workers/               # Background threads
│   └── camera.py          # Camera capture thread
│
├── data/                  # Data files (not code)
│   ├── classvision.db     # SQLite database
│   ├── gallery.npz        # Face embeddings
│   ├── students/          # Student photos
│   └── attendance_sessions/  # CSV exports
│
├── docs/                  # Documentation
│   └── check_lists.md     # Refactor checklist
│
└── main.py               # Application entry point
```

## Module Responsibilities

### config/
Configuration only. Contains all application settings and paths.

**Allowed:**
- Constants
- File paths
- Configuration values

**Forbidden:**
- Business logic
- Database access
- UI code

### database/
Persistent storage only. Handles SQLite and CSV operations.

**Allowed:**
- CRUD operations
- File I/O
- Query execution

**Forbidden:**
- UI updates
- Runtime state
- AI logic

### state/
Runtime memory only. Manages application state during execution.

**Allowed:**
- In-memory caches
- Current session data
- Temporary state

**Forbidden:**
- File I/O
- Database writes
- UI logic

### face/
Face recognition only. Encapsulates InsightFace and matching logic.

**Allowed:**
- Model loading
- Face detection
- Embedding comparison

**Forbidden:**
- UI code
- Database access
- File management

### ui/
User interface only. Everything related to PyQt6 widgets.

**Allowed:**
- Widget creation
- Layout management
- Event handlers (delegates to main.py)

**Forbidden:**
- Direct database access
- AI logic
- Background threads

### workers/
Background threads only. Handles async operations.

**Allowed:**
- Threading
- Camera capture
- Async processing

**Forbidden:**
- Direct UI updates (use callbacks)
- Database writes
- Configuration changes

## Import Rules

Use absolute imports from project root:

```python
from config.settings import DATA_DIR
from database.students import get_students
from face.recognizer import recognize_faces_in_frame
from ui.components import create_button
from workers.camera import start_camera
from state.attendance import add_attendance_record
```

## Dependency Flow

```
main.py
 ├── ui/           (coordinates everything)
 ├── workers/      (provides data via callbacks)
 ├── database/     (data persistence)
 ├── face/         (AI processing)
 ├── state/        (runtime memory)
 └── config/       (settings)
```

Lower-level modules never import higher-level modules.

## Running the Application

```bash
python main.py
```

## Key Principles

1. **One Responsibility per File** - Each file has one clear purpose
2. **No Circular Dependencies** - Import flow is strictly one-way
3. **Preserve Behavior** - Refactor did not change functionality
4. **Easy Navigation** - Find features by reading folder names
5. **University Project** - No enterprise patterns, keep it simple
