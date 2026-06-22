# ClassVision - Hệ Thống Điểm Danh Sinh Viên Bằng Nhận Diện Khuôn Mặt

## Giới thiệu

Đây là đồ án cuối kỳ môn Xử Lý Ảnh Số. Dự án xây dựng hệ thống điểm danh sinh viên tự động bằng công nghệ nhận diện khuôn mặt.

Mục tiêu của dự án:
- Tự động hóa việc điểm danh trong lớp học
- Giảm thời gian điểm danh thủ công
- Lưu trữ và quản lý kết quả điểm danh
- Hỗ trợ cả camera thường và IP camera (điện thoại)

## Chức năng

### 1. Điểm danh bằng Camera
Bật camera để nhận diện khuôn mặt sinh viên theo thời gian thực. Khi phát hiện khuôn mặt, hệ thống tự động so khớp với dữ liệu có sẵn và ghi nhận điểm danh.

### 2. Điểm danh bằng Ảnh tĩnh
Tải lên một ảnh chụp lớp học, hệ thống sẽ phát hiện tất cả khuôn mặt trong ảnh và thực hiện điểm danh hàng loạt.

### 3. Kết nối IP Camera
Hỗ trợ sử dụng điện thoại làm camera thông qua ứng dụng IP Webcam. Tiện lợi khi không có webcam.

### 4. Quản lý sinh viên
Thêm, sửa, xóa thông tin sinh viên trong cơ sở dữ liệu. Hỗ trợ tìm kiếm theo MSSV hoặc tên.

### 5. Xuất báo cáo
Xem danh sách sinh viên đã điểm danh và xuất kết quả ra file CSV để lưu trữ hoặc nộp.

## Công nghệ sử dụng

- **Python 3.x** - Ngôn ngữ lập trình chính
- **PyQt6** - Xây dựng giao diện desktop
- **OpenCV** - Xử lý ảnh và video
- **InsightFace** - Mô hình AI nhận diện khuôn mặt (buffalo_s)
- **NumPy** - Tính toán vector và cosine similarity
- **SQLite** - Lưu trữ thông tin sinh viên
- **ONNX Runtime** - Chạy mô hình AI

## Yêu cầu môi trường

- **Python**: 3.8 trở lên
- **pip**: Để cài đặt thư viện
- **Git**: Để clone dự án
- **Webcam** hoặc **điện thoại có IP Webcam** (tùy chọn)

## Hướng dẫn cài đặt và chạy

### Bước 1: Clone dự án

```bash
git clone <repository-url>
cd refactor
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

Nếu chưa có file `requirements.txt`, cài thủ công:

```bash
pip install PyQt6 opencv-python insightface numpy onnxruntime
```

### Bước 4: Chuẩn bị dữ liệu

Đảm bảo có các file sau trong thư mục `data/`:
- `classvision.db` - Database SQLite chứa thông tin sinh viên
- `gallery.npz` - File chứa face embeddings của sinh viên
- `students/` - Thư mục chứa ảnh khuôn mặt sinh viên (để training)

### Bước 5: Chạy chương trình

```bash
python main.py
```

Chương trình sẽ mở cửa sổ giao diện chính.

## Hướng dẫn sử dụng

### Điểm danh bằng Camera

1. Mở chương trình, chọn tab "Điểm danh Camera"
2. Bấm nút **"Bật Camera"** để bật webcam
3. Hướng camera vào sinh viên, hệ thống sẽ tự động nhận diện
4. Khi nhận diện thành công, tên sinh viên hiển thị trên khung hình
5. Thông tin điểm danh được lưu tự động
6. Bấm **"Tắt Camera"** khi xong

### Điểm danh bằng IP Camera (Điện thoại)

1. Cài ứng dụng **IP Webcam** trên điện thoại Android
2. Mở app, bấm **"Start server"**
3. Ghi nhớ địa chỉ IP hiển thị (VD: `http://192.168.1.10:8080`)
4. Trong chương trình, bấm **"Kết nối IP-Webcam"**
5. Nhập địa chỉ IP vào hộp thoại
6. Hệ thống sẽ kết nối và bắt đầu nhận diện

**Lưu ý**: Điện thoại và máy tính phải cùng mạng Wi-Fi.

### Điểm danh bằng Ảnh tĩnh

1. Chọn tab "Điểm danh Ảnh tĩnh"
2. Bấm **"Chọn ảnh tải lên..."**
3. Chọn file ảnh chụp lớp học (JPG, PNG)
4. Hệ thống sẽ phát hiện và nhận diện tất cả khuôn mặt
5. Kết quả hiển thị bên phải

### Quản lý sinh viên

1. Chọn tab "Quản lý Sinh viên"
2. **Thêm mới**: Bấm "Thêm mới", nhập MSSV, họ tên, lớp
3. **Sửa**: Chọn dòng cần sửa, bấm "Sửa", chỉnh sửa thông tin
4. **Xóa**: Chọn dòng cần xóa, bấm "Xóa", xác nhận
5. **Tìm kiếm**: Nhập MSSV hoặc tên vào ô tìm kiếm

### Xuất báo cáo

