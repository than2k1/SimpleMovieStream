from flask import Flask, render_template
from flask_socketio import SocketIO,send

from time import sleep
import cv2
import json
import base64
import threading


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
play = True
workerList = {}
class Worker:
	def __init__(self, filename, user):
		self.filename = filename
		self.user = user
		self.playing = True
		self.cap = cv2.VideoCapture(self.filename)
	def run(self):
			
		while(self.cap.isOpened() and self.playing == True):
			ret,img=self.cap.read()
			if ret:
				img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
				frame = cv2.imencode('.jpg', img)[1].tobytes()
				frame= base64.encodebytes(frame).decode("utf-8")
				self.send(frame)
				socketio.sleep(1/30)
			else:
				self.playing = False
				self.cap = None
				break
	def send(self, json, methods=['GET','POST']):
	
		socketio.emit('image', json )
	def pause(self):
		self.playing = False

	def play(self):
		if self.playing == False:
			self.playing = True
		if self.cap == None:
			self.cap = cv2.VideoCapture(self.filename)
		self.run()
	def stop(self): 
		self.playing = False
		self.cap = None


@app.route('/')
def index():
	return render_template('index.html')


@socketio.on('pause')
def pause(json):
	cur = int(json['data'])
	workerList[cur].pause()

@socketio.on('stop')
def stop(json):
	cur = int(json['data'])
	workerList[cur].stop()

@socketio.on('play')
def play(json):
	cur = int(json['data'])
	workerList[cur].play()


@socketio.on('check')
def gen(json):
	cur = int(json['data'])
	worker = Worker('movie.Mjpeg', cur)
	workerList[cur] = worker
	threading.Thread(target=worker.run()).start()


if __name__ == '__main__':
    socketio.run(app)