import argparse
import logging
import time

import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.estimator import Human
from skeleton_util import configure_skeleton, update_skeleton
from tf_pose.networks import get_graph_path, model_wh

import interface

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
logging.disable(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

lth = int( 656 * (1/3) )
rth = int( 656 * (2/3) )

skeleton = None
sk_flag = False
status = "Configuring..."

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    
    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')

    parser.add_argument('--hand_angle', type=float, default=45.0,
                        help='for dynamic interval rate')

    parser.add_argument('--max_frame_rate', type=float, default=15,
                        help='for dynamic interval rate')

    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    frame_interval_count = 1
    selected_frame_count = 1
    keypress_status = False
    frame_interval = 20

    # for i in list(range(4))[::-1]:
    #     print(i+1)
    #     time.sleep(1)
    while True:
        ret_val, image = cam.read()

        image = cv2.flip(image,1)
        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        
        if sk_flag==False:
            image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
            skeleton, sk_flag = configure_skeleton(humans[0])            
        else:
            image = TfPoseEstimator.draw_humans(image, [skeleton], imgcopy=False)

        logger.debug('show+')
        cv2.putText(image,
                    ("FPS: %f - " % (1.0 / (time.time() - fps_time)))+status,
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
                    
        y_offset_top = 62
        y_offset_bottom = 50
        cv2.line(image, (lth,y_offset_top), (lth,368+y_offset_bottom), (0,255,0), 3)
        cv2.line(image, (rth,y_offset_top), (rth,368+y_offset_bottom), (0,0,255), 3)
        cv2.imshow('tf-pose-estimation result', image)     

        fps_time = time.time()
                
        frame_interval_count+=1
        if frame_interval_count == 5 and sk_flag:
            skeleton = update_skeleton(skeleton, humans[0])
            status = "Processing..."
            keypress_status, frame_interval =  interface.get_keypress(skeleton, selected_frame_count, keypress_status, args.hand_angle, args.max_frame_rate)
            #print("Frame " + str(selected_frame_count) + ": " + str(frame_interval))
            selected_frame_count += 1
            frame_interval_count = 0
        
        logger.debug('postprocess+')



        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    cv2.destroyAllWindows()
