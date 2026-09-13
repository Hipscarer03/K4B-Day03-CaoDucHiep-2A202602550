# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Cao Đức Hiệp
> **Mã Sinh Viên / Mã Học viên:** 2A202602550
> **Chủ đề Lựa chọn:** Trợ lý gợi ý lịch trình du lịch theo nhu cầu cà nhân và gợi ý từ bài đăng review

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? |
| **2. Tool Interaction** | 5 / 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? |
| **3. Dynamic Decision** | 5 / 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? |
| **4. Long Horizon Goal** | 4 / 5 | Hệ thống có phải giữ mục tiêu xuyên suốt qua nhiều lượt xử lý không? |
| **TỔNG ĐIỂM AGENTIC FIT** | **18/ 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Đà lạt",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "trip_planning",
    "arguments": {
      "destination": "Đà Lạt"
    },
    "observation": {
      "status": "SUCCESS",
      "destination": "Đà Lạt",
      "duration": "3 ngày 2 đêm",
      "people_count": 2,
      "data": {
        "destination": "Đà Lạt",
        "recommended_duration": "3 ngày 2 đêm",
        "suitable_group": "1 - 4 người",
        "highlights": [
          "Săn mây tại Đồi Ngô Quyền & Suối Tía (khu vực yên tĩnh, ít khách du lịch thương mại)",
          "Tham quan Làng hoa Thái Phiên lâu đời",
          "Thưởng thức lẩu gà lá é Éo Éo & bánh căn Nhà Chung"
        ],
        "sample_itinerary_3d2n": {
          "Day 1": "Sáng: Đến Đà Lạt, check-in Homestay. Chiều: Dạo quanh Hồ Tuyền Lâm & Suối Tía. Tối: Ăn lẩu gà lá é.",
          "Day 2": "Sáng: Săn mây Đồi Ngô Quyền. Chiều: Ghé Làng hoa Thái Phiên. Tối: Cà phê ngắm thung lũng đêm.",
          "Day 3": "Sáng: Bánh căn Nhà Chung, mua mứt & rau củ chợ Đà Lạt. Chiều: Khởi hành về."
        },
        "review_sources": [
          "Blog 'Đà Lạt ẩn mình - Những tọa độ yên bình ít người biết 2026'"
        ]
      }
    },
    "latency_ms": 4104.05
  },
  {
    "step": 2,
    "query": "Đà lạt",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Gợi ý lịch trình du lịch Đà Lạt (3 ngày 2 đêm):\n🌟 Điểm nổi bật địa phương:\n - Săn mây tại Đồi Ngô Quyền & Suối Tía (khu vực yên tĩnh, ít khách du lịch thương mại)\n - Tham quan Làng hoa Thái Phiên lâu đời\n - Thưởng thức lẩu gà lá é Éo Éo & bánh căn Nhà Chung\n📅 Lịch trình gợi ý:\n Day 1: Sáng: Đến Đà Lạt, check-in Homestay. Chiều: Dạo quanh Hồ Tuyền Lâm & Suối Tía. Tối: Ăn lẩu gà lá é.\n Day 2: Sáng: Săn mây Đồi Ngô Quyền. Chiều: Ghé Làng hoa Thái Phiên. Tối: Cà phê ngắm thung lũng đêm.\n Day 3: Sáng: Bánh căn Nhà Chung, mua mứt & rau củ chợ Đà Lạt. Chiều: Khởi hành về.\n📚 Nguồn tham khảo review: Blog 'Đà Lạt ẩn mình - Những tọa độ yên bình ít người biết 2026'",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4  lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
