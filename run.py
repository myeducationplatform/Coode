import http.server
import socketserver
import threading
import subprocess
import sys
import os

# 1. إنشاء خادم وهمي لإرضاء Render على الخطة المجانية
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# تشغيل الخادم الوهمي في مسار جانبي (Thread)
threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. تشغيل بوت الإدارة وبوت الأساتذة معاً
p1 = subprocess.Popen([sys.executable, "admin_bot.py"])
p2 = subprocess.Popen([sys.executable, "teacher_bot.py"])

print("🚀 تم تشغيل الخادم والبوتات بنجاح!")

p1.wait()
p2.wait()