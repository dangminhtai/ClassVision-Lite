# LECTURER CRITICAL REVIEW
## Digital Image Processing Final Project

**Reviewer Role:** Senior University Lecturer  
**Review Date:** June 15, 2026  
**Project:** ClassVision Student Recognition System  
**Review Mindset:** STRICT - Assuming oral defense examination

---

## CATEGORY 1: Project Structure
**Score: 72/100**

### What I See:
```
config/    - Configuration
database/  - Database operations
state/     - Runtime memory
face/      - Face recognition
ui/        - User interface
workers/   - Background threads
```

### Strengths:
- Folder names are self-explanatory
- Clear separation of concerns
- No unnecessary nesting
- Easy to locate major components

### Critical Issues (-28 points):

**1. Over-abstraction for student level (-10 points)**
- Why do you need `state/` AND `database/`? A typical student would just put everything in one place.
- The separation between "runtime state" and "persistent state" is enterprise thinking, not student thinking.
- Question during defense: "Why didn't you just use a global variable in main.py?"

**2. `workers/` folder with single file (-8 points)**
- Only contains `camera.py`
- Creates unnecessary navigation depth
- Question: "Why not just name it `camera.py` at root level?"

**3. Missing obvious structure (-10 points)**
- Where are the image processing utilities?
- Where are preprocessing functions?
- Where is the face detection pipeline explanation?
- A DIP project should have folders like `preprocessing/`, `detection/`, `feature_extraction/`

### Verdict:
Structure is TOO clean and organized for a typical student project. Real students usually have:
- Some files at root level
- Maybe 1-2 folders max
- Less "perfect" organization

---

## CATEGORY 2: File Responsibility
**Score: 78/100**

### File-by-File Analysis:

| File | One-Sentence Summary | Can Student Explain? |
|------|---------------------|---------------------|
| `main.py` | Coordinates UI setup and event handlers | ⚠️ Maybe - but it's 350+ lines |
| `config/settings.py` | Stores configuration constants | ✅ Yes - straightforward |
| `face/recognizer.py` | Loads InsightFace and matches faces | ✅ Yes - core DIP logic |
| `workers/camera.py` | Captures frames in background thread | ⚠️ Risky - threading is advanced |
| `ui/components.py` | Creates reusable PyQt widgets | ✅ Yes - UI code |
| `ui/pages.py` | Builds page layouts | ⚠️ Maybe - 200+ lines |
| `ui/main_window.py` | Assembles main window | ✅ Yes - simple |
| `database/students.py` | CRUD for student table | ✅ Yes - basic SQL |
| `database/attendance.py` | CSV export functions | ✅ Yes - simple |
| `state/attendance.py` | In-memory attendance dict | ⚠️ Suspicious - why separate file? |

### Critical Issues (-22 points):

**1. main.py is too long (-10 points)**
- 350+ lines with 4 massive setup functions
- Each setup function is 80-100 lines
- During defense: "Walk me through setup_app_logic line by line"
- Student will struggle to remember what `.itemAt(1).widget().layout().itemAt(1).layout().itemAt(1).widget()` does

**2. state/attendance.py is pointless (-8 points)**
- 35 lines just to wrap a global dictionary
- Could be 3 lines in main.py:
  ```python
  attendance = {}
  ```
- This screams "AI generated abstraction"

**3. workers/camera.py threading complexity (-4 points)**
- Dual-thread architecture (camera + AI loop)
- Uses global variables for thread communication
- Question: "Why do you need two threads? Why not one?"
- Typical student answer: "Um... to make it faster?"
- Real answer requires understanding of GIL, which most students don't have

---

## CATEGORY 3: Student Readability
**Score: 65/100**

### Readability Test: Can a 2nd-year student understand this?

**Easy to understand:**
- ✅ `config/settings.py` - Just constants
- ✅ `database/students.py` - Basic CRUD
- ✅ `face/recognizer.py` - NumPy operations are standard DIP

**Confusing parts:**
- ❌ Why is `state/` separate from `main.py`?
- ❌ The callback pattern in `workers/camera.py`
- ❌ `_GuiInvoker` class using signals - WTF is this?
- ❌ Nested widget access: `.itemAt(1).widget().layout().itemAt(1)...`
- ❌ Lambda functions everywhere in button connections

### Major Issues (-35 points):

