## Raspberry Pi Thermal-Visual Player

A simple Python3 player that scales and blends the output of an Adafruit
MLX90640 thermal camera with the Pi camera output into one output stream.
MLX90640 has a resolution of 32×24 pixels.

![example output animated gif](https://github.com/9nut/thermalplayer/blob/master/thermalplayer.gif?raw=true)

### Run
```
$ python main.py
```

### Notes
On a Raspberry Pi 3 B+ thermal camera, a capture rate higher than 8Hz usually
fails. When running both the MLX and the Pi camera reader threads, the camera
thread should limit itself to 10 frames/sec to avoid a similar _too many
retries_ errors.

### License
MIT

### Authors
Skip Tavakkolian

### Pictures

![RPI3B+ with MLX90640](https://github.com/9nut/thermalplayer/blob/master/rpi3_mlx90640_thermalplayer.jpeg?raw=true)
