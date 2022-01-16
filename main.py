

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

print("Comandos:\n  Pulse 's' para establecer el learning rate a 0\n  Pulse 'a' para que establecer el learning rate a -1\n  Pulse 'p' para empezar a pintar(funciona con dos dedos levantaods)\n  Pulse 'b' para borrar lo pintado")
if mode == '0':
  dependencias.abrirCamara()
elif mode == '1':
  dependencias.abrirVideo('media/test.avi')
