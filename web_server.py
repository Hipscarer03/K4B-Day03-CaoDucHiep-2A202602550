"""
🌐 WEB SERVER BACKEND FOR REACT TRAVEL AGENT UI
Phục vụ Web UI giao diện Chatbot, API cho Test Cases và Streaming ReAct Loop.
"""

import json
import os
import sys
import time
from urllib.parse import parse_qs, urlparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from app import load_test_cases, save_waterfall_trace
from mcp_server import MCPAcademicServer
from prompts import CHATBOT_BASELINE_PROMPT, REACT_AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

provider = get_llm_provider()
mcp_server = MCPAcademicServer()
base_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(base_dir, "web")

class TravelAgentHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=web_dir, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/test-cases":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            tests = load_test_cases()
            self.wfile.write(json.dumps(tests, ensure_ascii=False).encode("utf-8"))
        elif parsed_url.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status_data = {
                "provider": provider.__class__.__name__,
                "model": getattr(provider, "model_name", "Mock"),
                "server_name": mcp_server.server_name,
                "version": mcp_server.version
            }
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode("utf-8"))
        else:
            if parsed_url.path == "/" or parsed_url.path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/chat-stream":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
            except Exception:
                data = {}

            user_query = data.get("prompt", "").strip()
            mode = data.get("mode", "react") # "react" or "baseline"

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            def send_event(event_type: str, payload: dict):
                try:
                    msg = f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    self.wfile.write(msg.encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass

            if mode == "baseline":
                send_event("step", {"type": "thought", "content": "Chatbot Baseline không sử dụng Tool, trả lời trực tiếp từ System Prompt..."})
                time.sleep(0.3)
                resp_text = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
                send_event("step", {"type": "final_answer", "content": resp_text})
                send_event("done", {"logs": []})
                return

            # ReAct Agent Mode
            step = 0
            trace_logs = []
            tools_list = mcp_server.list_tools()
            
            while step < MAX_ITERATIONS:
                step += 1
                step_start_time = time.time()
                
                llm_response = provider.generate_with_tools(user_query, tools_list, system_prompt=REACT_AGENT_SYSTEM_PROMPT)
                latency_ms = round((time.time() - step_start_time) * 1000, 2)
                
                thought = llm_response.get("thought", "Đang suy luận...")
                send_event("step", {
                    "step": step,
                    "type": "thought",
                    "content": thought,
                    "latency_ms": latency_ms
                })
                time.sleep(0.2)

                if llm_response.get("type") == "text":
                    final_content = llm_response.get("content", "")
                    send_event("step", {
                        "step": step,
                        "type": "final_answer",
                        "content": final_content,
                        "latency_ms": latency_ms
                    })
                    trace_logs.append({
                        "step": step,
                        "query": user_query,
                        "action_type": "FINAL_ANSWER",
                        "thought": thought,
                        "output": final_content,
                        "latency_ms": latency_ms
                    })
                    break

                elif llm_response.get("type") == "tool_call":
                    tool_name = llm_response.get("tool_name")
                    arguments = llm_response.get("arguments", {})

                    send_event("step", {
                        "step": step,
                        "type": "action",
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "latency_ms": latency_ms
                    })
                    time.sleep(0.2)

                    mcp_result = mcp_server.call_tool(tool_name, arguments)
                    obs_data = mcp_result.get("result", {})

                    send_event("step", {
                        "step": step,
                        "type": "observation",
                        "tool_name": tool_name,
                        "observation": obs_data
                    })
                    time.sleep(0.2)

                    # Format Final Answer
                    if obs_data.get("status") == "SUCCESS":
                        if "data" in obs_data:
                            d = obs_data["data"]
                            if isinstance(d, dict) and "highlights" in d:
                                dest = obs_data.get("destination", d.get("destination", ""))
                                dur = obs_data.get("duration", d.get("recommended_duration", ""))
                                hl = "\n - ".join(d.get("highlights", []))
                                itin = d.get("sample_itinerary_3d2n", {})
                                itin_str = "\n ".join([f"{k}: {v}" for k, v in itin.items()])
                                final_answer = (
                                    f"Gợi ý lịch trình du lịch {dest} ({dur}):\n"
                                    f"🌟 Điểm nổi bật địa phương:\n - {hl}\n"
                                    f"📅 Lịch trình gợi ý:\n {itin_str}\n"
                                    f"📚 Nguồn tham khảo review: {', '.join(d.get('review_sources', []))}"
                                )
                            elif isinstance(d, list):
                                loc = obs_data.get("location", "")
                                acc_list = []
                                for p in d:
                                    acc_list.append(f"• {p.get('name')} ({p.get('type')}) - Giá: {p.get('price_per_night', 0):,} VNĐ/đêm | Địa chỉ: {p.get('address')} | Đặc điểm: {p.get('features')} (Đánh giá: {p.get('rating')}/5)")
                                final_answer = f"Danh sách gợi ý nơi lưu trú phù hợp tại {loc}:\n" + "\n".join(acc_list)
                            else:
                                final_answer = f"Kết quả từ MCP Server ({tool_name}): {json.dumps(obs_data, ensure_ascii=False)}"
                        elif "message" in obs_data:
                            final_answer = obs_data["message"]
                        else:
                            final_answer = f"Đã hoàn tất xử lý qua MCP Server: {json.dumps(obs_data, ensure_ascii=False)}"
                    elif obs_data.get("status") == "NOT_FOUND":
                        final_answer = f"⚠️ {obs_data.get('message', 'Không tìm thấy dữ liệu yêu cầu.')}\n💡 Lời khuyên: Hãy kiểm tra lại tên địa điểm và lưu ý luôn tìm hiểu kỹ thông tin điểm đến từ các nguồn uy tín trước khi khởi hành."
                    else:
                        final_answer = f"Phản hồi từ công cụ: {json.dumps(obs_data, ensure_ascii=False)}"

                    trace_logs.append({
                        "step": step,
                        "query": user_query,
                        "action_type": "TOOL_EXECUTION",
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "observation": obs_data,
                        "latency_ms": latency_ms
                    })
                    trace_logs.append({
                        "step": step + 1,
                        "query": user_query,
                        "action_type": "FINAL_ANSWER",
                        "thought": "Tổng hợp kết quả từ MCP Server thành công.",
                        "output": final_answer,
                        "latency_ms": 10.0
                    })

                    send_event("step", {
                        "step": step + 1,
                        "type": "final_answer",
                        "content": final_answer,
                        "raw_data": obs_data
                    })
                    break

            save_waterfall_trace(trace_logs)
            send_event("done", {"logs": trace_logs})

def run_web_server(port=8080):
    os.makedirs(web_dir, exist_ok=True)
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, TravelAgentHTTPRequestHandler)
    print(f"🚀 [WEB SERVER RUNNING]: Mở trình duyệt truy cập -> http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_web_server(port)

