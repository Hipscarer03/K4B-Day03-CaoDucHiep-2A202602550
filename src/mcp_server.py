"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPAcademicServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "vinuni-academic-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] HỌC VIÊN HOÀN THIỆN HÀM THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC
        """
        # Bước 1: Gọi dispatch_tool_call để lấy chuỗi JSON từ Tool Router
        raw_result_str = dispatch_tool_call(tool_name, arguments)
        
        # Bước 2: Chuyển đổi chuỗi JSON kết quả thành Python Dictionary
        try:
            result_data = json.loads(raw_result_str)
        except Exception:
            result_data = {"status": "PARSE_ERROR", "raw_content": raw_result_str}

        # Bước 3: Đóng gói phản hồi chuẩn MCP JSON-RPC 2.0
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": result_data
        }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (travel-assistant-mcp-server)")
    print("==========================================================")
    
    server = MCPAcademicServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố: {len(tools)}")
    
    # In danh sách các Tools công bố
    for tool in tools:
        print(f"  - Tool '{tool.get('name')}': {tool.get('description')}")

    # Kiểm tra thử nghiệm hàm call_tool (TODO 2.1)
    test_result = server.call_tool("trip_planning", {"destination": "Đà Nẵng", "duration": "3 ngày 2 đêm", "people_count": 2})
    if not test_result or not test_result.get("result"):
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!")
    else:
        print(f"✅ [TODO 2.1]: Test dispatch tool 'trip_planning' thành công:")
        print(f"   Phản hồi JSON-RPC:\n{json.dumps(test_result, ensure_ascii=False, indent=2)}")

