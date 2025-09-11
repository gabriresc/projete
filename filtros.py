import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from PIL import Image

def process():

    model = YOLO("Gray_Blur.pt")
    im = cv2.imread("./img/img3.jpeg")
    # Processamento exemplo: escala de cinza
    imagem = cv2.resize(im, (800, 800))

    # Remove tons de azul com HSV
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    lower_blue = (115, 30, 50)   # limite inferior (H, S, V)
    upper_blue = (125, 160, 255)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Limpeza da máscara
    kernel_small = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel_small)

    # Dilatação para garantir remoção completa
    kernel_large = np.ones((5, 5), np.uint8)
    mask_dilated = cv2.dilate(mask_clean, kernel_large, iterations=2)

    # Remove azul da imagem original
    imagem_sem_azul = cv2.inpaint(imagem, mask_dilated, 3, cv2.INPAINT_TELEA)

    # Pré-processamento: grayscale + blur
    gray = cv2.cvtColor(imagem_sem_azul, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    #Com IA
    img_rgb = cv2.cvtColor(blur, cv2.COLOR_BGR2RGB)
    results = model(img_rgb, iou=0.45)
    tamanho = 0
    min_y1 = float('inf')  # valor bem alto para começar
    box_ref = None
    num = 1
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()   # coordenadas [x1, y1, x2, y2]
        confs = r.boxes.conf.cpu().numpy()   # confiança
        classes = r.boxes.cls.cpu().numpy()  # classes preditas
            
        for box, conf, cls in zip(boxes, confs, classes):
            x1, y1, x2, y2 = map(int, box)
        
            if y1 < min_y1:
                min_y1 = y1
                tamanho = y2 - y1
                box_ref = (x1, y1, x2, y2)
            
        for box, conf, cls in zip(boxes, confs, classes):
            x1, y1, x2, y2 = map(int, box)
            w = y2 - y1
            if(tamanho>w):
                # Desenha retângulo
                cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Escreve classe + confiança
                label = f"{'Correto'} {conf:.2f} {num}"
                cv2.putText(img_rgb, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                # Desenha retângulo
                cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Escreve classe + confiança
                label = f"{'Incorreto'} {conf:.2f} {num}"
                cv2.putText(img_rgb, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            num += 1
    if box_ref:
        x1, y1, x2, y2 = box_ref
        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (255, 255, 0), 2)
        cv2.putText(img_rgb, "Referencia", (x1, y1 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.imshow("Deteccao", img_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



process()