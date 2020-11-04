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

![Demo](https://github.com/jankais3r/HoloSkype/blob/main/demo.gif)

See it in action [here](https://twitter.com/jankais3r/status/1314972971967143937) and [here](https://twitter.com/jankais3r/status/1323772811048005633).

## To-do
- [x] Initial release
- [x] LiDAR sensor support
- [x] Texture effects (Edge/Jet)
- [ ] WebKit compatibility
- [ ] Port to HoloPlay.js v1.0+


## Inspiration
I saw [this demo](https://twitter.com/asidys230/status/1242135956456501248) made with Unity and I decided to re-create it using open web technologies.
[This demo](https://twitter.com/tks_yoshinaga/status/1323490627271630849) then inspired me to add the edge effect.

## References:
1) Record3d Python Demo App \[[link](https://github.com/marek-simonik/record3d)]
2) Stack Overflow answer on MJEPG streamer \[[link](https://stackoverflow.com/questions/42017354/python-mjpeg-server)]
3) Stack Overflow answer on turning depth map into a point cloud with Three.js \[[link](https://stackoverflow.com/questions/53082418/can-i-create-point-cloud-from-depth-and-rgb-image)]
4) Thomas Le Coz's HoloPlay.js demo \[[link](https://beginfill.com/holoplay/demo01/)]
