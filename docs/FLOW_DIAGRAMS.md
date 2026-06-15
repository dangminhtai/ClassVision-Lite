# Sơ Đồ Luồng Hoạt Động - ClassVision

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

```mermaid
graph TB
    User[👤 Người dùng] --> UI[🖥️ Giao diện PyQt6]
    UI --> Main[⚙️ main.py<br/>Điều phối]
    
    Main --> Workers[🎥 workers/camera.py<br/>Luồng camera]
    Main --> Face[🤖 face/recognizer.py<br/>Nhận diện AI]
    Main --> DB[💾 database/<br/>Cơ sở dữ liệu]
    Main --> State[📝 state/<br/>Bộ nhớ tạm]
    
    Workers --> Face
    Face --> State
    State --> UI
    DB --> UI
    
    Config[⚙️ config/settings.py<br/>Cấu hình] -.-> Main
    Config -.-> Workers
    Config -.-> Face
    Config -.-> DB
    
    style Main fill:#ffd700
    style Workers fill:#87ceeb
    style Face fill:#90ee90
    style UI fill:#ffb6c1
```

---

## 2. LUỒNG KHỞI ĐỘNG ỨNG DỤNG

```mermaid
sequenceDiagram
    participant User as 👤 Người dùng
    participant Main as main.py
    participant UI as ui/main_window.py
    participant Config as config/settings.py
    
    User->>Main: Chạy python main.py
    activate Main
    
    Main->>Config: Đọc cấu hình
    Config-->>Main: Trả về DATA_DIR, thresholds, etc
    
    Main->>UI: build_main_window()
    activate UI
    UI->>UI: Tạo sidebar, pages
    UI-->>Main: Trả về dict UI components
    deactivate UI
    
    Main->>Main: setup_app_logic(ui)
    Main->>Main: setup_student_manage_logic(ui)
    Main->>Main: setup_image_attendance_logic(ui)
    Main->>Main: setup_report_logic(ui)
    Note over Main: Gắn event handlers<br/>cho tất cả nút bấm
    
    Main->>UI: window.showMaximized()
    UI-->>User: Hiển thị giao diện
    deactivate Main
```

---

## 3. LUỒNG ĐIỂM DANH BẰNG CAMERA (Quan trọng nhất!)

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🖥️ UI Thread<br/>(Main)
    participant CamThread as 🎥 Camera Thread
    participant AIThread as 🤖 AI Thread
    participant Face as face/recognizer.py
    participant State as state/attendance.py
    
    User->>UI: Bấm "Bật Camera"
    activate UI
    
    UI->>CamThread: start_camera(callbacks)
    activate CamThread
    Note over CamThread: camera_running = True
    
    CamThread->>AIThread: Khởi động AI Thread
    activate AIThread
    
    loop Vòng lặp Camera (30 FPS)
        CamThread->>CamThread: cap.read() → frame
        CamThread->>CamThread: Lật/xoay ảnh
        CamThread->>CamThread: Tính FPS
        CamThread->>CamThread: latest_frame = frame
        
        Note over AIThread: Chạy song song
        AIThread->>AIThread: Copy latest_frame
        AIThread->>Face: recognize_faces_in_frame(frame)
        activate Face
        Face->>Face: InsightFace phát hiện khuôn mặt
        Face->>Face: Trích xuất embedding 512-dim
        Face->>Face: So sánh với gallery.npz
        Face->>Face: Tính cosine distance
        Face-->>AIThread: Trả về detections[]
        deactivate Face
        AIThread->>AIThread: latest_ai_results = detections
        AIThread->>AIThread: sleep(150ms)
        
        CamThread->>UI: on_frame_ready(frame, ai_results, fps)
        UI->>State: add_attendance_record()
        Note over State: Lưu vào global_attendance{}
        UI->>UI: Vẽ boxes lên ảnh
        UI->>UI: Cập nhật KPI cards
        UI-->>User: Hiển thị video + boxes
    end
    
    deactivate AIThread
    deactivate CamThread
    deactivate UI
