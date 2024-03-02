from algorithm.object_detector import YOLOv7
from utils.detections import draw
from tqdm import tqdm
import numpy as np
import cv2
from  emotion import init
from torchvision import transforms
import pandas as pd
from metadata import end, write_json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser('My program')
parser.add_argument('-p', '--path',required=True,
    help="file path of video", metavar="FILE")
parser.add_argument('-n', '--name',required=True,
    help="name of folder",)

args = parser.parse_args()
FILE_PATH = args.path
FILE_NAME = args.name



IMAGE_RATIO_THRESHOLD = 0.02 # 02%

yolov7 = YOLOv7()
yolov7.load('weights/yolov7-tiny.pt', classes='person.yaml') # use 'gpu' for CUDA GPU inference
device='cpu'
init(device)
video = cv2.VideoCapture(FILE_PATH)
width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video.get(cv2.CAP_PROP_FPS))
frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
output = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

if video.isOpened() == False:
	print('[!] error opening the video')

print('[+] tracking video...\n')
pbar = tqdm(total=frames_count, unit=' frames', dynamic_ncols=True, position=0, leave=True)
lines = {}

counter = []
metadata = pd.DataFrame(columns=['character', 'frame', "emotion", "confident"])
f = 0
map = {}

try:
    while video.isOpened():
        f+=1
        ret, frame = video.read()
        if ret == True:
            detections, emotions= yolov7.detect(frame,f, track=True)
            detected_frame = frame
            for detection in detections:
                color = (np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255))
                if 'id' in detection:
                    detection_id = detection['id']
                    if detection_id not in lines:
                        detection['color'] = color
                        lines[detection_id] = {'points':[], 'arrows':[], 'color':color}
                    else:
                        detection['color'] = lines[detection_id]['color']
                    
                    lines[detection_id]['points'].append(np.array([detection['x'] + detection['width']/2, detection['y'] + detection['height']/2], np.int32))
                    points = lines[detection_id]['points']
                    #crop
                    if int(detection['id']) not in counter:
                        if 'x' in detection and 'width' in detection and (int(detection['width']) * int(detection['height'])) / (width*height) > IMAGE_RATIO_THRESHOLD :
                            counter.append(int(detection['id']))
                            x1,y1,x2,y2 = int(detection['x']), int(detection['y']), int(detection['x']) + int(detection['width']), int(detection['y'])+detection['height']
                            tensor_to_pil = transforms.ToPILImage()(detected_frame[y1:y2, x1:x2,::-1])
                            file_path = f"ID_{str(detection['id'])}_img.jpg"  # You can use different image formats like .png, .jpeg, etc.
                            Path(f"./characters/{FILE_NAME}/img/").mkdir(parents=True,exist_ok=True)
                            try:
                                tensor_to_pil.save(f"./characters/{FILE_NAME}/img/"+file_path)
                            except:
                                print(file_path, x1,y1,x2,y2,)
                            map[str(detection['id'])] = f"ID_{str(detection['id'])}_img.jpg"


                          
            detected_frame = draw(frame, detections,map)
            output.write(detected_frame)
            pbar.update(1)
        else:
            break
except KeyboardInterrupt:
    pass

pbar.close()
video.release()
output.release()
yolov7.unload()

end(map,f,f'./characters/{FILE_NAME}/metadata.json')
write_json(map,f"./characters/{FILE_NAME}/img_map.json")