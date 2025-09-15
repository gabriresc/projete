from ultralytics import YOLO
from flask import Flask, jsonify, request
import cv2
import numpy as np
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)


# Rota POST que recebe dados do Dart
@app.route('/process', methods=['POST'])
def process():

    data = request.get_json("imagem")

    imagem_base64 = data.get("imagem")
    if not imagem_base64:
        return jsonify(error="Nenhuma imagem recebida"), 400

    
    # Decodifica Base64
    img_bytes = base64.b64decode(imagem_base64)
    np_arr = np.frombuffer(img_bytes,dtype=np.uint8)

    # Converte para OpenCV
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify(error="Imagem inválida ou corrompida"), 400
    model = YOLO("Gray_Blur.pt")
    # Processamento exemplo: escala de cinza
    imagem = cv2.resize(img, (800, 800))

    # Remove tons de azul com HSV
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    lower_blue = (90, 50, 20)
    upper_blue= (130, 255, 255)
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

 # valor bem alto para começar
    box_ref = None
    boxes_all = []

    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()   # coordenadas [x1, y1, x2, y2]
        confs = r.boxes.conf.cpu().numpy()   # confiança
        classes = r.boxes.cls.cpu().numpy()
          # classes preditasaa
        min_y1 = float('inf')
        tamanho = 0
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
        
            if y1 < min_y1:
                min_y1 = y1
                tamanho = y2 - y1
                box_ref = (x1, y1, x2, y2)
        num = 1 
        for box, conf, cls in zip(boxes, confs, classes):
            x1, y1, x2, y2 = map(int, box)
            w = y2 - y1
            verificador = 0
            if(tamanho>w):
                verificador = 1
                # Desenha retângulo
                cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Escreve  classe + confiança
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
            boxes_all.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                'veri':verificador
            })
            num += 1
    
    if box_ref:
        x1, y1, x2, y2 = box_ref
        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (255, 255, 0), 2)
        cv2.putText(img_rgb, "Referencia", (x1, y1 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("Deteccao", img_rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return jsonify({"boxes": boxes_all}),200


if __name__ == '__main__':
    app.run(debug=True, port=5000)