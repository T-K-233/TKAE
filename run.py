import subprocess
import psutil

from flask import Flask, render_template, Response
import cv2

app = Flask(__name__, template_folder="html")

camera = cv2.VideoCapture(1)

def getFrames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("cannot get camera frame")
            continue
        
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        
        # concat frame one by one and show result
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/get_temp")
def get_temp():
    res = subprocess.run("cat /sys/class/thermal/thermal_zone0/temp", shell=True, capture_output=True)
    return str(int(res.stdout.decode()) * 0.001)

@app.route("/get_cpu")
def get_cpu():
    res = subprocess.run("cat /proc/loadavg", shell=True, capture_output=True)
    return str(psutil.cpu_percent(1))

@app.route("/video_feed")
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(getFrames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
