import cv2
import numpy as np   

def draw(frameOG, bi_image):
    cv2.imshow("Frame", frameOG)
    cv2.imshow("bw", bi_image)

def contrast(frameOG, gamma):
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    frame = cv2.LUT(frameOG, lookUpTable)
    return frame

def thresh(frame, th, e, d):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
        
    #closing
    kernel_e = np.ones((e, e), np.uint8)
    kernel_d = np.ones((d, d), np.uint8)
    bi_image = cv2.erode(cv2.dilate(filtered_image, kernel_d), kernel_e)
    return bi_image

def findDots(contours, bi_image):
    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if ((perimeter > 30) and (perimeter < 100) and (len(approx) <= 10)):
            pix = []
            M = cv2.moments(contour)
            cy = int(M['m10']/(M['m00']+0.01))
            cx = int(M['m01']/(M['m00']+0.01))            
            
            pix.append(bi_image[np.clip(cx - 1, 0, bi_image.shape[0]-1), np.clip(cy, 0, bi_image.shape[1]-1)])
            pix.append(bi_image[np.clip(cx + 1, 0, bi_image.shape[0]-1), np.clip(cy, 0, bi_image.shape[1]-1)])
            pix.append(bi_image[np.clip(cx, 0, bi_image.shape[0]-1), np.clip(cy - 1, 0, bi_image.shape[1]-1)])
            pix.append(bi_image[np.clip(cx, 0, bi_image.shape[0]-1), np.clip(cy + 1, 0, bi_image.shape[1]-1)])
            pix.append(bi_image[np.clip(cx, 0, bi_image.shape[0]-1), np.clip(cy, 0, bi_image.shape[1]-1)])
            
            if(len(pix) > 0):
                meanPix = sum(pix)/len(pix)
                if(meanPix <= 125):
                    contour_list.append(contour)
    return contour_list

def main():
    cap = cv2.VideoCapture(0)
    
    while True:
        _, frameOG = cap.read()
        mean, _ = cv2.meanStdDev(frameOG)
        mean = np.mean(mean)
        
        if (mean < 30):
            th = 75
            e = 1
            d = 6
        elif (mean < 50):
            th = 115
            e = 1
            d = 8
        elif (mean < 85):
            th = 155
            e = 1
            d = 7
        elif (mean < 100):
            th = 185
            e = 1
            d = 8
        else:
            th = 190
            e = 1
            d = 7
        
        #contrast
        frame = contrast(frameOG, 0.6)
        
        #threshold
        bi_image = thresh(frame, th, e, d)
        
        #findContours
        contours, hierarchy = cv2.findContours(bi_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        #looking for black dots
        contour_list = findDots(contours, bi_image)
        
        #draw contours
        if(len(contour_list) > 0): 
            for contour in contour_list:
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(frameOG, ellipse, (0,255,0), 2)
        
        draw(frameOG, bi_image)
        
        #adjusting parameters
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
        if key == 32:
            cv2.imwrite('Result.png', frameOG)
            print(len(contour_list))
        if key == 27:
            break  
    cap.release()

if __name__ == "__main__":
    main()
