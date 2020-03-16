# Raspberry Pi Thermal-Visual Player

Example player that scales and blends the output of an Adafruit MLX90640
thermal camera and the Pi camera into one output stream. MLX90640 has a
32x24 resolution.

## Run
```
$ python main.py
```

## Notes
On a Raspberry Pi 3 B+ thermal camera capture rate higher than 8Hz usually
fails with _too many retries_ error. When running both threads (MLX and
camera capture), the Pi camera thread limits itself to 10 frames/sec to avoid
similar _too many retries_ errors.

### Author skip.tavakkolian@gmail.com

