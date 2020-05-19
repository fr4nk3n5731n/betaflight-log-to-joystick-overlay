#!/usr/bin/env python3

"""
small command line script to convert Betaflight Logs into a joystick overlay video.
Copyright (C) 2020  Dr.Fr4nk3n5731n

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import re
from PIL import Image, ImageDraw
from typing import Tuple, List
from scipy.interpolate import interp1d
import imageio
from numpy import asarray
import argparse

def parse_colour_string(colour_string: str) -> Tuple[int, int, int]:
	colour = (int(colour_string.split(";")[0]), 
			  int(colour_string.split(";")[1]), 
			  int(colour_string.split(";")[2]))

	return colour

def parse_range_string(range_string: str) -> List[int]:
	input_range = [int(range_string.split(":")[0]),
				   int(range_string.split(":")[1])]

	return input_range

def decode_to_video(input_file_path: str, 
					output_file_path: str,
					frame_rate: int, 
					height: int,
					width: int,
					gap: int,
					gap_colour: Tuple[int, int, int],
					left_background_colour: Tuple[int, int, int],
					left_cross_colour: Tuple[int, int, int],
					left_cross_thickness: int,
					left_cursor_size: int,
					left_cursor_colour: Tuple[int, int, int],
					left_x_range: List[int],
					left_y_range: List[int],
					right_background_colour: Tuple[int, int, int],
					right_cross_colour: Tuple[int, int, int],
					right_cross_thickness: int,
					right_cursor_size: int,
					right_cursor_colour: Tuple[int, int, int],
					right_x_range: List[int],
					right_y_range: List[int]):
	pattern = "^([0-9]+),([0-9]+)(?:[0-9-]+,){12}([0-9-]+),([0-9-]+),([0-9-]+),([0-9-]+).*$"
	regex = re.compile(pattern)
	frames = []
	with open(input_file_path, 'r') as logfile:
		for line in logfile:
			if re.match(regex, line):
				new_frame = []
				for tu in re.findall(pattern, line):
					for value in tu:
						new_frame.append(value)
				frames.append(new_frame)

	full_graph = {
		"height": height,
		"width": width,
		"matrix_spacing": gap,
		"matrix_height": height,
		"matrix_width": height,
		"background_colour": gap_colour,
		"matrixes": [
			{
			"background_colour": left_background_colour,
			"line_colour": left_cross_colour,
			"line_thiccness": left_cross_thickness,
			"cursor_colour": left_cursor_colour,
			"cursor_size": left_cursor_size,
			"scale-x": left_x_range,
			"scale-y": left_y_range
			},
			{
			"background_colour": right_background_colour,
			"line_colour": right_cross_colour,
			"line_thiccness": right_cross_thickness,
			"cursor_colour": right_cursor_colour,
			"cursor_size": right_cursor_size,
			"scale-x": right_x_range,
			"scale-y": right_y_range
			}
		]
	}
	print("=================will video to {0}".format(output_file_path))
	if frames:
		print("will video to {0}".format(output_file_path))
		mp4maker = imageio.get_writer(output_file_path, fps=frame_rate)
		start = frames[0][1]
		end = frames[-1][1]
		print("first: {0}".format(start))
		print("last: {0}".format(end))
		print("length: {0}".format(len(frames)))
		runtime = (int(end) - int(start)) / 100000
		print("runtime: {0}s".format(runtime))
		
		frame_count = len(frames)
		frames_for_framerate = frame_count/runtime/frame_rate
		print("frame time with {0}fps: {1}s".format(frame_rate, runtime/frame_rate))
		print("frame rate: {0}".format(frame_rate))
		print("possible frames divided by frametime: {0}".format(frame_count/runtime))
		print("use every n frame to get framerate: {0}".format(frames_for_framerate))
		print("total frames at framerate of {0}: {1}".format(frame_rate, frame_count/(frame_count/runtime/frame_rate)))
		counter = int(frames_for_framerate) - 1
		for frame in frames:
			if counter + 1 == int(frames_for_framerate):
				counter = 0
				img = Image.new("RGB", (full_graph["width"], full_graph["height"]), (0, 255, 0))
				draw = ImageDraw.Draw(img)

				for matrix in range(0, len(full_graph["matrixes"])):
					x_min = int(full_graph["matrixes"][matrix]["scale-x"][0])
					x_max = int(full_graph["matrixes"][matrix]["scale-x"][1])
					y_min = int(full_graph["matrixes"][matrix]["scale-y"][0])
					y_max = int(full_graph["matrixes"][matrix]["scale-y"][1])

					y_pos = 5 - (matrix * 2)
					x_pos = 4 - (matrix * 2)
					cursor_offset_x = interp1d([x_max,
											   x_min],								
											   [0,
											   full_graph["matrix_width"]])
					cursor_offset_y = interp1d([y_max,
											   y_min],
											   [0,
											   full_graph["matrix_height"]])
					horizontal_offset = matrix * full_graph["matrix_spacing"] + matrix * full_graph["matrix_width"]
					print("horizontal_offset: {0}".format(horizontal_offset))
					background_box = [(0 + horizontal_offset,
									  0),
									  (full_graph["matrix_width"] + horizontal_offset, 
									  full_graph["matrix_height"])]
					print("point 1x raw value: {0}; mapped value: {1}".format(frame[x_pos], int(cursor_offset_x(frame[x_pos]))))
					print("point 1y raw value: {0}; mapped value: {1}".format(frame[y_pos], int(cursor_offset_y(frame[y_pos]))))
					point1 = (int(cursor_offset_x(frame[x_pos])) - (full_graph["matrixes"][matrix]["cursor_size"] / 2) + horizontal_offset,
							  int(cursor_offset_y(frame[y_pos])) - (full_graph["matrixes"][matrix]["cursor_size"] / 2)
							 )
					point2 = (point1[0] + (full_graph["matrixes"][matrix]["cursor_size"] / 2),
							  point1[1] + (full_graph["matrixes"][matrix]["cursor_size"] / 2)
							 )
					print("point1: {0}".format(point1))
					print("point2: {0}".format(point2))

					cursor_location = [(point1[0],
									   point1[1]),
									   (point2[0],
									   point2[1])]
					horizontal_line = [(0 + horizontal_offset,
									   int(full_graph["matrix_height"] / 2)),
									   (full_graph["matrix_width"] + horizontal_offset,
									   int(full_graph["matrix_height"] / 2))]
					vertical_line = [(int(full_graph["matrix_height"] / 2) + horizontal_offset,
							    	 0),
							    	 (int(full_graph["matrix_height"] / 2) + horizontal_offset,
							    	 full_graph["matrix_width"])]
					draw.rectangle(background_box,
								   fill=full_graph["matrixes"][matrix]["background_colour"])
					draw.line(horizontal_line,
							  fill=full_graph["matrixes"][matrix]["line_colour"],
							  width=full_graph["matrixes"][matrix]["line_thiccness"])
					draw.line(vertical_line,
							  fill=full_graph["matrixes"][matrix]["line_colour"],
							  width=full_graph["matrixes"][matrix]["line_thiccness"])
					draw.ellipse(cursor_location, fill=full_graph["matrixes"][matrix]["cursor_colour"])

				mp4maker.append_data(asarray(img))
			else:
				counter = counter + 1
		mp4maker.close()


def info():
	print("Please use the Blacbox Explorer to export your flight log as in CSV.")
	print("Github: https://github.com/betaflight/blackbox-log-viewer/releases")
	print("if you are on Arch there of course is an AUR for it. https://aur.archlinux.org/packages/blackbox-explorer-bin/")
	print("good luck, have fun.")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='convert betaflight Blackbox log CSV to Video. And a lot faster then the Blackbox explorer at that.')
	parser.add_argument('--input', 
						'-i',
						type=str,
						dest="input_file",
	                    help='path to input CSV file')
	parser.add_argument('--out',
						'-o',
						type=str,
						dest='output_file',
						default="output.mp4",
	                    help='path to ouptut video file.')
	parser.add_argument('--framerate', 
						'-r',
						type=int,
						dest="frame_rate",
						default=60,
						help="framerate of video")
	parser.add_argument("--height",
						type=int,
						dest="height",
						default=500,
						help="Height of overlay in pixels")
	parser.add_argument("--width",
						type=int,
						dest="width",
						default=1050,
						help="Width of overlay in pixels")
	parser.add_argument("--gap",
						type=int,
						dest="gap",
						default=50,
						help="Size of gap between sticks in pixels")
	parser.add_argument("--gap-colour",
						type=str,
						dest="gap_colour",
						default="0;255;0",
						help="colour for the gap between the joysticks for keying out in video editor. Format \"R;G;B\" 0-255.")
	parser.add_argument('--info',
						help="small info text")
	#stuff for the left joystick
	parser.add_argument("--left-background-colour",
						type=str,
						dest="left_background_colour",
						default="0;0;0",
						help="colour for left background format: \"R;G;B\" 0-255.")
	parser.add_argument("--left-cross-colour",
						type=str,
						dest="left_cross_colour",
						default="255;255;255",
						help="colour for left cross format: \"R;G;B\" 0-255.")
	parser.add_argument("--left-cross-thickness",
						type=int,
						dest="left_cross_thickness",
						default=4,
						help="thickness for left cross in pixels.")
	parser.add_argument("--left-stick-size",
						type=int,
						dest="left_cursor_size",
						default=42,
						help="size in pixels of the left joystick.")
	parser.add_argument("--left-stick-colour",
						type=str,
						dest="left_cursor_colour",
						default="255;0;0",
						help="colour for left joystick format: \"R;G;B\" 0-255.")
	parser.add_argument("--left_x_range",
						dest="left_x_range",
						type=str,
						default="-505:505",
						help="value range of left x axes. Format: \"beging:end\"")
	parser.add_argument("--left_y_range",
						dest="left_y_range",
						type=str,
						default="998:2000",
						help="value range of left y axes. Format: \"beging:end\"")
	#stuff for the right joystick
	parser.add_argument("--right-background-colour",
						type=str,
						dest="right_background_colour",
						default="0;0;0",
						help="colour for right background format: \"R;G;B\" 0-255.")
	parser.add_argument("--right-cross-colour",
						type=str,
						dest="right_cross_colour",
						default="255;255;255",
						help="colour for right cross format: \"R;G;B\" 0-255.")
	parser.add_argument("--right-cross-thickness",
						type=int,
						dest="right_cross_thickness",
						default=4,
						help="thickness for right cross in pixels.")
	parser.add_argument("--right-stick-size",
						type=int,
						dest="right_cursor_size",
						default=42,
						help="size in pixels of the right joystick.")
	parser.add_argument("--right-stick-colour",
						type=str,
						dest="right_cursor_colour",
						default="0;0;255",
						help="colour for right joystick format: \"R;G;B\" 0-255.")
	parser.add_argument("--right_x_range",
						dest="right_x_range",
						type=str,
						default="505:-505",
						help="value range of right x axes. Format: \"beging:end\"")
	parser.add_argument("--right_y_range",
						dest="right_y_range",
						type=str,
						default="-505:505",
						help="value range of right y axes. Format: \"beging:end\"")

	args = parser.parse_args()

	if args.info:
		info()
	elif args.input_file:
		decode_to_video(args.input_file,
						args.output_file,
						args.frame_rate,
						args.height,
						args.width,
						args.gap,
						parse_colour_string(args.gap_colour),
						parse_colour_string(args.left_background_colour),
						parse_colour_string(args.left_cross_colour),
						args.left_cross_thickness,
						args.left_cursor_size,
						parse_colour_string(args.left_cursor_colour),
						parse_range_string(args.left_x_range),
						parse_range_string(args.left_y_range),
						parse_colour_string(args.right_background_colour),
						parse_colour_string(args.right_cross_colour),
						args.right_cross_thickness,
						args.right_cursor_size,
						parse_colour_string(args.right_cursor_colour),
						parse_range_string(args.right_x_range),
						parse_range_string(args.right_y_range))
	else:
		print("nothing to do")
						