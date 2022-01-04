# Main de la práctica de interacción gestuales
# 
# Asignatura: Sistemas de interacción persona-computador
# Universidad de La Laguna
# Diciembre de 2021
# Autores:
#     Ana Virginia Giambona Díaz (alu0101322650)
#     Pablo Pérez González (alu0101318318)

import dependencias
mode = '20'


while mode != '1' or mode != '0':
  mode = input("¿Quiere usar la cámara o un vídeo?\n0 - cámara\n1 - vídeo\nIntroduzca el valor: ")
  if mode == '1':
    break
  elif mode == '0':
    break
  else:
    print("\n\nOpción incorrecta.\n")

if mode == '0':
  dependencias.abrirCamara()
elif mode == '1':
  dependencias.abrirVideo('media/test.avi')