**1. The `_GuiInvoker` pattern (-15 points)**
```python
class _GuiInvoker(QObject):
    invoke_signal = pyqtSignal(object)

_invoker = _GuiInvoker()
_invoker.invoke_signal.connect(lambda func: func())
```
- This is ADVANCED PyQt threading
- 90% of students have never seen this
- Question: "Explain what invoke_signal does and why you need it"
- Expected answer: *silence*

**2. Over-use of callbacks (-10 points)**
```python
start_camera(on_frame_ready, on_camera_error, camera_source=0, is_ip_camera=False)
```
- Passing functions as parameters
- Most students just call functions directly
- This is functional programming thinking

**3. Dictionary-based UI refs (-10 points)**
```python
rt_ui["kpi_cards"].itemAt(1).widget()...
```
- Why not just make them instance variables?
- Why return dictionaries everywhere?
- Typical student: Makes everything a class attribute

---

## CATEGORY 4: Oral Defense Risk
**Score: 58/100** ⚠️ HIGH RISK

### Questions That Will Expose Weak Understanding:

**Q1: "Explain the _GuiInvoker class"**
- Expected struggle: 95%
- This is Qt thread-safety mechanism
- Requires understanding of event loops and signals
- Most students: "Um... it makes the GUI update?"

**Q2: "Why do you have both state/ and database/?"**
- Expected struggle: 80%
- This is architecture pattern (persistence vs transient)
- Student answer: "One is for... temporary? And one is for... saving?"
- Real reason requires enterprise software knowledge

**Q3: "Walk through the camera capture flow"**
- Expected struggle: 70%
- Must explain: main thread → camera thread → AI thread → callback → GUI thread
- Must understand: thread synchronization, GIL, frame copying
- Student will draw blank boxes and arrows

**Q4: "Why two threads in workers/camera.py?"**
- Expected struggle: 85%
- Must explain: camera capture at 30 FPS, AI at 5-10 FPS
- Must understand: CPU vs I/O bound operations
- Typical answer: "To make it faster" (wrong)

**Q5: "Show me where face detection happens"**
- Expected struggle: 40%
- It's in InsightFace library, hidden
- Student: "Um... in face/recognizer.py?"
- Follow-up: "Show me the actual detection code"
- Student: "It's... in the library?"
- **RED FLAG**: No custom detection code visible

**Q6: "Explain this line:"**
```python
distances = np.clip(1.0 - np.dot(_gallery["embeddings"], query_emb), 0.0, 2.0)
```
- Expected struggle: 60%
- Requires understanding: cosine similarity, L2 normalization, matrix multiplication
- Good student can explain
- Weak student: "It calculates... distance?"

### Files Most Likely to Expose Lack of Understanding:
1. 🚨 `workers/camera.py` - Threading (85% will fail)
2. 🚨 `main.py` (_GuiInvoker) - Qt threading (90% will fail)
3. ⚠️ `main.py` (KPI updates) - Nested widget access (70% will struggle)
4. ⚠️ `face/recognizer.py` - NumPy vectorization (60% will struggle)
5. ✅ `database/students.py` - Most can explain (20% struggle)

---

## CATEGORY 5: Digital Image Processing Focus
**Score: 55/100** ⚠️ WEAK

### Expected DIP Topics in Final Project:

**✅ Present (40 points):**
- Image acquisition (camera)
- Frame reading (OpenCV)
- Face detection (InsightFace - but hidden)
- Face recognition (cosine similarity)
- Embedding extraction
- Threshold-based classification

**❌ Missing or Hidden (45 points):**

**1. No visible preprocessing (-10 points)**
- No histogram equalization
- No noise reduction
- No contrast enhancement
- No face alignment
- All hidden in InsightFace

**2. No custom face detection (-15 points)**
- Uses InsightFace black box
- No Haar Cascades
- No HOG
- No custom detector
- Question: "Show me YOUR face detection algorithm"
- Answer: "It's in the library..."
- **This is a DIP course, not a library usage course!**

**3. No feature extraction explanation (-10 points)**
- Embeddings come from InsightFace
- No explanation of what embedding means
- No visualization
- No dimension reduction (PCA, t-SNE)
- Just: "call InsightFace, get 512-dim vector"

**4. No image quality assessment (-5 points)**
- No blur detection
- No lighting check
- No pose estimation
- Just process everything

