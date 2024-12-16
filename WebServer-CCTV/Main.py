import cv2
from flask import Flask, render_template, Response

app = Flask(__name__)

# Initialize the webcam or IP camera
camera = cv2.VideoCapture(0)  # Replace 0 with the IP camera URL if needed

def generate_frames():
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame")
            break
        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            break
        frame = buffer.tobytes()

        # Yield the frame as part of a multipart HTTP response (MJPEG stream)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('lobby.html')  # Simple HTML page for the video feed

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

