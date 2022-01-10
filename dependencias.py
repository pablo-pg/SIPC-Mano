import numpy as np
import cv2
import time
import math

cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
image = cv2.imread('media/hand.JPG')
# Convertir imagen en escala de grises
gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) 
# Pasa los pixeles que esten por encima de 127 los pasa a 255 y el resto a 0
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
		generarCuadrado(cap)
		if not ret:
			exit(0)
		cv2.imshow('frame',frame)
		keyboard = cv2.waitKey(1)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()




def abrirVideo(video):
	cap = cv2.VideoCapture(video)
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)
	while (True):
		ret,frame=cap.read()
		generarCuadrado(cap)
		if not ret:
			exit(0)
		cv2.imshow('frame',frame)
		keyboard = cv2.waitKey(40)
		if keyboard & 0xFF == ord('q'):
			break

	cap.release()
	# cap = cv2.VideoCapture(0)
	cv2.destroyAllWindows()



def generarCuadrado(cap):
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)
	pt1 = (400,100)
	pt2 = (600,300)

	learning_rate = -1
	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		
		roi = frame[pt1[1]:pt2[1],pt1[0]:pt2[0],:].copy()
		cv2.rectangle(frame,pt1,pt2,(255,0,0))
		cv2.imshow('frame',frame)
		fgMask = backSub.apply(roi,learningRate=learning_rate)
		cv2.imshow('Foreground Mask',fgMask)
		convDefects(roi, fgMask)

		keyboard = cv2.waitKey(1)
		if keyboard & 0xFF == ord('q'):
			break
		elif keyboard & 0xFF == ord('s'):
			learning_rate = 0
		elif keyboard & 0xFF == ord('a'):
			learning_rate = -1

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


# Hecho
def substraccionFondo(cap):
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
		if keyboard & 0xFF == ord('s'):
			learning_rate = 0

	cap.release()
	cv2.destroyAllWindows()



def contornos(frame):
	gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
	ret,bw = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	# Pinta el contarno detectado
	cv2.drawContours(frame, contours, -1, (0,255,0),3)
	# Mostramos el contorno
	cv2.imshow('Contours',frame)



# La malla convexa incluye el contorno
def mallaConvexa(frame, fgMask):
	gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
	ret,bw = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	cv2.drawContours(frame, contours, -1, (0,255,0),3)
	hull = cv2.convexHull(contours[0])
	cv2.drawContours(frame, [hull], 0, (255,0,0),3)
	cv2.imshow('Contours',frame)
  # keyboard = cv2.waitKey(0)
  # cv2.destroyAllWindows()



# Tambien incluye el contorno
def boundingRect(frame):
	gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
	ret,bw = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	cv2.drawContours(frame, contours, -1, (0,255,0),3)
	rect = cv2.boundingRect(contours[0])
	pt1 = (rect[0],rect[1])
	pt2 = (rect[0]+rect[2],rect[1]+rect[3])
	cv2.rectangle(frame,pt1,pt2,(0,0,255),3)
	cv2.imshow('Contours',frame)
	# keyboard = cv2.waitKey(0)
	# cv2.destroyAllWindows()


# Incluye el contorno y la malla convexa
def convDefects(frame, fgmask):
	# fgmask = cv2.blur(fgmask, (8,8))
	contours, hierarchy = cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
	print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
	if (len(contours) > 1):
		max = np.copy(contours[0]) 
		for i in contours:
			if (len(i) > len(max)):
				max = np.copy(i)
		cnt = np.copy(max)
		cv2.drawContours(frame, [cnt], -1, (0,255,0),3)
		# print(contours)
		# print('a')
		if (len(cnt) > 4):
			# print('b')
			# cnt = contours[0]
			# print('c')
			hull = cv2.convexHull(cnt, returnPoints=False)
			# print('d')
			hull.sort(True) 
			# time.sleep(0.05)
			# print('e')
			defects = cv2.convexityDefects(cnt,hull)         # <----- Falla
			print('f')
			if defects.__class__ == np.ndarray:
				# print('a')
				for i in range(len(defects)):
					s,e,f,d = defects[i,0]
					start = tuple(cnt[s][0])
					end = tuple(cnt[e][0])
					far = tuple(cnt[f][0])
					print('aa')
					depth = d/256.0
					print('bb')
					ang = angle(start,end,far)
					# print(ang)
					# finger_cnt = 0
					# if  5 * np.pi / 180.0 <= ang and ang <= np.pi / 2:  		# Un dedo es aquello mayor de 5 grados y menor de 90
					# 	finger_cnt += 1
					# 	cv2.circle(frame, far, 4, [0, 0, 255], -1)
					# # if finger_cnt > 0:
					# finger_cnt = finger_cnt + 0
					# cv2.putText(frame, str(finger_cnt), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0) , 2, cv2.LINE_AA)
					# cv2.line(frame,start,end,[255,0,0],2)
					# cv2.circle(frame,far,5,[0,0,255],-1)

	cv2.imshow('Contours',frame)

		

