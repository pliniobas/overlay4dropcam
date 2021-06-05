# -*- coding: utf-8 -*-
"""
Created on Sun May 30 23:48:33 2021

@author: plinio silva
"""

import cv2 as cv
import time
import sys
import datetime
import os
import json
import serial
import socket

print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
print("APERTE A TECLA Q PARA FECHAR A JANELA DE VIDEO E ENCERRAR O PROGRAMA")
time.sleep(0.2)


#%%Arquivo de configurações. Se não existir, criará um padrão.
try:
    with open('dropOverlay-config.txt') as f:
        temp = f.read()
        config = json.loads(temp)
except Exception as e:
    print(e)
    print("Nao foi possivel abrir arquivo de configuração. Criando modelo novo.")
    config = dict(
                camperaip = "rtsp://10.0.0.1",
                legrec = "Escrever rec para gravar ou qualquer outra coisa para pausar",
                rec = "stop",
                recloc = (640,20),
                legloc = "locs sao distancia do canto superior direito (horizontal,vertical)",
                cia1text = "cia1text\ncia1text\ncia1text",
                cia1loc = (10,20),
                cia1logo = "logo1.jpg",
                cia1logopos = (20,80),
                cia1logoscale = 1,
                cia2text = "cia2text",
                cia2loc = (500,20),
                cia2logo = "logo2.jpg",
                cia2logopos = (1000,60),
                cia2logoscale = 1.5,
                dateloc = (20,900),
                utmloc = (980,800),
                depthloc = (490,450),
                targetloc = (500,500),
                fontScale = 1,
                lfjump = 30, 
                color = (0, 255, 255),
                thickness = 2,
                fps = 15,
                zoom = 2,
                zoomtlocprop = 2,
                serialouIP = "IP",
                legenda1 = "Entrada de dados Shared Memory da porta serial",
                comport = "COM30",
                baudrate = 9600,
                legTCP = "Entrada de dados Share Memoru via porta TCP",
                TCP_IP = "127.0.0.1",
                TCP_PORT = 8001,
                legUTM = 'UTM 23 S'
                )
    temp = json.dumps(config,indent = 4)
    with open('dropOverlay-config.txt','w') as f:
        f.write(temp)
        f.close()
    print("Verifique as configuracoes de porta ou IP no novo modelo de arquivo de configuracao ")
    print("encerrando o programa")
    time.sleep(3)
    sys.exit(5)




#%%Ou brindo a porta TCP 

comport = config["comport"]
baudrate = config["baudrate"]
TCP_IP = config["TCP_IP"]
TCP_PORT = config["TCP_PORT"]

if config["serialouIP"] == "IP":
    TCP_IP = TCP_IP
    TCP_PORT = TCP_PORT
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.0001)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except Exception as e:
        print(e)
        print("Nao foi possivel conectar a porta TCP em %s na porta %d"%(TCP_IP,TCP_PORT))
        print("Verifique e tente novamente")
        s.close()
        
#%%Ou abrindo a porta Serial 
elif config["serialouIP"] == "serial" or config["serialouIP"] == "Serial":
    try:
        ser = serial.Serial(comport, baudrate, timeout=2)
    except Exception as e:
        print(e)
        print("A porta serial nao pode ser aberta. Tentando novamente")
        # time.sleep(10)
        ser.close()
        sys.exit(11)

else:
    pass


#%%
# os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# cap = cv.VideoCapture("rtsp://10.0.0.1/",cv.CAP_FFMPEG) #Captura da dropcam. Comentar ou descomentar
# cap = cv.VideoCapture("rtsp://10.0.0.1/",cv.CAP_FFMPEG) #Captura da dropcam. Comentar ou descomentar
# cap = cv.VideoCapture(0) #captura da webcam. #Comentar ou descomentar
if config['cameraip']:
    cap = cv.VideoCapture(config['cameraip'],cv.CAP_FFMPEG)
    # cap = cv.VideoCapture("rtsp://10.0.0.1/") #Captura da dropcam. Comentar ou descomentar
else:
    cap = cv.VideoCapture(0,cv.CAP_DSHOW) #captura da webcam. #Comentar ou descomentar


