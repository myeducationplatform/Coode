import http.server
import socketserver
import threading
import subprocess
import sys
import os

# خادم وهمي لإبقاء الخدمة شغالة على Render
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# تشغيل بوت الأكواد الجديد فقط
p = subprocess.Popen([sys.executable, "simple_code_bot.py"])

print("🚀 تم تشغيل خادم وبوت الأكواد بنجاح!")

p.wait()
