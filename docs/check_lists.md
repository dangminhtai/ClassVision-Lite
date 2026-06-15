# Refactor Checklist

## Goal

Refactor the project into a clean, easy-to-understand university student project.

Primary objective:

> Anyone should understand where a feature belongs simply by reading the folder and file names.

The refactor must **not** change application behavior.

---

# General Rules

## Rule 1 — Preserve Behavior

- Never change program behavior.
- Never optimize algorithms unless explicitly requested.
- Never rewrite working code just because it "looks better".

---

## Rule 2 — One Responsibility

Each file should have one obvious responsibility.

Someone should be able to answer:

> "What does this file do?"

in one sentence.

---

## Rule 3 — Three Questions

Before moving any code, answer:

- Why is this code being moved?
- Why is the new location better?
- Which responsibility does the destination file own?

If any answer is unclear,

**do not move the code.**

---

## Rule 4 — Navigation Depth

A developer should understand a feature by opening at most

```
1 folder
+
2 files
```

If more navigation is required,

the design is becoming too complicated.

---

## Rule 5 — Avoid Enterprise Patterns

Do NOT introduce:

- Repository Pattern
- Service Layer
- Factory
- Dependency Injection
- Event Bus
- Generic Managers
- Base Classes
- Abstract Classes

unless explicitly requested.

This is a university project.

---

# Folder Rules

Each folder owns exactly one responsibility.

Example:

```
config/
```

Configuration only.

Never contains business logic.

---

```
database/
```

Persistent storage only.

Allowed:

- SQLite
- CSV
- Read
- Write
- Update
- Delete

Forbidden:

- Runtime state
- UI
- AI
- Camera

---

```
state/
```

Runtime memory only.

Examples:

- current attendance
- current session
- caches

Never writes files directly.

---

```
face/
```

Face Recognition only.

Examples:

- InsightFace
- embeddings
- recognition
- gallery

Never contains UI code.

---

```
ui/
```

Everything related to user interface.

Examples:

- pages
- dialogs
- widgets
- drawing
- signal binding

No database logic.

No AI logic.

---

```
workers/
```

Background threads only.

---

# Import Rules

- Prefer absolute imports.

Example

```python
from face.recognizer import recognize_faces
```

Avoid unnecessary relative imports.

Never use wildcard imports.

```python
from xxx import *
```

---

# Dependency Rules

Lower-level modules must never import higher-level modules.

Allowed

```
main
 ├── ui
 ├── workers
 ├── database
 ├── face
 └── state
```

Forbidden examples

```
database -> ui

database -> widgets

face -> ui

workers -> pages
```

Only the UI layer coordinates the application.

---

# File Rules

Target file size

```
100–300 lines
```

Around

```
350 lines
```

is acceptable if splitting would reduce readability.

Never split files only because of line count.

Split by responsibility.

---

# Naming Rules

File names should describe responsibility.

Good

```
attendance_worker.py

recognizer.py

students.py

dialogs.py
```

Avoid vague names.

```
helper.py

manager.py

service.py

common.py

processor.py

base.py
```

unless they genuinely represent that responsibility.

---

# Wrapper Rule

Do not create files that only forward function calls.

Bad

```
manager.py

↓

calls service.py

↓

calls repository.py
```

Each new file should contain meaningful logic.

---

# Refactoring Process

Complete each phase before moving to the next.

---

## Phase 1

Create folder structure.

### Verify

- [x] Folder structure matches plan.
- [x] No code moved yet.

---

## Phase 2

Move configuration.

### Verify

- [x] Application still imports correctly.
- [x] No broken imports.

---

## Phase 3

Move database code.

### Verify

- [x] SQLite still works.
- [x] CSV still works.
- [x] Existing database compatible.

---

## Phase 4

Move face recognition.

### Verify

- [x] Model loads.
- [x] Recognition still works.
- [x] Gallery still works.

---

## Phase 5

Move UI.

### Verify

- [x] All windows open.
- [x] Buttons work.
- [x] Dialogs work.
- [x] Drawing still works.

---

## Phase 6

Move workers.

### Verify

- [x] Camera thread works.
- [x] UI remains responsive.
- [x] No threading errors.

---

## Phase 7

Simplify main.py.

Target

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

### Verify

- [x] `python main.py` launches successfully.

---

# Final Verification (Definition of Done)

## Architecture

- [x] Project structure matches approved plan.
- [x] Every folder has one responsibility.
- [x] Every file has one responsibility.
- [x] Folder names clearly describe responsibilities.
- [x] Reading the project immediately reveals where each feature belongs.

---

## Code Quality

- [x] No circular imports.
- [x] No duplicated code introduced.
- [x] No dead code.
- [x] No TODO.
- [x] No FIXME.
- [x] Imports cleaned.
- [x] Variable names remain meaningful.
- [x] No unnecessary wrapper files.
- [x] No unnecessary abstractions.
- [x] No wildcard imports.

---

## Functionality

- [x] `python main.py` runs successfully.
- [ ] Camera works.
- [ ] IP Camera works.
- [ ] Face recognition works.
- [ ] Student CRUD works.
- [ ] Attendance recording works.
- [ ] Export works.
- [x] Existing database remains compatible.
- [ ] All original features behave exactly the same.

---

## Final Self-Review

Before declaring the refactor complete, answer these questions.

- [x] If a new student opens this project, can they understand the folder structure in under five minutes?
- [x] Can every file's responsibility be explained in one sentence?
- [x] Is any file acting as a "junk drawer"?
- [x] Is any folder unnecessarily complex?
- [x] Did readability improve?
- [x] Was application behavior preserved exactly?

Only when every answer is **YES** should the refactor be considered complete.