import numpy as np
import cv2
import time
import math


# Comprueba si una lista esta ordenada de mayor a menor
def checkOrder(list):
	ordered = True
	for i in range(len(list)):
		if i > 0:
			if list[i] > list[i - 1]:
				ordered = False
	return ordered


# Bubblesort para ndarray de ndarrays
def mysort(list):
	while not checkOrder(list):
		for iter_num in range(len(list)-1,0,-1):
			for idx in range(iter_num):
				if list[idx] < list[idx + 1]:
					temp = np.ndarray(list[idx].shape,list[idx].dtype, list[idx].T, strides=list[idx].strides)
					temp = list[idx].copy()
					list[idx] = list[idx+1]
					list[idx+1] = temp
	return list


# Calcula el angulo entre puntos.
# Se utiliza para saber el angulo entre defectos de convexidad
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


# En el caso de que el usuario quiera usar el programa con su propia camara.
# Este metodo se encarga de la gestion de la camara unicamente.
def abrirCamara():
	cap = cv2.VideoCapture(0)
	if not cap.isOpened:
		print ("Unable to open cam")
		exit(0)
	
	generarCuadrado(cap)     #< Hace todo lo referente a fgMask, defectos de convexidad, etc.
	cap.release()
	cv2.destroyAllWindows()


# En el caso de que el usuario quiera usar un video cuya ruta se pasa por parametro.
# Este metodo se encarga de la gestion del video unicamente.
def abrirVideo(video):
	cap = cv2.VideoCapture(video)
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)
	
	generarCuadrado(cap)     #< Hace todo lo referente a fgMask, defectos de convexidad, etc.
	cap.release()
	cv2.destroyAllWindows()


# Consigue el fotograma, selecciona un area rectangular, calcula el fgMask y trata el fotograma con los defectos de convexidad
def generarCuadrado(cap):
	if not cap.isOpened:
		print ("Unable to open file")
		exit(0)
	
	# Las dimensiones del rectangulo
	pt1 = (390,90)
	pt2 = (590,310)

	# Se configura la forma de sustraer el fondo
	backSub = cv2.createBackgroundSubtractorMOG2(detectShadows = True)

  # Por defecto la mascara se actualiza y no se pinta en la pantalla
	learning_rate = -1
	imprimir_puntos = False
	todos_puntos = []
	# Empieza el tratamiento de la informacion
	while (True):
		ret,frame=cap.read()
		if not ret:
			exit(0)
		
		# Se crea un rectangulo donde se va a trabajar
		roi = frame[pt1[1]:pt2[1],pt1[0]:pt2[0],:].copy()
		cv2.rectangle(frame,pt1,pt2,(255,0,0))

		# Se aplica la mascara
		fgMask = backSub.apply(roi,learningRate=learning_rate)
		ret,fgMask = cv2.threshold(fgMask,200,255,cv2.THRESH_BINARY)
		cv2.imshow('frame',frame)
		cv2.imshow('Foreground Mask',fgMask)

		# Se hace todo lo relacionado con los defectos de convexidad (conteo de dedos, deteccion de gestos, etc.)
		nuevo_punto = convDefects(roi, fgMask, todos_puntos, imprimir_puntos)
		# En el caso de que se haya detectado un dedo y este activado el modo pintar, se anadira el punto a la lista de puntos independientes del fotograma
		if nuevo_punto.__class__ == tuple:
			if imprimir_puntos == True:
				if nuevo_punto[0].__class__ == np.int32:
					todos_puntos.append(nuevo_punto)

		keyboard = cv2.waitKey(1)
		# Si se pulsa la q, se sale
		if keyboard & 0xFF == ord('q'):
			break
		# Si se pulsa la s, deja de actualizar la mascara
		elif keyboard & 0xFF == ord('s'):
			learning_rate = 0
		# Si se pulsa la a, vuelve a actualizar la mascara
		elif keyboard & 0xFF == ord('a'):
			learning_rate = -1
		# Si se pulsa la p, se entra en el modo de pintar
		elif keyboard & 0xFF == ord('p'):
			imprimir_puntos = True
		# Si se pulsa la b, se borra lo pintado y se sale del modo pintar
		elif keyboard & 0xFF == ord('b'):
			todos_puntos = []
			imprimir_puntos = False

	cap.release()
	cv2.destroyAllWindows()


