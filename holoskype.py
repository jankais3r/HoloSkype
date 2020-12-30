#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import urllib.request
from threading import Event, Thread
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
	import cv2
	import numpy as np
except:
	print('Install OpenCV with "pip3 install opencv-python"')
	quit()
try:
	from skimage import img_as_ubyte
except:
	print('Install scikit-image with "pip3 install scikit-image"')
	quit()
try:
	from record3d import Record3DStream
except:
	print('Install Record3D with "pip3 install record3d"')
	quit()
try:
	from diff_match_patch import diff_match_patch
except:
	print('Install diff-match-patch with "pip3 install diff-match-patch"')
	quit()

ip = socket.gethostbyname(socket.gethostname())
port = 9090
fps = 15

with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/holoplay@0.2.3/holoplay.js') as f:
	holoplay_js_vanilla = f.read().decode('utf-8')

with urllib.request.urlopen('https://raw.githubusercontent.com/jankais3r/driverless-HoloPlay.js/main/holoplay.js.patch') as f:
	diff = f.read().decode('utf-8').replace('\r\n', '\n')
	dmp = diff_match_patch()
	patches = dmp.patch_fromText(diff)
	holoplay_js, _ = dmp.patch_apply(patches, holoplay_js_vanilla)
	holoplay_js = holoplay_js.replace('localhost', ip)
	holoplay_js = holoplay_js.replace(
	# Original calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":49.825218200683597},"slope":{"value":5.2160325050354},"center":{"value":-0.23396748304367066},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}',
	# Your calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":47.56401443481445},"slope":{"value":-5.480000019073486},"center":{"value":0.374184787273407},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}')

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global ip, port
		jpegQuality = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
		if self.path.endswith('/rgb.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(rgbframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', rgbframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('/edge.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(edgeframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', edgeframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('/jet.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(jetframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', jetframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('/depth.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(depthframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', depthframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('holoplay.js'):
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript')
			self.end_headers()
			self.wfile.write((holoplay_js).encode())
			return
		
		if self.path.endswith('holo.html') or self.path.endswith('holo_edge.html') or self.path.endswith('holo_jet.html'):
			if self.path.endswith('holo_edge.html'):
				texture = 'edge'
			elif self.path.endswith('holo_jet.html'):
				texture = 'jet'
			else:
				texture = 'rgb'
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			try:
				if sensor == 'faceid':
					skip = 3
					size = 7
					depthspread = 1800
				elif sensor == 'lidar':
					skip = 1
					size = 5
					depthspread = 1500
			except Exception as e:
				print('USB Streaming not started on iDevice. Quitting.')
				print(e)
				os._exit(1)
			self.wfile.write(('''<!DOCTYPE html>
			<html>
			<head>
			<meta charset="utf-8"/>
				<style>
				body {
					margin: 0;
					cursor: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAMSURBVBhXY/j//z8ABf4C/qc1gYQAAAAASUVORK5CYII=), auto;);
				}
				
				canvas {
					width: 100vw;
					height: 100vh;
					display: block;
				}
				</style>
			</head>

			<body>
				<script src="https://cdn.jsdelivr.net/npm/three@0.121.1/build/three.min.js"></script>
				<script src="http://''' + ip + ':' + str(port) + '''/holoplay.js"></script>
				<script>
					/* global THREE */
					function loadImage(url) {
						return new Promise((resolve, reject) => {
							var img = new Image();
							img.crossOrigin = "anonymous";
							img.onload = (e) => {
								resolve(img);
							};
							img.onerror = reject;
							img.src = url;
						});
					}

					function getImageData(img) {
						var ctx = document.createElement("canvas").getContext("2d");
						ctx.canvas.width = img.width;
						ctx.canvas.height = img.height;
						ctx.drawImage(img, 0, 0);
						return ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
					}
					// return the pixel at UV coordinates (0 to 1) in 0 to 1 values
					function getPixel(imageData, u, v) {
						var x = u * (imageData.width - 1) | 0;
						var y = v * (imageData.height - 1) | 0;
						if(x < 0 || x >= imageData.width || y < 0 || y >= imageData.height) {
							return [0, 0, 0, 0];
						} else {
							var offset = (y * imageData.width + x) * 4;
							return Array.from(imageData.data.slice(offset, offset + 4)).map(v => v / 255);
						}
					}
					async function main() {
						var images = await Promise.all([
							loadImage("http://''' + ip + ':' + str(port) + '''/''' + texture + '''.mjpg"),
							loadImage("http://''' + ip + ':' + str(port) + '''/depth.mjpg")
						]);
						var data = images.map(getImageData);
						var canvas = document.querySelector("canvas");
						var renderer = new THREE.WebGLRenderer();
						document.body.appendChild(renderer.domElement);
						var fov = 72; // iPhone Facetime camera FOV
						var aspect = 2;
						var near = 1;
						var far = 4000;
						var size = ''' + str(size) + '''; // size of points - decrease for more "pointy cloudy" feel
						var camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
						camera.position.z = 2500;
						var scene = new THREE.Scene();
						var holoplay = new HoloPlay(scene, camera, renderer);
						var rgbData = data[0];
						var depthData = data[1];
						var skip = ''' + str(skip) + '''; // space between points - increase for better FPS
						var across = Math.ceil(rgbData.width / skip);
						var down = Math.ceil(rgbData.height / skip);
						var positions = [];
						var colors = [];
						var spread = 800;
						var depthSpread = ''' + str(depthspread) + ''';
						var imageAspect = 1.67; //rgbData.width / rgbData.height
						for(let y = 0; y < down; ++y) {
							var v = y / (down - 1);
							for(let x = 0; x < across; ++x) {
								var u = x / (across - 1);
								var rgb = getPixel(rgbData, u, v);
								var depth = 1 - getPixel(depthData, u, v)[0];
								if(depth < 0.95) {
									positions.push((u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread);
									colors.push(...rgb.slice(0, 3));
								}
							}
						}
						var geometry = new THREE.BufferGeometry();
						geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
						geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
						geometry.computeBoundingSphere();
						var material = new THREE.PointsMaterial({
							size: size,
							vertexColors: THREE.VertexColors
						});
						var points = new THREE.Points(geometry, material);
						points.name = "hologram";
						scene.add(points);
						setInterval(function() {
							refresh()
						}, ''' + str(1000 / fps) + ''')
						
						async function refresh() {
							data = images.map(getImageData);
							rgbData = data[0];
							depthData = data[1];
							positions = [];
							colors = [];
							for(let y = 0; y < down; ++y) {
								v = y / (down - 1);
								for(let x = 0; x < across; ++x) {
									u = x / (across - 1);
									rgb = getPixel(rgbData, u, v);
									depth = 1 - getPixel(depthData, u, v)[0];
									if(depth < 0.95) {
										positions.push((u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread);
										colors.push(...rgb.slice(0, 3));
									}
								}
							}
							geometry = new THREE.BufferGeometry();
							geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
							geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
							geometry.computeBoundingSphere();
							material = new THREE.PointsMaterial({
								size: size,
								vertexColors: THREE.VertexColors
							});
							
							var oldObject = scene.getObjectByName("hologram")
							scene.remove(oldObject);
							oldObject.geometry.dispose();
							oldObject.material.dispose();
							oldObject = undefined;
							
							points = new THREE.Points(geometry, material);
							points.name = "hologram";
							scene.add(points);
						}
						
						function resizeRendererToDisplaySize(renderer) {
							var canvas = renderer.domElement;
							var width = canvas.clientWidth;
							var height = canvas.clientHeight;
							var needResize = canvas.width !== width || canvas.height !== height;
							if(needResize) {
								renderer.setSize(width, height, false);
							}
							return needResize;
						}

						function render(time) {
							time *= 0.001;
							if(resizeRendererToDisplaySize(renderer)) {
								var canvas = renderer.domElement;
								camera.aspect = canvas.clientWidth / canvas.clientHeight;
								camera.updateProjectionMatrix();
							}
							holoplay.render(scene, camera);
							requestAnimationFrame(render);
						}
						requestAnimationFrame(render);
					}
					main();
				</script>
				<button onclick="openFullscreen();" style="position: absolute">Fullscreen</button>
				<script>
					var elem = document.documentElement;
					var btn = document.getElementsByTagName('button')[0];
					function openFullscreen() {
						if (elem.requestFullscreen) {
							elem.requestFullscreen();
						} else if (elem.webkitRequestFullscreen) { /* Safari */
							elem.webkitRequestFullscreen();
						}
						btn.parentNode.removeChild(btn);
					}
				</script>
			</body>
			</html>''').encode())
			return
		
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>'.encode())
			self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/rgb.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/edge.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<br><img src="http://' + ip + ':' + str(port) + '/depth.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/jet.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<br><a href="http://' + ip + ':' + str(port) + '/holo.html">Open HoloSkype</a>').encode())
			self.wfile.write(('<br><a href="http://' + ip + ':' + str(port) + '/holo_edge.html">Open HoloSkype with edge effect</a>').encode())
			self.wfile.write(('<br><a href="http://' + ip + ':' + str(port) + '/holo_jet.html">Open HoloSkype with jet effect</a>').encode())
			self.wfile.write('</body></html>'.encode())
			return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

class StreamerApp:
	def __init__(self):
		self.event = Event()
		self.session = None
	
	def on_new_frame(self):
		"""
		This method is called from non-main thread, therefore cannot be used for presenting UI.
		"""
		self.event.set() # Notify the main thread to stop waiting and process new frame.
	
	def on_stream_stopped(self):
		print('Stream stopped')
		quit()
	
	def connect_to_device(self, dev_idx):
		print('Searching for devices')
		devs = Record3DStream.get_connected_devices()
		print('{} device(s) found'.format(len(devs)))
		for dev in devs:
			print('\tID: {}\n\tUDID: {}\n'.format(dev.product_id, dev.udid))

		if len(devs) <= dev_idx:
			raise RuntimeError('Cannot connect to device #{}, try different index.'.format(dev_idx))
		
		dev = devs[dev_idx]
		self.session = Record3DStream()
		self.session.on_new_frame = self.on_new_frame
		self.session.on_stream_stopped = self.on_stream_stopped
		self.session.connect(dev) # Initiate connection and start capturing
	
	def start_processing_stream(self):
		global rgbframe, edgeframe, jetframe, depthframe, ip, port, sensor
		server = ThreadedHTTPServer(('0.0.0.0', port), CamHandler)
		print('Starting server on address ' + ip + ':' + str(port))
		target = Thread(target = server.serve_forever, args = ())
		target.start()
		
		while True:
			self.event.wait() # Wait for new frame to arrive
			
			# Copy the newly arrived RGBD frame
			depth = self.session.get_depth_frame()
			rgb = self.session.get_rgb_frame()
			
			# FaceID
			if depth.shape[0] == 640:
				sensor = 'faceid'
				depth = cv2.flip(depth, 1)
				depth = cv2.rotate(depth, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
				rgb = cv2.flip(rgb, 1)
				rgb = cv2.rotate(rgb, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
				depth = img_as_ubyte(depth)
				jet = cv2.applyColorMap(depth, cv2.COLORMAP_JET)
			
			# LiDAR
			elif depth.shape[0] == 256:
				sensor = 'lidar'
				depth = cv2.rotate(depth, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
				rgb = cv2.rotate(rgb, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
				try:
					depth *= (255.0/depth.max()).astype(depth.dtype)
					jet = cv2.applyColorMap(np.uint8(depth), cv2.COLORMAP_JET)
				except:
					pass
			
			gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
			edges = cv2.Canny(gray, 150, 200)
			kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
			dilate = cv2.dilate(edges, kernel, iterations = 1)
			ret, edge = cv2.threshold(dilate, 100, 255, cv2.THRESH_BINARY_INV)
			
			rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
			
			# Show the RGBD Stream
			#cv2.imshow('RGB', rgb)
			#cv2.imshow('Edges', edge)
			#cv2.imshow('Depth', depthx)
			#cv2.imshow('Depth Map', jet)
			#cv2.waitKey(1)
			
			rgbframe = rgb
			edgeframe = edge
			jetframe = jet
			depthframe = depth
			
			self.event.clear()
			time.sleep(1 / fps)

if __name__ == '__main__':
	np.seterr(all = 'ignore')
	app = StreamerApp()
	try:
		app.connect_to_device(dev_idx = 0)
	except:
		print('Quitting.')
		quit()
	app.start_processing_stream()
	