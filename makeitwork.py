# os import
import os
import time
from pathlib import Path

# ai import
import argparse
import os
import sys
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn

from models.common import DetectMultiBackend
from utils.datasets import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync

# firebase import
from firebase_admin import credentials, firestore, storage, initialize_app
import uuid
import random
import string

#folders
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

#setting 
weight_path = os.path.join(APP_ROOT, 'models/best.pt')
cred_path = os.path.join(APP_ROOT, "bidex-c1983-firebase-adminsdk.json")
img_size = 640
conf_thres = 0.7
iou_thres = 0.4
#source = "/worker/img_cache/inputfolder/"
source = '/Users/beau/dev/bidex_at/backend-bidexat/img_cache/inputfolder'
output = '/Users/beau/dev/bidex_at/backend-bidexat/img_cache/outputfolder'


#initial
cred = credentials.Certificate(cred_path)
initialize_app(cred, {'storageBucket': 'bidex-c1983.appspot.com'})
bucket = storage.bucket()
db = firestore.client()

def fuckit(userID, patientID, slideID):
    # 1.1 get image_name_list from firestore
    imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images')
    deleted_query = imagesRef.where(u'deleted','==',False)
    processed_query = deleted_query.where(u'processed','==',False)
    docs = processed_query.get()
    image_name_list = []
    for doc in docs:
        image_name_list.append(doc.to_dict()['name'])
    print(f'found {len(image_name_list)} images')

    # 1.2 create directory based on clusterIDs
    clusterID =  ''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase + string.digits, k=12))
    direc = f'/Users/beau/dev/bidex_at/backend-bidexat/{clusterID}'
    if os.path.exists(direc):
        pass
    os.makedirs(direc)
    # 1.3 fetch actual files
    for fileName in image_name_list:
        print('start fetching')
        blob = bucket.blob(f'input/{userID}/{patientID}/{slideID}/{fileName}')
        savePath = os.path.joing(source, clusterID, fileName)
        blob.download_to_filename(savePath)
        print('fetch finished')

        #2.1
        print('start detection')
        results = []
        # Initialize
        set_logging()
        device = select_device("")
        half = device.type != 'cpu'  # half precision only supported on CUDA

        models =  attempt_load(weight_path, map_location=device) # load FP32 models
        imgsz = check_img_size(img_size, s=models.stride.max())  # check img_size (default value is 640)
        if half:
            models.half()  # to FP16

        # Second-stage classifier
        classify = False
        if classify:
            modelc = load_classifier(name='resnet101', n=2)  # initialize
            modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model'])  # load weights
            modelc.to(device).eval()

        # Get names and colors
        names = models.module.names if hasattr(models, 'module') else models.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

        # Run inference
        img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
        _ = models(img.half() if half else img) if device.type != 'cpu' else None  # run once

        time1 = time.time()
        # Set Dataloader
        dataset = LoadImages(source, img_size=imgsz)

        for path, img, im0s, vid_cap in dataset:
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            # Inference
            pred = models(img, augment=False)[0]
            # Apply NMS
            pred = non_max_suppression(pred, conf_thres, iou_thres, agnostic=False,classes=None)
            # Apply Classifier
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)
            # Process detections
            print()
            for i, det in enumerate(pred):  # detections per image
                p, s, im0 = path, '', im0s
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n}"  # add to string
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        start_point=(int(xyxy[0]), int(xyxy[1]))
                        end_point = (int(xyxy[2]), int(xyxy[3]))
                        print((start_point, end_point),names[int(cls)],int(conf*1000)/1000)
                        if output != None:  # Add bbox to image
                            label = '%s %.2f' % (names[int(cls)], conf)
                            plot_one_box(xyxy, im0, label=label, color=(9,34.1,2.7), line_thickness=3)
                            results.append(s)
                else:
                    results.append("0")
                    print("nothing found here")
                # Print time (inference + NMS)
                #print('%sDone. (%.3fs)' % (s, t2 - t1))
                # Save results (image with detections)
                if output != None:
                    cv2.imwrite(str(Path(output) / Path(p).name), im0)
        if output != None:
            print('Results saved to %s' % Path(output))
        print("used time:",int((time.time() - time1)*100)/100,"s")
        print(len(results))
    
    
    for fileName in image_name_list:
        path = os.path.joing(output, clusterID, fileName)
        blob = bucket.blob(f'output/{userID}/{patientID}/{slideID}/{fileName}')
        blob.upload_from_filename(path)
        imagesRef = db.collection(u'users').document(userID).collection(u'patients').document(patientID).collection(u'slides').document(slideID).collection(u'images').document(fileName)
        imagesRef.update({

        })

