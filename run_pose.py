# To use Inference Engine backend, specify location of plugins:
# export LD_LIBRARY_PATH=/opt/intel/deeplearning_deploymenttoolkit/deployment_tools/external/mklml_lnx/lib:$LD_LIBRARY_PATH
import cv2
import numpy as np
import argparse
#import imutils
import time


model='pose/coco/pose_iter_440000.caffemodel'
proto='pose/coco/deploy_coco.prototxt'
inWidth = 368
inHeight = 368

cap = cv2.VideoCapture(0)

#Loading glasses asset
collier = cv2.imread('pose/bijoux/necklace.png', cv2.IMREAD_UNCHANGED)
ratio = collier.shape[1] / collier.shape[0]
#smallcollier = cv2.resize(collier, (50, 50))

#if args.dataset == 'COCO':
BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["Neck", "Nose"], ["Nose", "REye"],
                   ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]]

net = cv2.dnn.readNetFromCaffe(proto, model)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    '--------------------------------------------------------------------------------'
    # frame = cv2.imread(args.input)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    inp = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                               (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inp)
    #start_t = time.time()
    out = net.forward()

    #print('out', out)

    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        #print('point:',point)
        #print('conf: ', point)

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > 0.1 else None)

    for pair in POSE_PAIRS:

        partFrom = pair[0]
        partTo = pair[1]
        assert (partFrom in BODY_PARTS)
        assert (partTo in BODY_PARTS)
        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]
        if points[idFrom] and points[idTo]:
            cv2.line(frame, points[idFrom], points[idTo], (255, 74, 0), 3)
            cv2.ellipse(frame, points[idFrom], (4, 4), 0, 0, 360, (255, 255, 255), cv2.FILLED)
            cv2.ellipse(frame, points[idTo], (4, 4), 0, 0, 360, (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, str(idFrom), points[idFrom], cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2,
                       cv2.LINE_AA)
            cv2.putText(frame, str(idTo), points[idTo], cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)


    # print("time is ", time.time() - start_t)
    #print(inp.shape)
    #frame[y_offset:y_offset + smallcollier.shape[0], x_offset:x_offset + smallcollier.shape[1]] = smallcollier

    cv2.imshow('frame', frame)
    t, _ = net.getPerfProfile()
    freq = cv2.getTickFrequency() / 1000
    #cv2.putText(frame, '%.2fms' % (t / freq), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    '--------------------------------------------------------------------------------'

    # Display the resulting frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

