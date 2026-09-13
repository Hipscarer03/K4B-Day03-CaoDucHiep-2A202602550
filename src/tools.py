"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND (TRAVEL ASSISTANT)
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server Du lịch.
"""

import json
from typing import Dict, Any, Optional

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu bài đăng review & Gợi ý lịch trình du lịch (TC03)
    {
        "name": "trip_planning",
        "description": "Tra cứu bài đăng review chia sẻ kinh nghiệm, địa điểm tham quan địa phương và gợi ý lịch trình du lịch dựa trên địa điểm, thời gian và số lượng người.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Tên địa điểm/thành phố du lịch (ví dụ: 'Đà Nẵng', 'Đà Lạt')"
                },
                "duration": {
                    "type": "string",
                    "description": "Thời gian dự kiến chuyến đi (ví dụ: '3 ngày 2 đêm', '2 ngày 1 đêm')"
                },
                "people_count": {
                    "type": "integer",
                    "description": "Số lượng người tham gia chuyến đi (ví dụ: 2)"
                }
            },
            "required": ["destination"]
        }
    },
    
    # Tool 2: Tra cứu & Lọc khách sạn / homestay theo địa điểm và budget (TC04)
    {
        "name": "search_accommodations",
        "description": "Tra cứu các khách sạn, homestay trong khu vực chỉ định, lọc theo ngân sách tối đa/đêm và các trải nghiệm không gian địa phương.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Khu vực hoặc thành phố cần tra cứu lưu trú (ví dụ: 'Đà Lạt', 'Đà Nẵng')"
                },
                "max_budget": {
                    "type": "number",
                    "description": "Ngân sách tối đa cho 1 đêm tính theo VNĐ (ví dụ: 1000000 cho 1 triệu đồng)"
                },
                "preference": {
                    "type": "string",
                    "description": "Yêu cầu hoặc trải nghiệm mong muốn (ví dụ: 'homestay trải nghiệm địa phương ít người biết', 'view núi')"
                }
            },
            "required": ["location"]
        }
    }
]

import unicodedata

def normalize_text(text: str) -> str:
    """Loại bỏ dấu tiếng Việt và chuyển sang chữ thường để so sánh địa điểm chuẩn xác"""
    text_nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in text_nfkd if not unicodedata.combining(c)]).lower().strip()

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "TRIPS": {
        "ĐÀ NẴNG": {
            "destination": "Đà Nẵng",
            "recommended_duration": "3 ngày 2 đêm",
            "suitable_group": "2 - 4 người",
            "highlights": [
                "Bán đảo Sơn Trà & Chùa Linh Ứng (ngắm toàn cảnh thành phố)",
                "Danh thắng Ngũ Hành Sơn & Động Huyền Không",
                "Trải nghiệm văn hóa địa phương: Làng chài Nam Ô & thưởng thức gỏi cá Nam Ô truyền thống",
                "Dạo quanh Cầu Rồng & Chợ đêm Sơn Trà thưởng thức hải sản"
            ],
            "sample_itinerary_3d2n": {
                "Day 1": "Sáng: Đón khách, nhận phòng. Chiều: Tham quan Bán đảo Sơn Trà. Tối: Xem Cầu Rồng phun lửa/nước và ăn hải sản Chợ đêm Sơn Trà.",
                "Day 2": "Sáng: Check-in Đỉnh Bàn Cờ & Ngũ Hành Sơn. Chiều: Khám phá Làng chài Nam Ô ít người biết, ăn gỏi cá Nam Ô. Tối: Dạo phố cổ Hội An.",
                "Day 3": "Sáng: Tắm biển Mỹ Khê, mua quà đặc sản tại Chợ Cồn. Chiều: Trả phòng & kết thúc lịch trình."
            },
            "review_sources": [
                "Bài viết 'Đà Nẵng 3N2Đ tự túc cho 2 người - Khám phá góc địa phương' từ TravelVn",
                "Review 'Bí kíp vi vu Nam Ô & Sơn Trà vắng người chốn Đà Thành' từ CheckinVietnam"
            ]
        },
        "ĐÀ LẠT": {
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
    "ACCOMMODATIONS": {
        "ĐÀ LẠT": [
            {
                "name": "Mây Lang Thang Homestay & Chill",
                "type": "homestay",
                "price_per_night": 650000,
                "address": "Phường 11, Gần Đồi Ngô Quyền, Đà Lạt",
                "features": "Không gian gỗ ấm cúng, view thung lũng thông, gần nhiều khu vực trải nghiệm địa phương ít người biết, chủ nhà nhiệt tình chỉ dẫn tour bản địa.",
                "rating": 4.8
            },
            {
                "name": "Rừng Hoa Hillside Stay",
                "type": "homestay",
                "price_per_night": 850000,
                "address": "Thái Phiên, Đà Lạt",
                "features": "Nằm giữa vườn hoa Thái Phiên yên tĩnh, trải nghiệm tự hái dâu & làm nông dân cùng gia đình bản địa, cực kỳ yên tĩnh nhẹ nhàng.",
                "rating": 4.7
            },
            {
                "name": "Dalat Pine Boutique Hotel",
                "type": "hotel",
                "price_per_night": 1500000,
                "address": "Trung tâm Phường 1, Đà Lạt",
                "features": "Khách sạn 3 sao hiện đại trung tâm thành phố.",
                "rating": 4.5
            }
        ],
        "ĐÀ NẴNG": [
            {
                "name": "Nam Ô Ocean Homestay",
                "type": "homestay",
                "price_per_night": 500000,
                "address": "Làng chài Nam Ô, Liên Chiểu, Đà Nẵng",
                "features": "Gần biển Nam Ô, không gian trải nghiệm đời sống ngư dân địa phương.",
                "rating": 4.6
            },
            {
                "name": "Son Tra Retreat Villa",
                "type": "hotel",
                "price_per_night": 950000,
                "address": "Bán đảo Sơn Trà, Đà Nẵng",
                "features": "View núi rừng & biển Sơn Trà thanh bình.",
                "rating": 4.7
            }
        ]
    }
}


def execute_trip_planning(destination: str, duration: str = "3 ngày 2 đêm", people_count: int = 2) -> str:
    """Thực thi tra cứu gợi ý lịch trình và địa điểm du lịch"""
    dest_norm = normalize_text(destination)
    trip_data = None
    
    # So sánh không phân biệt dấu và hoa/thường
    for key, data in MOCK_DATABASE["TRIPS"].items():
        key_norm = normalize_text(key)
        if key_norm in dest_norm or dest_norm in key_norm:
            trip_data = data
            break
            
    if trip_data:
        return json.dumps({
            "status": "SUCCESS",
            "destination": destination,
            "duration": duration,
            "people_count": people_count,
            "data": trip_data
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "destination": destination,
            "message": f"Không tìm thấy bài đăng review hoặc dữ liệu gợi ý lịch trình cho địa điểm '{destination}' trong cơ sở dữ liệu."
        }, ensure_ascii=False)

def execute_search_accommodations(location: str, max_budget: Optional[float] = None, preference: str = "") -> str:
    """Thực thi tra cứu khách sạn / homestay theo địa điểm và budget"""
    loc_norm = normalize_text(location)
    places = None
    
    for key, data in MOCK_DATABASE["ACCOMMODATIONS"].items():
        key_norm = normalize_text(key)
        if key_norm in loc_norm or loc_norm in key_norm:
            places = data
            break
    
    if not places:
        return json.dumps({
            "status": "NOT_FOUND",
            "location": location,
            "message": f"Không tìm thấy dữ liệu lưu trú (khách sạn/homestay) tại khu vực '{location}'."
        }, ensure_ascii=False)
        
    filtered = places
    # Lọc theo ngân sách tối đa (budget dưới 1 triệu VNĐ/đêm)
    if max_budget is not None and max_budget > 0:
        filtered = [p for p in filtered if p["price_per_night"] <= max_budget]
        
    # Ưu tiên các homestay/khách sạn có trải nghiệm địa phương ít người biết
    if preference:
        pref_lower = preference.lower()
        matched = [p for p in filtered if any(kw in p["features"].lower() or kw in p["type"].lower() for kw in pref_lower.split())]
        if matched:
            filtered = matched

    return json.dumps({
        "status": "SUCCESS",
        "location": location,
        "max_budget_requested": max_budget,
        "preference": preference,
        "count": len(filtered),
        "data": filtered
    }, ensure_ascii=False)



# Router gọi tool thực tế
TOOL_ROUTER = {
    "trip_planning": execute_trip_planning,
    "search_accommodations": execute_search_accommodations
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