**5. Software architecture overshadows DIP (-5 points)**
- Too much focus on: folders, databases, UI, threads
- Too little focus on: image processing pipeline
- Where is the "Digital Image Processing" part?

### Critical Question:
**"This looks like a Software Engineering project. Where is the image processing?"**

Student answer: "Um... in face/recognizer.py?"

**Follow-up: "Show me the image processing code YOU wrote"**

Student: *scrolls through face/recognizer.py*

**Reality:** It's just InsightFace API calls. No custom processing.

---

## CATEGORY 6: Pipeline Clarity
**Score: 48/100** ⚠️ VERY POOR

### Can I Understand This Flow?
```
Camera → Frame → Detection → Embedding → Recognition → Attendance → Database → UI
```

**Let me trace it:**

1. **Camera** → `workers/camera.py` reads frame
2. **Frame** → Passed to `_ai_loop()`
3. **Detection** → ??? WHERE?? 
4. **Embedding** → ??? WHERE??
5. **Recognition** → `face/recognizer.py` ← All in one function!
6. **Attendance** → `state/attendance.py`
7. **Database** → `database/students.py`
8. **UI** → `ui/components.py` draws boxes

### Problems:

**1. Detection + Embedding + Recognition all in ONE function (-20 points)**
```python
def recognize_faces_in_frame(frame, threshold=0.38, uncertain_margin=0.08):
    faces = _face_app.get(frame)  # Detection? Embedding? Both??
    # ... matching code
```
- Can't see detection separately
- Can't see embedding extraction separately
- All hidden in `_face_app.get()`

**2. No intermediate steps visible (-15 points)**
- Where is preprocessing?
- Where is face alignment?
- Where is feature extraction?
- All black-boxed

**3. Pipeline not self-documenting (-10 points)**
- Need to read 4 files to understand flow
- No pipeline.py that shows the flow
- No comments explaining stages

**4. Image processing lost in software engineering (-7 points)**
- More focus on: threading, databases, UI state management
- Less focus on: detection algorithms, feature extraction, matching

### What a Good DIP Project Should Look Like:
```
preprocessing/
  - histogram_eq.py
  - denoise.py
detection/
  - haar_cascade.py
  - hog_detector.py
features/
  - face_embedding.py
  - lbp_features.py
matching/
  - cosine_similarity.py
  - threshold_classifier.py
```

**Current structure hides the DIP pipeline!**

---

## CATEGORY 7: Maintainability
**Score: 75/100**

### Can Another Student Find Things?

**Easy to find:**
- ✅ Database code → `database/`
- ✅ Camera code → `workers/camera.py`
- ✅ UI code → `ui/`
- ✅ Config → `config/settings.py`

