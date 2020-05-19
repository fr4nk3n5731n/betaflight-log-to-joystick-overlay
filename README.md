# betaflight-log-to-joystick-overlay
small python script to convert the betaflight blackbox log into a small somewhat customisable joystick overlay.

I made this because the existing Betaflight Blackbox Explorer is horribly slow in exporting a stick overlay video because it does more then that in the backgorund. My little script here just crunches through the exprted CSV and give you a neet little mp4 file you can just import into KDENlive or whatever video editor you use.

The green stip in the middle is meant to be keyed out to make it look a little nicer in the video I suppose.


## usage

```
log-to-mp4.py -i yourinput_file.csv -f 60 -o output.mp4
```

argument defaults will be used if not specified.
```
--input|-i INPUT_FILE: path to input CSV file                    
--out|-o OUTPUT_FILE: path to ouptut video file. Default: ./output.mp4
--framerate|-r FRAME_RATE: framerate of video. Default: 60
--height HEIGHT: Height of overlay in pixels. Dfault: 500
--width WIDTH: Width of overlay in pixels. Default: 1050
--gap GAP: Size of gap between sticks in pixels. Default: 50
--gap-colour GAP_COLOUR: colour for the gap between the joysticks for keying out. in video editor. Format "R;G;B" 0-255. Default: 0;255;0

left joystick specific: 
--left-background-colour LEFT_BACKGROUND_COLOUR: colour for left background format: "R;G;B" 0-255. Default: 0;0;0
--left-cross-colour LEFT_CROSS_COLOUR: colour for left cross format: "R;G;B" 0-255. Default 255;255;255
--left-cross-thickness LEFT_CROSS_THICKNESS: thickness for left cross in pixels. Default: 4
--left-stick-size LEFT_CURSOR_SIZE: size in pixels of the left joystick. Default: 42
--left-stick-colour LEFT_CURSOR_COLOUR: colour for left joystick format: "R;G;B" 0-255. Default: 255;0;0
--left_x_range LEFT_X_RANGE: value range of left x axes. Format: "beging:end" Default: -505:505
--left_y_range LEFT_Y_RANGE: value range of left y axes. Format: "beging:end" Default: 998:2000

right joystick specific:
--right-background-colour RIGHT_BACKGROUND_COLOUR: colour for right background format: "R;G;B" 0-255. Default: 0;0;0
--right-cross-colour RIGHT_CROSS_COLOUR: colour for right cross format: "R;G;B" 0-255. Default: 255;255;255
--right-cross-thickness RIGHT_CROSS_THICKNESS: thickness for right cross in pixels. Default: 4
--right-stick-size RIGHT_CURSOR_SIZE: size in pixels of the right joystick. Default: 42
--right-stick-colour RIGHT_CURSOR_COLOUR: colour for right joystick format: "R;G;B" 0-255. Default: 0;0;255
--right_x_range RIGHT_X_RANGE: value range of right x axes. Format: "beging:end" Default: 505:-505
--right_y_range RIGHT_Y_RANGE: value range of right y axes. Format: "beging:end" Default: -505:505
```
### note:
The X and Y range is based on the minimum/maximum values I got from my test logs.


### note:
thanks and have fun

## TODO?:
* maybe add a UI with preview
* maybe read data straight from Betaflight Log
  * decode log data