# Hace todo lo referente a los defectos de convexidad:
#   * Calcula los defectos de convexidad
#   * Cuenta los dedos
#   * Identifica los gestos
#   * Pinta
def convDefects(frame, fgmask, todos_puntos, imprimir_puntos):
	time.sleep(0.05)
	finger_cnt = 0  # Contador inicial de cuantos dedos hay
	nuevo_punto = 0 # Punto que retornara en el caso de que este en modo pintar

	# Se obtienen los contornos de la mano segun el fgMask
	contours, hierarchy = cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]

	# De todos los contornos que puedan haber, nos quedamos solo con el mas grande (la mano)
	if (len(contours) > 1):
		max = np.copy(contours[0]) 
		for i in contours:
			if (len(i) > len(max)):
				max = np.copy(i)
		cnt = np.copy(max)

		# Se muestra el borde de la mano
		cv2.drawContours(frame, [cnt], -1, (0,255,0),3)

		# Se calcula el bounding rect, es decir, un rectangulo cuyos bordes coinciden con los bordes de la mano
		rect = cv2.boundingRect(cnt)
		pt1 = (rect[0],rect[1])
		pt2 = (rect[0]+rect[2],rect[1]+rect[3])
		cv2.rectangle(frame,pt1,pt2,(0,0,255),3)

		# En el caso de que el contorno sea suficientemente grande, se tratara como si fuera la mano
		if (len(cnt) > 4):
			hull = cv2.convexHull(cnt, returnPoints=False)

			# Existe la posibilidad de que el hull este desordenado, haciendo que falle convexityDefects(), por lo que se ordena
			mysort(hull)

			# Se obtienen todos los defectos de convexidad de la mano
			defects = cv2.convexityDefects(cnt,hull)

			# En el caso de que hayan defectos de convexidad, es decir, defects no sea de tipo NoneType
			if defects.__class__ == np.ndarray:
				for i in range(len(defects)):
					# Se obtienen los puntos del defecto de convexidad que este en la posicion i, se calcula el angulo y las distancias
					s,e,f,d = defects[i,0]
					start = tuple(cnt[s][0])
					end = tuple(cnt[e][0])
					far = tuple(cnt[f][0])
					depth = d/256.0
					ang = angle(start,end,far)

					# Se calcula el tamano horizontal y vertical del rectangulo
					vertical_size = float(abs((pt2[1] - pt1[1])))
					horizontal_size = float(abs((pt2[0] - pt1[0])))

					# En el caso de que el angulo del defecto de convexidad sea menor de 90 y tenga una longitud mayor de 50p, sera un dedo
					if  ang <= 90:
						if depth > 50:
							finger_cnt += 1
							cv2.circle(frame, far, 4, [0, 0, 255], -1)
							cv2.line(frame,start,end,[255,0,0],2)

				# Si hay mas de un dedo, empiezan a detectarse posibles gestos
				if finger_cnt > 0:
					finger_cnt = finger_cnt + 1

					# end es el dedo de la izquierda, start es el dedo de la derecha
					cv2.circle(frame, start, 10, [255, 255, 0], -1)
					cv2.circle(frame, end, 10, [255, 255, 255], -1)

					# Se calculan las distancias de las puntas de los dedos con los bordes del bounding rect
					distY_d_izq_esq_sup_izq = abs(end[1] - pt1[1]) / float(vertical_size) * 100
					distY_d_der_esq_sup_izq = abs(start[1] - pt1[1]) / float(vertical_size) * 100
					distX_d_izq_esq_sup_izq = abs(end[0] - pt1[0]) / float(horizontal_size) * 100
					distX_d_der_esq_sup_izq = abs(start[0] - pt1[0]) / float(horizontal_size) * 100
					# print(f'{distY_d_izq_esq_sup_izq}  -  {distY_d_der_esq_sup_izq}  -  {distX_d_izq_esq_sup_izq} - {distX_d_der_esq_sup_izq}')
					# print(distY_d_izq_esq_sup_izq, distY_d_der_esq_sup_izq, distX_d_izq_esq_sup_izq, distX_d_der_esq_sup_izq)
					
					# Gesto de la paz
					if finger_cnt == 2 and vertical_size > horizontal_size * 1.2:
						if distY_d_izq_esq_sup_izq < 11 and distY_d_der_esq_sup_izq < 11 and distX_d_izq_esq_sup_izq < 25:
							cv2.putText(frame, str("Paz hermano"), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0) , 2, cv2.LINE_AA)
							nuevo_punto = start
						if distY_d_izq_esq_sup_izq < 1 and distY_d_der_esq_sup_izq < 1 and distX_d_izq_esq_sup_izq < 91 and distX_d_der_esq_sup_izq < 100:
							if distY_d_izq_esq_sup_izq >= 0 and distY_d_der_esq_sup_izq >= 0 and distX_d_izq_esq_sup_izq > 60 and distX_d_der_esq_sup_izq > 64:
								cv2.putText(frame, str("Paz hermano"), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0) , 2, cv2.LINE_AA)
								nuevo_punto = start

					# Gesto rockero
					if finger_cnt == 3:
						if distY_d_izq_esq_sup_izq < 2 and distY_d_der_esq_sup_izq < 25 and distX_d_izq_esq_sup_izq < 45 and distX_d_der_esq_sup_izq < 100:
							if distY_d_izq_esq_sup_izq >= 0 and distY_d_der_esq_sup_izq > 10 and distX_d_izq_esq_sup_izq > 15 and distX_d_der_esq_sup_izq > 61:
								cv2.putText(frame, str("Rock & Roll"), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0) , 2, cv2.LINE_AA)

				# En el caso de que no hayan defectos de convexidad, es posible que se este levantando solo un dedo.
				elif finger_cnt == 0:
					# En el caso de levantar el dedo indice, corazon, anular o menique
					if vertical_size / horizontal_size > 1.5:
						finger_cnt = finger_cnt + 1

					# En el caso de levantar el dedo pulgar
					elif horizontal_size / vertical_size > 1.2:
						finger_cnt = finger_cnt + 1

	# Se imprime el numero de dedos en la imagen	
	cv2.putText(frame, str(finger_cnt), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0) , 2, cv2.LINE_AA)
	
	# En el caso de que este activado el modo pintar, se imprimen todos los puntos almacenados
	if (imprimir_puntos == True):
		if nuevo_punto.__class__ == tuple:
			if nuevo_punto[0].__class__ == np.int32:
				todos_puntos.append(nuevo_punto)
		for i in todos_puntos:
			cv2.circle(frame, i, 10, [150, 55, 50], -1)
	
	cv2.imshow('Contours',frame)
	return nuevo_punto

