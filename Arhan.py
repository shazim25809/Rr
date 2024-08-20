import requests
import time
import threading
import http.server
import socketserver
import urllib.parse


sections = [
    {"profile_id": "", "messages": [], "access_tokens": [], "timer": 10, "running": False}
    for _ in range(10)
]

def send_message(profile_id, message, access_token):
    try:
        url = "https://graph.facebook.com/v17.0/{0}/".format("t_" + profile_id)
        parameters = {'access_token': access_token, 'message': message}
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Referer': 'http://www.google.com'
        }
        s = requests.post(url, data=parameters, headers=headers)
        s.raise_for_status()

        tt = time.strftime("%Y-%m-%d %I:%M:%S %p")
        print(f"[{tt}] Message sent to {profile_id}: {message}")

    except requests.exceptions.RequestException as e:
        print("[!] Failed to send message:", e)

def run_server(ports):
    for port in ports:
        try:
            with socketserver.TCPServer(("", port), MyHandler) as httpd:
                print("Serving at port", port)
                httpd.serve_forever()
        except OSError:
            print("Port", port, "is already in use. Trying the next port.")

def start_section(index):
    global sections
    sections[index]["running"] = True
    threading.Thread(target=send_messages, args=(index,)).start()

def stop_section(index):
    global sections
    sections[index]["running"] = False

def send_messages(index):
    global sections
    message_index = 0
    token_index = 0
    while sections[index]["running"]:
        if message_index >= len(sections[index]["messages"]):
            message_index = 0
        if token_index >= len(sections[index]["access_tokens"]):
            token_index = 0
        send_message(sections[index]["profile_id"], sections[index]["messages"][message_index], sections[index]["access_tokens"][token_index])
        message_index += 1
        token_index += 1
        time.sleep(sections[index]["timer"])

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
            <head>
              <title>Message Sender</title>
              <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }
                .container {
                    width: 80%;
                    max-width: 1200px;
                    margin: 20px auto;
                    background: white;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }
                h1 {
                    text-align: center;
                    color: #333;
                }
                h2 {
                    color: #444;
                }
                form {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                input[type="text"], input[type="number"], textarea {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                input[type="submit"] {
                    padding: 10px 20px;
                    background: #007BFF;
                    border: none;
                    color: white;
                    border-radius: 5px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background: #0056b3;
                }
                .section {
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                }
              </style>
            </head>
            <body>
              <div class="container">
                <h1>MILLER RULEX</h1>
        """)
        for i in range(10):
            self.wfile.write(f"""
                <div class="section">
                    <h2>Section {i+1}</h2>
                    <form action="/start{i}" method="post">
                        <label for="profile_id_{i}">Profile ID:</label>
                        <input type="text" id="profile_id_{i}" name="profile_id">
                        <label for="messages_{i}">Messages :</label>
                        <textarea id="messages_{i}" name="messages" rows="4"></textarea>
                        <label for="access_tokens_{i}">Access Tokens :</label>
                        <textarea id="access_tokens_{i}" name="access_tokens" rows="4"></textarea>
                        <label for="timer_{i}">Timer (seconds):</label>
                        <input type="number" id="timer_{i}" name="timer" value="10">
                        <input type="submit" value="Start Section {i+1}">
                    </form>
                    <form action="/stop{i}" method="post">
                        <input type="submit" value="Stop Section {i+1}">
                    </form>
                </div>
            """.encode('utf-8'))
        self.wfile.write(b"""
              </div>
            </body>
            </html>
        """)

    def do_POST(self):
        global sections
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        for i in range(10):
            if self.path == f"/start{i}":
                sections[i]["profile_id"] = data.get('profile_id', [''])[0]
                sections[i]["messages"] = data.get('messages', [''])[0].split('\n')
                sections[i]["access_tokens"] = data.get('access_tokens', [''])[0].split('\n')
                sections[i]["timer"] = int(data.get('timer', ['10'])[0])
                start_section(i)

            elif self.path == f"/stop{i}":
                stop_section(i)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


available_ports = [1113, 1114, 1115, 1116, 1117, 1118] 
threading.Thread(target=run_server, args=(available_ports,)).start()