1. Chọn tab "Báo cáo Điểm danh"
2. Bấm **"Làm mới"** để xem danh sách sinh viên đã điểm danh
3. Bấm **"Xuất CSV"** để lưu kết quả ra file
4. Chọn nơi lưu file và tên file

## Giải thích các thư mục chính

### `config/`
Chứa file cấu hình của chương trình như đường dẫn, ngưỡng nhận diện, thiết lập AI.

### `database/`
Chứa các hàm thao tác với cơ sở dữ liệu SQLite (thêm, sửa, xóa sinh viên) và xuất CSV.

### `face/`
Chứa code xử lý nhận diện khuôn mặt bằng InsightFace. Load model AI, trích xuất đặc trưng (embedding), tính toán độ tương đồng.

### `workers/`
Chứa code xử lý camera chạy trên thread riêng để không làm giật giao diện. Có 2 luồng: đọc camera và xử lý AI.

### `ui/`
Chứa tất cả code giao diện PyQt6. Bao gồm các widget, trang, cửa sổ chính.

### `state/`
Lưu trữ dữ liệu tạm thời trong bộ nhớ (danh sách điểm danh hiện tại). Khi xuất CSV hoặc tắt app thì mất.

### `data/`
Chứa dữ liệu thật như database, ảnh sinh viên, file embeddings. **Không phải code**.

### `main.py`
File chính để chạy chương trình. Khởi tạo giao diện và kết nối các chức năng lại với nhau.

## Một số lỗi thường gặp

### Lỗi: "Không thể kết nối Camera"

**Nguyên nhân**: Camera đang được dùng bởi ứng dụng khác hoặc không có camera.

**Cách xử lý**:
- Đóng các ứng dụng đang dùng camera (Zoom, Skype, Teams)
- Kiểm tra camera có hoạt động không
- Thử chạy lại chương trình

### Lỗi: "Không thể kết nối IP Webcam"

**Nguyên nhân**: Điện thoại và máy tính khác mạng, hoặc sai địa chỉ IP.

**Cách xử lý**:
- Kiểm tra điện thoại và máy tính cùng mạng Wi-Fi
- Tắt 4G trên điện thoại, chỉ dùng Wi-Fi
- Kiểm tra đã bấm "Start server" trên app IP Webcam chưa
- Nhập đúng địa chỉ IP (VD: `http://192.168.1.10:8080`)

### Lỗi: "Thiếu file gallery.npz"

**Nguyên nhân**: Chưa có file chứa embeddings của sinh viên.

**Cách xử lý**:
- Đảm bảo file `data/gallery.npz` tồn tại
- Nếu chưa có, cần chạy script training để tạo file này từ ảnh sinh viên

### Lỗi: "Model InsightFace không tải được"

**Nguyên nhân**: Thiếu model buffalo_s hoặc chưa cài InsightFace đúng cách.

**Cách xử lý**:
```bash
pip install insightface --upgrade
```
- Model sẽ tự động tải về lần đầu chạy (cần Internet)
- Đợi khoảng 1-2 phút để tải model

### Lỗi: "Không nhận diện được khuôn mặt"

**Nguyên nhân**: Ánh sáng yếu, góc nghiêng, hoặc khuôn mặt quá xa camera.

**Cách xử lý**:
- Tăng ánh sáng trong phòng
- Giữ khuôn mặt thẳng với camera
- Đứng gần camera hơn (khoảng 1-2 mét)
- Đảm bảo khuôn mặt không bị che khuất (khẩu trang, kính râm)

### Lỗi: "Nhận diện sai người"

**Nguyên nhân**: Threshold nhận diện quá cao, hoặc dữ liệu training chưa đủ.

**Cách xử lý**:
- Kiểm tra file `config/settings.py`, điều chỉnh `FACE_MATCH_THRESHOLD` (mặc định 0.38)
- Thêm nhiều ảnh hơn cho sinh viên đó vào thư mục `data/students/`
- Chạy lại script training

## Ghi chú

### Giới hạn của hệ thống

- **Ánh sáng**: Cần đủ ánh sáng để camera và AI hoạt động tốt
- **Góc quay**: Khuôn mặt quá nghiêng (> 45 độ) có thể giảm độ chính xác
- **Khoảng cách**: Tốt nhất từ 1-3 mét, quá xa sẽ khó nhận diện
- **Chất lượng camera**: Camera độ phân giải thấp ảnh hưởng đến kết quả
- **Che khuất**: Khẩu trang, kính đen, mũ che khuôn mặt sẽ làm giảm độ chính xác

### Khuyến nghị sử dụng

- Nên điểm danh trong điều kiện ánh sáng tự nhiên hoặc đèn đủ sáng
- Sinh viên nên nhìn thẳng vào camera khi điểm danh
- Với ảnh tĩnh, nên chụp toàn cảnh lớp học để nhận diện nhiều người cùng lúc
- Định kỳ cập nhật ảnh sinh viên mới để cải thiện độ chính xác

### Tài liệu tham khảo

- **InsightFace**: https://github.com/deepinsight/insightface
- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **OpenCV Python**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

---

**Phát triển bởi**: Nhóm 10
**Lớp**: DIPR430685_06CLC  
**Môn học**: Xử Lý Ảnh Số  
**Năm học**: 2025-2026
