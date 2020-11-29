import cv2
import numpy as np   

def draw(frameOG, frame, bi_image):
    cv2.imshow("Frame", frameOG)
    cv2.imshow("Contrast", frame)
    cv2.imshow("bw", bi_image)

def contrast(frameOG, gamma):
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    frame = cv2.LUT(frameOG, lookUpTable)
    return frame

def tresh(frame, th, e, d):
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
    th = 135
    e = 1
    d = 6
    gamma = 0.8
    while True:
        _, frameOG = cap.read()
        frameOG2 = frameOG.copy()
        frameOGCon = frameOG.copy()
        allContours = frameOG.copy()
        mean, _ = cv2.meanStdDev(frameOG)
        print(mean)
        mean = np.mean(mean)
        print(mean)
        
        #if (mean < 30):
        #    th = 65
        #    e = 1
        #    d = 2
        #    gamma = 1.2
        #elif (mean < 75):
        #    th = 135
        #    e = 1
        #    d = 6
        #    gamma = 0.8
        #elif (mean < 85):
        #    th = 190
        #    e = 1
        #    d = 5
        #    gamma = 0.4
        
        
        #contrast
        frame = contrast(frameOG, gamma)
        
        #frame_gray dla sprawozdania
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #frame_gray po threshold dla sprawozdania
        _, filtered_image = cv2.threshold(frame_gray, th, 255, cv2.THRESH_BINARY)
        
        #threshold
        bi_image = tresh(frame, th, e, d)
        
        #findContours
        contours, hierarchy = cv2.findContours(bi_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        #looking for black dots
        contour_list = findDots(contours, bi_image)
        
        cv2.drawContours(allContours, contours, -1,(255, 0, 0), 2)
        cv2.drawContours(frameOGCon, contour_list, -1, (255, 0, 0), 2)
        #draw contours
        if(len(contour_list) > 0): 
            for contour in contour_list:
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(frameOG, ellipse, (0,255,0), 2)
        
        print(len(contour_list)/2)
        
        draw(frameOG, frame, bi_image)
        
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
            cv2.imwrite('frameOG.png', frameOG2)
            cv2.imwrite('contrast.png', frame)
            cv2.imwrite('frame_gray.png', frame_gray)
            cv2.imwrite('filtered_image.png', filtered_image)
            cv2.imwrite('closing.png', bi_image)
            cv2.imwrite('allContours.png', allContours)
            cv2.imwrite('ogContours.png', frameOGCon)
            cv2.imwrite('finalResult.png', frameOG)
        if key == 27:
            break  
    cap.release()

if __name__ == "__main__":
    main()
