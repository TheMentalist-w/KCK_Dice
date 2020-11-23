import cv2
import numpy as np

cap = cv2.VideoCapture(0)
th = 170;
e = 2
d = 2
while True:
    _, frame = cap.read()
    gamma = 0.4
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    frame = cv2.LUT(frame, lookUpTable)
    
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean, std = cv2.meanStdDev(frame_gray)
    #print(mean)
    
    
    if (mean < 70):
        _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
        len_a = 20
        approx = 0.01
        dist = 100
    elif (mean < 90):
        _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
        len_a = 10
        dist = 100
        approx = 0.01
    elif (mean < 120):
        _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
        len_a = 10
        dist = 100
        approx = 0.01
    else:
        _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
    kernel_e = np.ones((e, e), np.uint8)
    kernel_d = np.ones((d, d), np.uint8)
    filtered_image = cv2.erode(cv2.dilate(filtered_image, kernel_d), kernel_e)
    bi_image = cv2.bilateralFilter(filtered_image, 5, 175, 175)
    #bi_image = cv2.medianBlur(filtered_image, filtered_image, 5)
    edges = cv2.Canny(bi_image, 50, 200)
    contours, hierarchy = cv2.findContours(bi_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    dice_list = []
    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        #maska na piksele w konturze
        
        if ((perimeter > 10) and (perimeter < 50) and (len(approx) > 5) and (len(approx) < 9)):
            contour_list.append(contour)
            raw_dist = np.empty(frame.shape, dtype=np.float32)
            pics = []
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    if(cv2.pointPolygonTest(contour, (i,j), True) == 1):
                        pics.append(frame[i, j])
                        #print(pics[0])
                    
            if(len(pics) > 0):
                meanPic = sum(pics)/len(pics)
                #print(meanPic)
                if((meanPic[0] < 30) and (meanPic[1] < 30) and (meanPic[2] < 30)):
                    contour_list.append(contour)
            #        print(meanPic)
            #print(len(approx))
        #else:
        #    if((perimeter > 10) & (perimeter < 50)):
                        #contour_list.append(contour)
            #if((perimeter > 100) & (perimeter < 400) & (len(approx) <= len_a)):
            #    dice_list.append(contour)
            #else:
            #    for dice in dice_list:
            #        M = cv2.moments(dice)
            #        cx = int(M['m10']/(M['m00']+0.01))
            #        cy = int(M['m01']/(M['m00']+0.01))
            #        Me = cv2.moments(contour)
            #        cxe = int(Me['m10']/(Me['m00']+0.01))
            #        cye = int(Me['m01']/(Me['m00']+0.01))
            #        if((perimeter > 10) & (perimeter < 50) & (abs(cxe - cx) < dist) & (abs(cye - cy) < dist)):
            #            contour_list.append(contour)
    #cv2.drawContours(frame, dice_list, -1, (0, 255, 0), 2)

    #cv2.drawContours(frame, contour_list, -1, (255, 0, 0), 2)
    
    for contour in contour_list:
        ellipse = cv2.fitEllipse(contour)
        cv2.ellipse(frame,ellipse,(0,255,0),2)
    
    #print(len(contour_list)/2)
    #print(mean)
    cv2.imshow("Frame", frame)
    cv2.imshow("bw", bi_image)
    key = cv2.waitKey(1)
    if key == 115:
        th = th + 5
        print(th)
    if key == 97:
        th -= 5
        print(th)
    if key == 119:
        e += 1
        print(e)
    if key == 113:
        e -= 1
        print(e)
    if key == 120:
        d += 1
        print(d)
    if key == 122:
        d -= 1
        print(d)
    if key == 27:
        break