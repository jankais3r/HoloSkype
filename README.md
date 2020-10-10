# HoloSkype
FaceID to Hologram all-in-one script

## Hardware Requirements
- iPhone/iPad with FaceID camera and [Record3d app](https://record3d.app) with unlocked USB streaming (In-app purchase)
- [Looking Glass](https://lookingglassfactory.com) holographic display

## Software Requirements
### Server
- Python 3 with following modules `opencv-python`, `scikit-image`, `record3d`

### Client
- [HoloPlay service](https://lookingglassfactory.com/software/holoplay-service)
- Blink-based web browser (e.g. [Brave](https://brave.com))

You don't need two computers, Client and Server can be the same machine.

See it in action [here](https://twitter.com/jankais3r/status/1314972971967143937).

## To-do
- [x] Initial release
- [ ] Add WebKit compatibility
- [ ] Port to HoloPlay.js v1.0+


## Inspiration
I saw [this demo](https://twitter.com/asidys230/status/1242135956456501248) made with Unity and I decided to re-create it using open web technologies.

## References:
1) Record3d Python Demo App \[[link](https://github.com/marek-simonik/record3d)]
2) Stack Overflow answer on MJEPG streamer \[[link](https://stackoverflow.com/questions/42017354/python-mjpeg-server)]
3) Stack Overflow ansfer on turning depth map into a point cloud with Three.js \[[link](https://stackoverflow.com/questions/53082418/can-i-create-point-cloud-from-depth-and-rgb-image)]
4) Thomas Le Coz's HoloPlay.js demo \[[link](https://beginfill.com/holoplay/demo01/)]
