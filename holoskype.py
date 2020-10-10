#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
from threading import Event, Thread
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
    import cv2
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

ip = socket.gethostbyname(socket.gethostname())
port = 9090

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
                self.wfile.write('--jpgboundary\r\n'.encode())
                self.end_headers()
                self.wfile.write(bytearray(buf))
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
                self.wfile.write('--jpgboundary\r\n'.encode())
                self.end_headers()
                self.wfile.write(bytearray(buf))
            return

        if self.path.endswith('holo.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
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
                <script src="https://cdn.jsdelivr.net/npm/holoplay@0.2.3/holoplay.min.js"></script>
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
                            loadImage("http://''' + ip + ':' + str(port) + '''/rgb.mjpg"),
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
                        var size = 15; // size of points - decrease for more "pointy cloudy" feel
                        var camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
                        camera.position.z = 2500;
                        var scene = new THREE.Scene();
                        var holoplay = new HoloPlay(scene, camera, renderer);
                        var rgbData = data[0];
                        var depthData = data[1];
                        var skip = 4; // space between points - increase for better FPS
                        var across = Math.ceil(rgbData.width / skip);
                        var down = Math.ceil(rgbData.height / skip);
                        var positions = [];
                        var colors = [];
                        var spread = 800;
                        var depthSpread = 2000;
                        var size = size;
                        var imageAspect = 1.67; //rgbData.width / rgbData.height
                        for(let y = 0; y < down; ++y) {
                            var v = y / (down - 1);
                            for(let x = 0; x < across; ++x) {
                                var u = x / (across - 1);
                                var rgb = getPixel(rgbData, u, v);
                                var depth = 1 - getPixel(depthData, u, v)[0];
                                if(depth < 0.95) {
                                    positions.push(
                                        (u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread, );
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
                        }, 200) // experiment with this value - 200 is sweetspot for my machine
                        
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
                                        positions.push(
                                            (u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread, );
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
            </body>
            </html>''').encode())
            return

        if self.path.endswith('cameras.html') or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode())
            self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/rgb.mjpg"/>').encode())
            self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/depth.mjpg"/>').encode())
            self.wfile.write(('<br><a href="http://' + ip + ':' + str(port) + '/holo.html" target="_blank">Open Holo window</a>').encode())
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
        self.event.set()  # Notify the main thread to stop waiting and process new frame.

    def on_stream_stopped(self):
        print('Stream stopped')

    def connect_to_device(self, dev_idx):
        print('Searching for devices')
        devs = Record3DStream.get_connected_devices()
        print('{} device(s) found'.format(len(devs)))
        for dev in devs:
            print('\tID: {}\n\tUDID: {}\n'.format(dev.product_id, dev.udid))

        if len(devs) <= dev_idx:
            raise RuntimeError('Cannot connect to device #{}, try different index.'
                               .format(dev_idx))

        dev = devs[dev_idx]
        self.session = Record3DStream()
        self.session.on_new_frame = self.on_new_frame
        self.session.on_stream_stopped = self.on_stream_stopped
        self.session.connect(dev)  # Initiate connection and start capturing

    def start_processing_stream(self):
        global rgbframe, depthframe, ip, port
        server = ThreadedHTTPServer(('0.0.0.0', port), CamHandler)
        print('Starting server on address ' + ip + ':' + str(port))
        target = Thread(target=server.serve_forever,args=())
        i = 0
        
        while True:
            self.event.wait()  # Wait for new frame to arrive

            # Copy the newly arrived RGBD frame
            depth = self.session.get_depth_frame()
            rgb = self.session.get_rgb_frame()
            #intrinsic_mat = self.get_intrinsic_mat_from_coeffs(self.session.get_intrinsic_mat())
            # You can now e.g. create point cloud by projecting the depth map using the intrinsic matrix.

            # Postprocess it
            are_truedepth_camera_data_being_streamed = depth.shape[0] == 640
            if are_truedepth_camera_data_being_streamed:
                depth = cv2.flip(depth, 1)
                depth = cv2.rotate(depth, cv2.cv2.ROTATE_90_CLOCKWISE)
                rgb = cv2.flip(rgb, 1)
                rgb = cv2.rotate(rgb, cv2.cv2.ROTATE_90_CLOCKWISE)

            rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            depth = img_as_ubyte(depth)
            #depth2 = cv2.applyColorMap(depth, cv2.COLORMAP_JET);
            
            # Show the RGBD Stream
            #cv2.imshow('RGB', rgb)
            #cv2.imshow('Depth', depth)
            #cv2.imshow('Depth Map', depth2)
            cv2.waitKey(1)
            
            rgbframe = rgb
            depthframe = depth
            if(i == 0):
                target.start()
            i +=1

            self.event.clear()


if __name__ == '__main__':
    app = StreamerApp()
    app.connect_to_device(dev_idx = 0)
    app.start_processing_stream()