```

---

## 4. LUỒNG XỬ LÝ NHẬN DIỆN KHUÔN MẶT (Chi tiết)

```mermaid
flowchart TD
    Start([📸 Nhận frame từ camera]) --> Check{Frame có<br/>dữ liệu?}
    Check -->|Không| Error[❌ Báo lỗi]
    Check -->|Có| InitCheck{Model đã<br/>load?}
    
    InitCheck -->|Chưa| LoadModel[🔄 init_face_model<br/>- Load InsightFace buffalo_s<br/>- Load gallery.npz<br/>- Normalize embeddings]
    InitCheck -->|Rồi| Detect
    LoadModel --> Detect
    
    Detect[🔍 InsightFace.get<br/>Phát hiện khuôn mặt] --> HasFaces{Có khuôn<br/>mặt?}
    
    HasFaces -->|Không| ReturnEmpty[📋 Trả về list rỗng]
    HasFaces -->|Có| LoopFaces[🔄 Duyệt từng khuôn mặt]
    
    LoopFaces --> ExtractBox[📐 Lấy bounding box<br/>x1, y1, x2, y2]
    ExtractBox --> NormalizeBox[📏 Chuẩn hóa box về 0-1<br/>theo kích thước ảnh]
    
    NormalizeBox --> ExtractEmb[🧮 Lấy embedding vector<br/>512 chiều từ InsightFace]
    ExtractEmb --> NormalizeEmb[📊 Chuẩn hóa L2<br/>query_emb / ||query_emb||]
    
    NormalizeEmb --> CheckGallery{Gallery<br/>có dữ liệu?}
    CheckGallery -->|Không| Unknown1[❓ Đánh dấu Unknown]
    CheckGallery -->|Có| CalcDist
    
    CalcDist[🎯 Tính cosine distance<br/>dist = 1 - dot_product] --> FindBest[🏆 Tìm sinh viên gần nhất<br/>best_idx = argmin]
    
    FindBest --> CompareThreshold{best_dist ≤<br/>threshold?}
    CompareThreshold -->|≤ 0.38| Present[✅ Present<br/>Có mặt chắc chắn]
    CompareThreshold -->|> 0.38| CheckUncertain{≤ 0.46?}
    
    CheckUncertain -->|Có| Uncertain[⚠️ Uncertain<br/>Cần xem xét]
    CheckUncertain -->|Không| Unknown2[❓ Unknown<br/>Không nhận ra]
    
    Present --> AddResult[➕ Thêm vào detections]
    Uncertain --> AddResult
    Unknown1 --> AddResult
    Unknown2 --> AddResult
    
    AddResult --> MoreFaces{Còn khuôn<br/>mặt khác?}
    MoreFaces -->|Có| LoopFaces
    MoreFaces -->|Không| Return[📤 Trả về detections]
    
    ReturnEmpty --> End([🏁 Kết thúc])
    Return --> End
    Error --> End
    
    style Start fill:#90ee90
    style Detect fill:#87ceeb
    style CalcDist fill:#ffd700
    style Present fill:#00ff00
    style Uncertain fill:#ffff00
    style Unknown2 fill:#ff6347
```

---

## 5. LUỒNG THREADING (2 Luồng Song Song)

```mermaid
graph TB
    subgraph MainThread["🖥️ MAIN THREAD (GUI)"]
        UI[Giao diện PyQt6]
        Render[Render video frame]
        UpdateKPI[Cập nhật KPI]
    end
    
    subgraph CameraThread["🎥 CAMERA THREAD"]
        Init1[Khởi tạo cv2.VideoCapture]
        Loop1[Vòng lặp 30 FPS]
        Read[cap.read frame]
        Flip[Lật/xoay ảnh]
        CalcFPS[Tính FPS]
        UpdateFrame[latest_frame = frame]
        Callback[Gọi on_frame_ready]
    end
    
    subgraph AIThread["🤖 AI THREAD"]
        Init2[Khởi tạo InsightFace]
        Loop2[Vòng lặp ~5-10 FPS]
        CopyFrame[Copy latest_frame]
        Recognize[recognize_faces_in_frame]
        UpdateResults[latest_ai_results = results]
        Sleep[sleep 150ms]
    end
    
    Init1 --> Loop1
    Loop1 --> Read
    Read --> Flip
    Flip --> CalcFPS
    CalcFPS --> UpdateFrame
    UpdateFrame --> Callback
    Callback --> Loop1
    
    Init2 --> Loop2
    Loop2 --> CopyFrame
    CopyFrame -->|Đọc| UpdateFrame
    CopyFrame --> Recognize
    Recognize --> UpdateResults
    UpdateResults --> Sleep
    Sleep --> Loop2
    
    Callback -->|Callback| UI
    UI --> Render
    Render --> UpdateKPI
    
    UpdateResults -.->|Dùng chung| Callback
    
    style MainThread fill:#ffb6c1
    style CameraThread fill:#87ceeb
    style AIThread fill:#90ee90
