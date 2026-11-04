from flask import Flask, request, Response
import sys

app = Flask(__name__)

latest_frame = None

@app.route('/')
def index():
    return '''
    <html>
      <head><title>Live Stream from client</title></head>
      <body style="margin:0; background:#000; display:flex; justify-content:center; align-items:center; height:100vh;">
        <img src="/video_feed" style="max-width:100%; max-height:100%; object-fit:contain;">
      </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_frame():
    global latest_frame
    file_bytes = request.data
    if file_bytes:
        latest_frame = file_bytes
    return "OK", 200

def generate():
    global latest_frame
    while True:
        if latest_frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        port = sys.argv[1]
        port = int(port)
        app.run(host="0.0.0.0", port=port, threaded=True)
    except:
        print(f"usage: python {sys.argv[0]} <port>")
