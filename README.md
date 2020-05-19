# betaflight-log-to-joystick-overlay
small python script to convert the betaflight blackbox log into a small somewhat customisable joystick overlay.

I made this because the existing Betaflight Blackbox Explorer is horribly slow in exporting a stick overlay video because it does more then that in the backgorund. My little script here just crunches through the exprted CSV and give you a neet little mp4 file you can just import into KDENlive or whatever video editor you use.

The green stip in the middle is meant to be keyed out to make it look a little nicer in the video I suppose.

I'll add some more bells as whistles at some point.

## usage

log-to-mp4.py -i yourinput_file.csv -f 60 -o output.mp4

-i|--input PATH: path to input csv file
-f|--framerate FRAMERATE: framerate of the output video. Default: 60fps
-o|--output PATH: path to output video file. Default: output.mp4

pip dependencies: PIL, numpy, scipy, imageio

### note:
thanks and have fun