**Harder to find:**
- ⚠️ Recognition code → Split between `face/` and `workers/`
- ⚠️ Attendance logic → Split between `state/`, `main.py`, and `database/`
- ⚠️ Image processing → Hidden in InsightFace
- ⚠️ Face detection → Where?? (it's in InsightFace)

### Issues (-25 points):

**1. Scattered attendance logic (-10 points)**
- Recording: `main.py` (setup_app_logic)
- Storage: `state/attendance.py`
- Export: `database/attendance.py`
- Display: `main.py` (setup_report_logic)
- Why not one place?

**2. Recognition flow requires 3 files (-8 points)**
- Capture: `workers/camera.py`
- Process: `face/recognizer.py`
- Display: `ui/components.py`
- Coordinate: `main.py`

**3. No documentation in code (-7 points)**
- Comments mostly in Vietnamese
- No docstrings with parameter types
- No usage examples
- New student will struggle

---

## CATEGORY 8: AI Suspicion Score
**Score: 35/100** 🚨 HIGHLY SUSPICIOUS

*(Lower score = more suspicious)*

### Red Flags That Suggest AI Generation:

**1. Perfect separation of concerns (Enterprise pattern) 🚩🚩🚩**
- `state/` for runtime, `database/` for persistent
- This is Clean Architecture
- 95% of students don't think this way
- Students usually: everything in `main.py` or one big `utils.py`

**2. Callback-based architecture 🚩🚩**
```python
start_camera(on_frame_ready, on_camera_error, ...)
```
- Functional programming style
- Students usually: global variables and direct calls
- This is event-driven architecture

**3. The `_GuiInvoker` pattern 🚩🚩🚩**
- This is ADVANCED Qt threading
- Uses signals/slots for thread-safe GUI updates
- I've taught for 10 years, seen maybe 2 students do this
- The underscore prefix (_GuiInvoker) is Pythonic convention - students rarely use

**4. Thread synchronization using global variables correctly 🚩**
```python
global camera_running, latest_frame, latest_ai_results
```
- Proper thread coordination
- Frame copying to avoid race conditions
- Most students: threads crash or race conditions

**5. Dual-thread architecture 🚩🚩**
- Camera thread + AI thread
- Separated I/O from computation
- Understanding of GIL and CPU-bound vs I/O-bound
- University students don't think like this

**6. Consistent naming conventions 🚩**
- All functions: `snake_case`
- All classes: `PascalCase`
- Private variables: `_underscore`
- Constants: `UPPER_CASE`
- Real students: inconsistent naming

**7. Import organization 🚩**
```python
from config.settings import DATA_DIR
from database.students import get_students
from face.recognizer import recognize_faces_in_frame
```
- Organized by module
- Grouped logically
- Students usually: random import order, missing imports, import *

**8. Error handling patterns 🚩**
```python
return True, "Success message"
return False, "Error message"
```
- Consistent tuple return pattern
- Students usually: just raise exceptions or print errors

**9. Type hints in comments (but not Python type hints) 🚩**
```python
def setup_app_logic(ui: dict):
def recognize_faces_in_frame(frame, threshold=0.38, uncertain_margin=0.08):
```
- Some type hints, but not all
- Mixed usage suggests: AI started it, human edited it

**10. "Perfect" code with no obvious bugs 🚩🚩**
- No debug print statements
- No commented-out code
- No TODO/FIXME
- No half-implemented features
- Real student code: messy, with artifacts

### What Suggests Some Human Touch:

**1. Vietnamese comments ✅**
```python
# Bắt buộc phải import ONNX Runtime ĐẦU TIÊN
# Lỗi chí tử của PyQt6
```
- Natural language, not translator-perfect
- Context-specific knowledge

**2. Workarounds and hacks ✅**
```python
# Khắc phục lỗi font OpenCV không hỗ trợ tiếng Việt
name_no_accents = ''.join(c for c in unicodedata.normalize('NFD', name)...)
```
- This is learned from experience
- AI wouldn't add this without being told

**3. Real-world problem solving ✅**
```python
# Kiểm tra nhanh kết nối trước khi khởi động OpenCV (tránh treo app 60 giây)
socket.create_connection((host, port), timeout=2.0)
```
- Specific timeout values from testing
- Knowledge of OpenCV's 60-second timeout

### Verdict:
**70% likely AI-generated structure, 30% human modifications**

---

## CATEGORY 9: Defense Readiness
**Score: 52/100** ⚠️ WILL STRUGGLE

### Predicted Performance:

**Easy Questions (Will Pass):**
- "What database do you use?" → SQLite
- "How do you store face embeddings?" → NumPy .npz file
- "What is cosine similarity?" → Measure of vector similarity
- "Show me the student CRUD code" → database/students.py

**Medium Questions (50/50 Chance):**
- "Explain the camera capture flow" → Might get confused with threads
- "Why do you need two threads?" → Might say "for speed" (partial)
- "What is the purpose of state/ folder?" → Will struggle to justify
- "Walk through frame processing" → Can trace, but miss details

**Hard Questions (Will Fail):**
- "Explain _GuiInvoker" → Likely can't explain Qt signals
- "Why not put attendance in main.py?" → No good answer
- "Show me YOUR face detection code" → It's in InsightFace...
- "Prove you understand this threading code" → Will fail

### Top 15 Defense-Breaking Questions:

**1. Architecture Questions:**
- Q: "Why do you need state/ AND database/?"
- Bad A: "One is temporary, one is permanent"
- Follow-up: "Why not just use database for both?"
- Student: *blank stare*

**2. Threading Questions:**
- Q: "Explain this line: `ai_thread = threading.Thread(target=_ai_loop, daemon=True)`"
- Bad A: "It creates a thread"
- Follow-up: "What does daemon=True do?"
- Student: "Um... it makes it run in background?"
- Reality: Daemon threads die when main thread dies. 80% don't know.

**3. Qt Threading:**
- Q: "Why can't you update GUI from worker thread?"
- Bad A: "Because... it's not allowed?"
- Follow-up: "What happens if you try?"
- Student: "It crashes?"
- Reality: Requires understanding of event loops. 90% don't know.

**4. Image Processing:**
- Q: "Show me where you do face detection"
- A: "In face/recognizer.py"
- Follow-up: "Show me the detection ALGORITHM"
- Student: *scrolls through code*
- Follow-up: "I don't see it. Where is it?"
- Student: "It's... in InsightFace..."
- **CRITICAL FAILURE** - No custom implementation

**5. Cosine Similarity:**
- Q: "Explain this: `distances = np.clip(1.0 - np.dot(...), 0.0, 2.0)`"
- Good student: Can explain dot product, normalization, distance
- Weak student: "It calculates distance"
- Follow-up: "Why 1.0 minus dot product?"
- Student: "Because... higher similarity means lower distance?"
- Follow-up: "Why clip to 2.0?"
- Student: *blank*

**6. Global Variables:**
- Q: "You use global variables in workers/camera.py. Is this good practice?"
- A: "It works"
- Follow-up: "What are the alternatives?"
- Student: *can't answer*
- Reality: Should mention queues, locks, but won't

**7. Error Handling:**
- Q: "What happens if database connection fails?"
- A: "It prints an error"
- Follow-up: "Then what?"
- Student: "The function returns empty list"
- Follow-up: "Is the user notified?"
- Student: "Um... no?"
- **This is a bug they didn't think about**

**8. Memory Management:**
- Q: "Why do you copy the frame here: `frame_to_process = latest_frame.copy()`?"
- Weak A: "To... save it?"
- Follow-up: "Why not just use latest_frame directly?"
- Student: *can't explain race conditions*

**9. Normalization:**
- Q: "Why normalize embeddings?"
- A: "To make them comparable"
- Follow-up: "What does normalization do mathematically?"
- Weak student: *can't explain L2 norm*

**10. Threshold Selection:**
- Q: "How did you choose threshold=0.38?"
- A: "By testing"
- Follow-up: "Show me the test results"
- Student: *has no documentation*
- **Red flag: arbitrary number**

**11-15. More Lethal Questions:**
- "Why is this in a separate file?"
- "Could these two files be merged?"
- "What does this lambda do?"
- "Trace this variable through 3 files"
- "What happens if two students have the same name?"

---

## CATEGORY 10: Overall Student Project Quality
**Score: 68/100**

### As a University Project (Not Enterprise):

**Strengths:**
- ✅ Works (functionality is complete)
- ✅ Clean code (readable)
- ✅ Good naming
- ✅ Proper file organization
- ✅ Uses modern libraries (InsightFace, PyQt6)
- ✅ Has real-world application

**Critical Weaknesses:**
- ❌ Over-engineered for student level
- ❌ Hides image processing behind library
- ❌ More Software Engineering than DIP
- ❌ Complex threading difficult to defend
- ❌ No custom image processing algorithms
- ❌ Suspiciously perfect architecture

### Why Not Full Marks? (-32 points)

**1. This is a DIP course, not Software Engineering (-15 points)**
- Where are the custom algorithms?
- Where is the image processing pipeline?
- Too much focus on architecture, not enough on algorithms

**2. Over-engineering (-10 points)**
- state/ folder for 35 lines
- workers/ folder for one file
- Separation that doesn't add value

**3. Defense risk too high (-7 points)**
- Student likely can't explain 40% of the code
- Threading, signals, callbacks too advanced
- Will struggle under questioning

---

# FINAL VERDICT

## Scores Summary:

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Project Structure | 72/100 | 10% | 7.2 |
| File Responsibility | 78/100 | 10% | 7.8 |
| Student Readability | 65/100 | 15% | 9.75 |
| Oral Defense Risk | 58/100 | 20% | 11.6 |
| DIP Focus | 55/100 | 20% | 11.0 |
| Pipeline Clarity | 48/100 | 10% | 4.8 |
| Maintainability | 75/100 | 5% | 3.75 |
| AI Suspicion | 35/100 | 5% | 1.75 |
| Defense Readiness | 52/100 | 10% | 5.2 |
| Overall Quality | 68/100 | 5% | 3.4 |

**OVERALL SCORE: 66.25/100** (Weighted Average)

**LETTER GRADE: C+ to B-**

---

## Biggest Strengths:

1. **Functional completeness** - All features work
2. **Code readability** - Well-formatted, consistent style
3. **Real-world applicability** - Solves actual problem
4. **Modern tech stack** - InsightFace, PyQt6, SQLite

---

## Biggest Weaknesses:

1. **🚨 Not enough Digital Image Processing** - Too much library usage, not enough custom algorithms
2. **🚨 Over-engineered for student level** - Enterprise patterns, complex threading
3. **🚨 High defense risk** - Student likely can't explain 40% of code
4. **🚨 AI-generated suspicion** - Too perfect, too clean
5. **⚠️ Image processing pipeline hidden** - Can't see detection, extraction, matching separately

---

## Top 10 Improvements:

### For Better DIP Focus:
1. **Add custom face detection** - Implement Haar Cascade or HOG
2. **Add preprocessing pipeline** - Histogram eq, denoising, alignment
3. **Add feature visualization** - Show embeddings, distance matrices
4. **Add image quality checks** - Blur detection, lighting assessment
5. **Separate detection and recognition** - Make pipeline visible

### For Better Defense:
6. **Simplify threading** - Remove dual-thread, use single thread
7. **Remove _GuiInvoker** - Use simpler GUI update method
8. **Merge state/ into main.py** - Eliminate unnecessary abstraction
9. **Add algorithm documentation** - Explain WHY, not just WHAT
10. **Add test/validation docs** - Show how threshold was chosen

---

## Files That Should Be Refactored:

1. **workers/camera.py** - Simplify threading, remove AI loop
2. **main.py** - Remove _GuiInvoker, simplify callbacks
3. **state/attendance.py** - Merge into main.py (too small)
4. **face/recognizer.py** - Split into detection, extraction, matching

---

## Files That Should NOT Be Changed:

1. ✅ **config/settings.py** - Perfect as-is
2. ✅ **database/students.py** - Simple, clear CRUD
3. ✅ **ui/components.py** - Good UI abstraction
4. ✅ **database/attendance.py** - Simple CSV export

---

## Project Type Assessment:

### Does This Look Like:

**❌ A Real Student Project?**
- **NO** - Too clean, too organized
- Real student projects: messier, less separation, more bugs
- This has zero debug prints, no commented code, no TODOs
- Structure screams "professional" not "student"

**✅ An AI-Generated Project?**
- **LIKELY (70% confidence)**
- Perfect separation of concerns
- Enterprise patterns (state/, workers/, callbacks)
- Advanced threading (dual threads, _GuiInvoker)
- Too few "learning artifacts" (trial and error marks)

**❌ An Enterprise Project?**
- **NO** - Missing: tests, CI/CD, documentation, type hints throughout
- But the architecture thinking is enterprise-level

---

## Final Question:
### "If you were the examiner, would you believe the student actually wrote this project?"

**HONEST ANSWER: NO, with 70% confidence.**

### Reasoning:

**Evidence Against Student Authorship:**
1. Architecture too sophisticated (state separation, callbacks)
2. Threading complexity beyond typical student
3. _GuiInvoker pattern is expert-level Qt
4. Zero "learning mess" (no debug prints, commented code)
5. Perfect naming conventions throughout
6. Consistent error handling patterns

**Evidence For Some Student Involvement:**
1. Vietnamese comments show cultural context
2. Specific workarounds (font issues, IP camera rotation)
3. Real-world problem-solving (socket timeout check)
4. Some code could be explained by good student

**What I Would Do in Oral Defense:**
1. Focus on threading - ask detailed questions
2. Ask about _GuiInvoker - most students will fail
3. Ask "show me YOUR algorithm" - expose library dependence
4. Ask "why state/ folder?" - no good justification
5. Ask to trace data flow - see if they understand

**Expected Outcome:**
- Strong student: Can defend 60-70%, struggles with threading
- Weak student: Can defend 30-40%, fails on architecture questions
- AI-assisted student: Can defend 20-30%, memorized but doesn't understand

**My Verdict:**
This project shows signs of AI assistance with human modifications. The architecture is too clean for typical student work, but the problem-solving shows real experience. I would **pass the project conditionally** - pending successful oral defense of the complex parts (threading, architecture decisions).

**Recommended Grade Range:**
- If student defends well: **B (75-82)**
- If student struggles: **C+ (68-74)**
- If student fails defense: **C or lower (60-67)**

---

**END OF REVIEW**

*Reviewed by: Senior Lecturer (Simulated)*  
*Date: June 15, 2026*  
*Recommendation: Require thorough oral defense before final grade*