if not cap.isOpened():
    print("Cannot open camera")
    sys.exit()
    
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))


#mudar o tamanho do frame de video
zoom = config["zoom"]
tprop = config["zoomtlocprop"]
size = (frame_width*zoom, frame_height*zoom)

# fps = cap.get(cv.CAP_PROP_FPS)
# print('fps = ',fps)
fps = config["fps"]
print('fps = ',fps)
# Below VideoWriter object will create
# a frame of above defined The output 
video_filename = "video_" + datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S") + '.avi'
result = cv.VideoWriter(video_filename, 
                         cv.VideoWriter_fourcc(*'XVID'),
                         fps,#fps é referente ao frame rate da camera
                         size) 


#%%LENDO UM FRAME DO LADO DE FORA DO LOOP PARA CALCULAR O OVERLAY DO LOGO

# t0 = time.time()
# while not frame:
# ret, frame = cap.read()

# frame = cv.resize(frame,size,fx=0,fy=0, interpolation = cv.INTER_CUBIC)
# if frame is read correctly ret is True
# if not ret:
#     print("Can't receive frame (stream end?). Exiting ...")
    
#%%

def transparentOverlay(src, overlay, pos=(0, 0), scale=1):
    """
    :param src: Input Color Background Image
    :param overlay: transparent Image (BGRA)
    :param pos:  position where the image to be blit.
    :param scale : scale factor of transparent image.
    :return: Resultant Image
    """
    overlay = cv.resize(overlay, (0, 0), fx=scale, fy=scale)
    h, w, _ = overlay.shape  # Size of foreground
    rows, cols, _ = src.shape  # Size of background Image
    y, x = pos[0], pos[1]  # Position of foreground/overlay image
    rx = x+h
    ry = y+w 
    try:
        src[ x:rx , y:ry,:] = overlay
    except Exception as e:
        print(e)
        print("Antecao para que a posicao do logo nao exceda as marges da imagem")
        print("PARA INSERIR O LOGO, PRIMEIRO COLOQUE AS \"cia1logopos\" : (0,0)")
        time.sleep(2)
        
    # a = src[ x:rx , y:ry,:]
    # overlay = cv.imread(config['cia2logo'], -1)
    # pos = config['cia2logopos']
    # src = framecopy.copy()
    
    return src



#%%
#%%
#%%
#%%
rec = config['rec']