```

**⚠️ GIẢI THÍCH QUAN TRỌNG:**
- **Camera Thread**: Chạy nhanh 30 FPS, chỉ đọc frame
- **AI Thread**: Chạy chậm 5-10 FPS, xử lý AI nặng
- **Tại sao 2 threads?**: Để camera không bị giật lag khi AI xử lý
- **latest_frame**: Biến global chia sẻ giữa 2 threads
- **latest_ai_results**: Kết quả AI mới nhất

---

## 6. LUỒNG QUẢN LÝ SINH VIÊN (CRUD)

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as ui/pages.py
    participant Main as main.py
    participant DB as database/students.py
    participant SQLite as classvision.db
    
    rect rgb(200, 255, 200)
    Note over User,SQLite: 1️⃣ XEM DANH SÁCH
    User->>UI: Mở trang Quản lý SV
    UI->>Main: load_data()
    Main->>DB: get_students(search_text)
    DB->>SQLite: SELECT * FROM students
    SQLite-->>DB: rows[]
    DB-->>Main: [(id, name, class), ...]
    Main->>UI: Điền vào table
    UI-->>User: Hiển thị danh sách
    end
    
    rect rgb(255, 255, 200)
    Note over User,SQLite: 2️⃣ THÊM SINH VIÊN
    User->>UI: Bấm "Thêm mới"
    UI->>UI: Hiển thị StudentDialog
    User->>UI: Nhập MSSV, Tên, Lớp
    UI->>Main: on_add()
    Main->>DB: add_student(mssv, name, class)
    DB->>SQLite: INSERT INTO students
    SQLite-->>DB: Success / IntegrityError
    DB-->>Main: (True, "Thành công")
    Main->>Main: load_data()
    Main-->>UI: Cập nhật table
    end
    
    rect rgb(255, 200, 200)
    Note over User,SQLite: 3️⃣ XÓA SINH VIÊN
    User->>UI: Chọn dòng + bấm "Xóa"
    UI->>Main: on_delete()
    Main->>UI: Hiển thị confirm dialog
    User->>UI: Bấm Yes
    Main->>DB: delete_student(mssv)
    DB->>SQLite: DELETE FROM students WHERE id=?
    SQLite-->>DB: Success
    DB-->>Main: (True, "Xóa thành công")
    Main->>Main: load_data()
    end
```

---

## 7. LUỒNG ĐIỂM DANH BẰNG ẢNH TĨNH

```mermaid
flowchart TD
    Start([👤 User bấm Upload]) --> FileDialog[📂 Chọn file ảnh]
    FileDialog --> CheckFile{File hợp<br/>lệ?}
    
    CheckFile -->|Không| ShowError[❌ Hiển thị lỗi]
    CheckFile -->|Có| ReadImage[📷 cv2.imread]
    
    ReadImage --> CheckSize{Width > 1920?}
    CheckSize -->|Có| Resize[🔄 Resize về 1920px]
    CheckSize -->|Không| Process
    Resize --> Process
    
    Process[🤖 recognize_faces_in_frame<br/>Cùng hàm với camera!] --> GetResults[📋 Nhận detections]
    
    GetResults --> DrawBoxes[🎨 draw_boxes_on_image<br/>Vẽ khung + tên]
    DrawBoxes --> DisplayImage[🖼️ Hiển thị ảnh đã vẽ]
    
    GetResults --> CalcKPI[📊 Tính toán KPI<br/>Present / Absent / Unknown]
    CalcKPI --> UpdateKPI[📈 Cập nhật KPI cards]
    
    GetResults --> FilterPresent{Lọc sinh viên<br/>có mặt}
    FilterPresent --> SaveState[💾 Lưu vào state/attendance]
    SaveState --> FillTable[📝 Điền vào bảng kết quả]
    
    FillTable --> Done([✅ Hoàn thành])
    ShowError --> Done
    DisplayImage --> Done
    UpdateKPI --> Done
    
    style Process fill:#90ee90
    style DrawBoxes fill:#87ceeb
    style SaveState fill:#ffd700
```

