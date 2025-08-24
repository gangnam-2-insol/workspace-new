#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/applicants?skip=0&limit=1':
            # 수정된 API 응답 (email, phone 포함)
            response_data = {
                "applicants": [
                    {
                        "id": "68aa026c4514c59b9e3936af",
                        "name": "김아름",
                        "email": "seojeongho@example.net",
                        "phone": "063-957-8920",
                        "position": "UI/UX 디자이너",
                        "department": "마케팅팀",
                        "experience": "1-3년",
                        "skills": "Photoshop, Illustrator",
                        "status": "reviewing",
                        "created_at": "2025-08-24T03:03:24.063000"
                    }
                ],
                "total_count": 300,
                "skip": 0,
                "limit": 1,
                "has_more": True
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_test_server():
    server_address = ('', 8001)
    httpd = HTTPServer(server_address, TestHandler)
    print("🔍 테스트 서버 시작: http://localhost:8001")
    print("📝 API 엔드포인트: http://localhost:8001/api/applicants?skip=0&limit=1")
    httpd.serve_forever()

if __name__ == '__main__':
    run_test_server()