hydata = 'x x x x x x x x x x x x x x\r\n' #temporario enquanto a porta nao pega dados do shared memory
while True:
   
    #%%CAPTURA O FRAME DA CAMERA
    # Capture frame-by-frame
    ret, frame = cap.read()
    try:
        frame = cv.resize(frame,size,fx=0,fy=0, interpolation = cv.INTER_CUBIC)
    except Exception as e:
        print(e)
        print("Conexao com a camera perdida. Ira encerrar o programa")
        time.sleep(3)
        break
    
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    #%%INSERE LOGOTIPOS

    if config['cia1logo']:
        waterImg = cv.imread(config['cia1logo'], -1)
        pos = config['cia1logopos']
        framecopy = frame.copy()
        # opacity = 1
        
        frame = transparentOverlay(framecopy, waterImg, pos, scale=config['cia1logoscale'])
        # logo1overlay = transparentOverlay(framecopy, waterImg, pos, scale=config['cia1logoscale'])
        # frame = cv.addWeighted(logo1overlay, opacity, frame, 0, 0,frame)
        
    if config['cia2logo']:
        waterImg = cv.imread(config['cia2logo'], -1)
        pos = config['cia2logopos']
        framecopy = frame.copy()
        
        
        frame = transparentOverlay(framecopy, waterImg, pos, scale=config['cia2logoscale'])
        # frame = transparentOverlay(framecopy, waterImg, pos, scale=config['cia2logoscale'])
        # logo1overlay = transparentOverlay(framecopy, waterImg, pos, scale=config['cia2logoscale'])
        # frame = cv.addWeighted(logo1overlay, opacity, frame, 0, 0,frame)
    
    #%%CAPTURA A STRING DO SHARED MEMORY
    if config["serialouIP"] == "IP":
        try:
            hydata = s.recv(BUFFER_SIZE).decode().split('\r\n')[-2]
        except:
            pass
        
    elif config["serialouIP"] == "serial" or config["serialouIP"] == "Serial":
        hydata = ser.read_all().decode().split('\n')
        
    else:
        hydata = """config["serialouIP"] tem que ser ou serial ou IP"""
    
    #%%CONFIGURACOES DE FONTE DEFAULT
    window_name = 'Image' # Window name in which image is displayed
    font = cv.FONT_HERSHEY_SIMPLEX # font
    # fontScale = 1
    # lfjump = 30 * fontScale #esse eh o tamanho da fonte para calcular nova posicao. Caso haja quebra de linha (\n) 
    # color = (255, 255, 255)
    # thickness = 2

    
    #%%CONFIGURACOES EM TEMPO REAL NO ARQUIVO TXT / JSON
    try:
        with open('dropOverlay-config.txt') as f:
            temp = f.read()
            config = json.loads(temp)   
    
        cia1loc = config["cia1loc"]
        cia2loc = config["cia2loc"]
        dateloc = config["dateloc"]
        utmloc = config["utmloc"]
        depthloc = config["depthloc"]
        targetloc = config["targetloc"]
        fontScale = config["fontScale"]
        lfjump = config["lfjump"]
        color = config["color"]
        thickness = config["thickness"]
        tprop = config["zoomtlocprop"]
    
    except:
        pass
   
    #%%NOME DO CLIENTE
    texto = config['cia1text']
    # org = (10 ,20 ) #Local - distancia do canto superior direito (horizontal,vertical)
    org = (cia1loc[0] ,cia1loc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA)

    #%%NOME DO PRESTADOR DE SERVICO
    texto = config['cia2text']
    # org = (500,20) #Local - distancia do canto superior direito (horizontal,vertical)
    org = (cia2loc[0],cia2loc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA)
        
    #%%DATA E HORA EXTRAIDA DO COMPUTADOR LOCAL
    texto = datetime.datetime.now().strftime("%d/%m/%Y\n%H:%M:%S UTC")
    # org = (10,330) #Local - distancia do canto superior direito (horizontal,vertical)
    org = (dateloc[0],dateloc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA) 

    #%%INFORMACAOS DO HYPACK 1
    temp = hydata.replace('\n','').replace('\r','').split(' ')
    texto = config['legUTM'] + '\n'
    texto += "N: %s"%temp[1] + '\n'
    texto += "E: %s"%temp[0]
    # sys.exit()
    org = (utmloc[0],utmloc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA) 
        
    #%%INFORMACAOS DO HYPACK 2
    temp = hydata.replace('\n','').replace('\r','').split(' ')
    texto = "localDepth: %s"%temp[2] + '\n'
    texto += "CamDepth: %s"%temp[3]
    
    org = (depthloc[0],depthloc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA) 

    #%%INFORMACAOS DO HYPACK 3 - TARGET
    temp = hydata.replace('\n','').replace('\r','').split(' ')
    texto = "tgt %s"%temp[4]

    org = (targetloc[0],targetloc[1]) #Local - distancia do canto superior direito (horizontal,vertical)
    for ix, line in enumerate(texto.split('\n')): #loop para caso hava quebra de linha (\n)
        org2 = (org[0],org[1]+ix*lfjump) 
        cv.putText(frame, line, org2, font, fontScale, color, thickness, cv.LINE_AA) 

    #%%REC
    fontScale2 = 0.5
    org2 = config['recloc']
    text = rec
    if rec == "rec":
        colorrec = (0,0,255)
    else:
        colorrec = (255,255,255)

    cv.putText(frame, rec, org2, font, fontScale2, colorrec, thickness, cv.LINE_AA)     
    #%%VIDEO DISPLAY
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv.imshow('frame',frame)
    
    #%%VIDEO RECORD
    # Write the frame into the
    if rec == "rec":
        result.write(frame)
    
    if cv.waitKey(10) == ord('r'):
        if rec == "rec":
            rec = 'stop'
        else:
            rec = 'rec'
                
    if cv.waitKey(10) == ord('q'):
        break
    
# When everything done, release the capture
result.release()
cap.release()
cv.destroyAllWindows()

# %%
