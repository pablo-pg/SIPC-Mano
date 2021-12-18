import numpy as np
import cv2
import math

cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
image = cv2.imread('media/hand.JPG')
gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
ret,bw = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)



def angle(s,e,f):
    v1 = [s[0]-f[0],s[1]-f[1]]
    v2 = [e[0]-f[0],e[1]-f[1]]
    ang1 = math.atan2(v1[1],v1[0])
    ang2 = math.atan2(v2[1],v2[0])
    ang = ang1 - ang2
    if (ang > np.pi):
        ang -= 2*np.pi
    if (ang < -np.pi):
        ang += 2*np.pi
    return ang*180/np.pi



def abrirCamara():
	if not cap.isOpened:
		print ("Unable to open cam")
		exit(0)

	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		cv2.imshow('frame',frame)
		keyboard = cv2.waitKey(1)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()



def generarCuadrado():
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)
	pt1 = (400,100)
	pt2 = (600,300)

	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		
		frame = cv2.flip(frame,1)
		
		roi = frame[pt1[1]:pt2[1],pt1[0]:pt2[0],:].copy()

		cv2.rectangle(frame,pt1,pt2,(255,0,0))
		cv2.imshow('frame',frame)
		cv2.imshow('ROI',roi)

		keyboard = cv2.waitKey(40)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()




def crearVideo():
	if not cap.isOpened:
		print ("Unable to open cam")
		exit(0)

	frame_width = int(cap.get(3))
	frame_height = int(cap.get(4))
		
	out = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 20, (frame_width,frame_height))
		

	while (True):
		ret,frame=cap.read()
		cv2.imshow('frame',frame)

		out.write(frame)

		keyboard = cv2.waitKey(1)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	out.release()
	cv2.destroyAllWindows()



def abrirVideo(video :str):
	cap = cv2.VideoCapture(video)
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)

	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		cv2.imshow('frame',frame)
		keyboard = cv2.waitKey(40)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	cap = cv2.VideoCapture(0)
	cv2.destroyAllWindows()



def substraccionFondo():
	learning_rate = -1
	if not cap.isOpened:
		print ("Unable to open cam")
		exit(0)

	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		fgMask = backSub.apply(frame,learningRate=learning_rate)
		cv2.imshow('frame',frame)
		cv2.imshow('Foreground Mask',fgMask)

		keyboard = cv2.waitKey(1)
		if keyboard & 0xFF == ord('q'):
			break
		elif keyboard & 0xFF == ord('s'):
			learning_rate = 0

	cap.release()
	cv2.destroyAllWindows()



def contornos():
  contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
  cv2.drawContours(image, contours, -1, (0,255,0),3)

  cv2.imshow('Contours',image)

  keyboard = cv2.waitKey(0)

  cv2.destroyAllWindows()



# La malla convexa incluye el contorno
def mallaConvexa():
  contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
  cv2.drawContours(image, contours, -1, (0,255,0),3)

  hull = cv2.convexHull(contours[0])
  cv2.drawContours(image, [hull], 0, (255,0,0),3)
  cv2.imshow('Contours',image)

  keyboard = cv2.waitKey(0)

  cv2.destroyAllWindows()



# También incluye el contorno
def boundingRect():
  contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
  cv2.drawContours(image, contours, -1, (0,255,0),3)
  rect = cv2.boundingRect(contours[0])
  pt1 = (rect[0],rect[1])
  pt2 = (rect[0]+rect[2],rect[1]+rect[3])

  cv2.rectangle(image,pt1,pt2,(0,0,255),3)

  cv2.imshow('Contours',image)

  keyboard = cv2.waitKey(0)

  cv2.destroyAllWindows()



# Incluye el contorno y la malla convexa
def convDefects():
	contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	cv2.drawContours(image, contours, -1, (0,255,0),3)

	cnt = contours[0]
	hull = cv2.convexHull(cnt,returnPoints = False)
	defects = cv2.convexityDefects(cnt,hull)

	for i in range(len(defects)):
			s,e,f,d = defects[i,0]
			start = tuple(cnt[s][0])
			end = tuple(cnt[e][0])
			far = tuple(cnt[f][0])
			depth = d/256.0
			print(depth)
			ang = angle(start,end,far)
			cv2.line(image,start,end,[255,0,0],2)
			cv2.circle(image,far,5,[0,0,255],-1)

	cv2.imshow('Contours',image)

	keyboard = cv2.waitKey(0)

	cv2.destroyAllWindows()