---

## 8. LUỒNG XUẤT BÁO CÁO CSV

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as ui/pages.py
    participant Main as main.py
    participant State as state/attendance.py
    participant CSV as 📄 File CSV
    
    User->>UI: Bấm "Xuất CSV"
    UI->>Main: export_csv()
    
    Main->>State: get_attendance_records()
    State-->>Main: global_attendance{}
    
    Main->>Main: Kiểm tra có dữ liệu?
    
    alt Không có dữ liệu
        Main->>UI: QMessageBox.warning("Trống")
    else Có dữ liệu
        Main->>UI: QFileDialog.getSaveFileName
        UI-->>User: Hộp thoại chọn nơi lưu
        User->>UI: Chọn đường dẫn
        
        Main->>CSV: open(path, 'w', utf-8-sig)
        Main->>CSV: writerow(["STT", "MSSV", ...])
        
        loop Từng sinh viên
            Main->>CSV: writerow([stt, id, name, ...])
        end
        
        Main->>CSV: close()
        Main->>UI: QMessageBox("Thành công")
        UI-->>User: "Đã lưu báo cáo tại..."
    end
```

---

## 9. CẤU TRÚC DỮ LIỆU

### 9.1. Gallery (Face Database)

```mermaid
graph LR
    Gallery[gallery.npz] --> StudentIDs[student_ids<br/>Array string]
    Gallery --> Names[full_names<br/>Array string]
    Gallery --> Classes[class_names<br/>Array string]
    Gallery --> Embeddings[embeddings<br/>Matrix N×512]
    
    Embeddings --> Normalized[Đã chuẩn hóa L2<br/>||emb|| = 1]
    
    style Gallery fill:#ffd700
    style Embeddings fill:#90ee90
```

### 9.2. Detection Result

```mermaid
classDiagram
    class Detection {
        +string name
        +string student_id
        +string status
        +tuple box
    }
    
    class Box {
        +float x (0-1)
        +float y (0-1)
        +float w (0-1)
        +float h (0-1)
    }
    
    class Status {
        <<enumeration>>
        present
        uncertain
        unknown
    }
    
    Detection --> Box
    Detection --> Status
```

### 9.3. Attendance Record

```mermaid
graph TD
    GlobalAttendance[global_attendance<br/>Dictionary] --> Record1[student_id_1]
    GlobalAttendance --> Record2[student_id_2]
    GlobalAttendance --> RecordN[student_id_N]
    
    Record1 --> Name1[name: string]
    Record1 --> Class1[class: string]
    Record1 --> Time1[time: HH:MM:SS]
    Record1 --> Source1[source: Camera/Ảnh tĩnh]
    
    style GlobalAttendance fill:#ffd700
```

---

## 10. COSINE SIMILARITY (Toán học quan trọng!)

```mermaid
graph TB
    subgraph Input["📥 ĐẦU VÀO"]
        Query[Query Embedding<br/>512 chiều<br/>từ khuôn mặt mới]
        Gallery[Gallery Embeddings<br/>N × 512<br/>từ gallery.npz]
    end
    
    subgraph Normalize["📐 CHUẨN HÓA L2"]
        NormQuery[||query|| = 1<br/>query / sqrt sum_query²]
        NormGallery[||gallery|| = 1<br/>Đã làm lúc load]
    end
    
    subgraph Calculate["🧮 TÍNH TOÁN"]
        DotProduct[Dot Product<br/>similarity = gallery · query<br/>Phép nhân ma trận]
        Distance[Cosine Distance<br/>dist = 1 - similarity<br/>Càng nhỏ càng giống]
        Clip[Clip về 0-2<br/>Tránh lỗi số học]
    end
    
    subgraph Output["📤 KẾT QUẢ"]
        ArgMin[argmin distances<br/>Tìm SV gần nhất]
        BestDist[best_dist<br/>Khoảng cách nhỏ nhất]
    end
    
    subgraph Threshold["🎯 NGƯỠNG"]
        Check1{dist ≤ 0.38?}
        Check2{dist ≤ 0.46?}
        Present[✅ Present]
        Uncertain[⚠️ Uncertain]
        Unknown[❓ Unknown]
    end
    
    Query --> NormQuery
    Gallery --> NormGallery
    
    NormQuery --> DotProduct
    NormGallery --> DotProduct
    
    DotProduct --> Distance
    Distance --> Clip
    Clip --> ArgMin
    Clip --> BestDist
    
    BestDist --> Check1
    Check1 -->|Có| Present
    Check1 -->|Không| Check2
    Check2 -->|Có| Uncertain
    Check2 -->|Không| Unknown
    
    style DotProduct fill:#90ee90
    style Distance fill:#87ceeb
    style Present fill:#00ff00
    style Uncertain fill:#ffff00
    style Unknown fill:#ff6347
