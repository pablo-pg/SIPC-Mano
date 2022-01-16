

import dependencias
mode = '20'

# Permite al usuario entre abrir la cámara o un vídeo
while mode != '1' or mode != '0':
  mode = input("Quiere usar la camara o un video?\n0 - camara\n1 - video\nIntroduzca el valor: ")
  if mode == '1':
    break
  elif mode == '0':
    break
  else:
    print("\n\nOpcion incorrecta.\n")

if mode == '0':
  dependencias.abrirCamara()
elif mode == '1':
  dependencias.abrirVideo('media/test.avi')
