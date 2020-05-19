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
from typing import List
import datetime
from scipy.interpolate import interp1d
import imageio
from numpy import asarray
import argparse

def decode_to_video(input_file_path: str, 
					frame_rate: int, 
					output_file_path: str):
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
		"height": 500,
		"width": 1050,
		"matrix_spacing": 50,
		"matrix_height": 500,
		"matrix_width": 500,
		"background_colour": (0, 255, 0),
		"matrixes": [
			{
			"background_colour": (0, 0, 0),
			"line_colour": (255, 255, 255),
			"line_thiccness": 5,
			"cursor_colour": (255, 0, 0),
			"cursor_size": 42,
			"scale-x": [-501, 501],
			"scale-y": [998, 2000]
			},
			{
			"background_colour": (0, 0, 0),
			"line_colour": (255, 255, 255),
			"line_thiccness": 5,
			"cursor_colour": (0, 0, 255),
			"cursor_size": 42,
			"scale-x": [501, -501],
			"scale-y": [-501, 501]
			}
		]
	}

	if frames:
		frame_rate = 60
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
					print("========= matrix: {0}".format(matrix))
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
						required=True,
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
	parser.add_argument('--info',
						help="small info text")

	args = parser.parse_args()
	print(args.accumulate(args.integers))

	if args.info:
		info()
	else:
		decode_to_video(args.input_file, args.output_file, args.frame_rate)