```

**CÔNG THỨC:**
```
similarity = cos(θ) = (A · B) / (||A|| × ||B||)
distance = 1 - similarity
```

**Nếu embedding đã chuẩn hóa (||A|| = ||B|| = 1):**
```
distance = 1 - (A · B)
```

---

## 11. TÓM TẮT CÁC LUỒNG CHÍNH

| Luồng | File chính | Mô tả ngắn gọn |
|-------|-----------|----------------|
| 🚀 **Khởi động** | main.py | Load config → Build UI → Setup handlers |
| 🎥 **Camera** | workers/camera.py | 2 threads: Camera 30 FPS + AI 5-10 FPS |
| 🤖 **Nhận diện** | face/recognizer.py | InsightFace → Embedding → Cosine distance |
| 👥 **Quản lý SV** | database/students.py | CRUD trên SQLite |
| 📷 **Ảnh tĩnh** | main.py | Upload → Nhận diện → Hiển thị |
| 📊 **Báo cáo** | state/attendance.py | In-memory → Export CSV |

---

## 12. CÂU HỎI THƯỜNG GẶP KHI BẢO VỆ

### Q1: "Tại sao cần 2 threads?"
**A:** 
- Thread 1 (Camera): Đọc frame nhanh 30 FPS, không bị giật
- Thread 2 (AI): Xử lý chậm 5-10 FPS, không làm lag camera
- Nếu 1 thread: AI chậm → camera giật lag

### Q2: "Giải thích cosine similarity"
**A:**
- Đo độ giống nhau giữa 2 vector
- Cos(0°) = 1 (giống nhau)
- Cos(90°) = 0 (khác nhau)
- Distance = 1 - similarity
- Threshold 0.38: Nếu dist ≤ 0.38 → Nhận diện đúng

### Q3: "Tại sao normalize embedding?"
**A:**
- Để chỉ so sánh hướng, không so sánh độ dài
- Sau normalize: ||emb|| = 1
- Cosine similarity = dot product (nhanh hơn)

### Q4: "InsightFace làm gì?"
**A:**
- Phát hiện khuôn mặt (bounding box)
- Trích xuất đặc trưng (embedding 512-dim)
- Embedding: Vector đại diện khuôn mặt
- Học từ hàng triệu ảnh

### Q5: "Giải thích _GuiInvoker"
**A:**
- Qt không cho update GUI từ thread khác
- _GuiInvoker dùng Signal/Slot
- Signal emit từ worker thread
- Slot chạy ở main thread → An toàn

---

**🎯 LỜI KHUYÊN KHI BẢO VỆ:**

1. **Vẽ sơ đồ**: In sơ đồ này ra, trỏ vào giải thích
2. **Nhấn mạnh**: "Em dùng InsightFace cho detection và embedding"
3. **Giải thích toán**: Cosine similarity công thức đơn giản
4. **Threading**: "Camera nhanh, AI chậm, nên em tách ra"
5. **Thành thật**: "Phần này em dùng thư viện, em hiểu cách hoạt động"

**Tránh nói:** "Em tự code từ đầu" → Sẽ bị hỏi sâu!

**Nên nói:** "Em sử dụng InsightFace, một mô hình state-of-the-art, kết hợp với cosine similarity để matching"
