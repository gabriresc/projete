from flask import Flask, jsonify, request
import cv2
import numpy as np
import base64

app = Flask(__name__)


# Rota POST que recebe dados do Dart
@app.route('/process', methods=['POST'])
def process():

    nome = request.json.get("nome")
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

    # Processamento exemplo: escala de cinza
    imagem = cv2.resize(img, (400, 400))

    # Remove tons de azul com HSV
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 30, 50])
    upper_blue = np.array([125, 160, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Limpeza da máscara
    kernel_small = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel_small)

    # Dilatação para garantir remoção completa
    kernel_large = np.ones((5, 5), np.uint8)
    mask_dilated = cv2.dilate(mask_clean, kernel_large, iterations=2)

    # Remove azul da imagem original
    imagem_sem_azul = cv2.inpaint(imagem, mask_dilated, 3, cv2.INPAINT_TELEA)

    # Pré-processamento: grayscale + blur
    gray = cv2.cvtColor(imagem_sem_azul, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Detecção de bordas
    canny = cv2.Canny(blur, threshold1=100, threshold2=200)

    # Fechamento morfológico para unir bordas
    kernel_close = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(canny, kernel_close, iterations=1)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel_close)
    cv2.imshow("Resultado",closed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Detecção de contornos na imagem já dilatada
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Cria imagem apenas com círculos válidos desenhados
    resultado_circulos = imagem_sem_azul.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)

        if perimeter == 0:
            continue

        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        # Filtra apenas contornos quase circulares e com área adequada
        if 0.5 < circularity <= 1 and area >  100:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            if 5 < radius < 30:
                center = (int(x), int(y))
                radius = int(radius)
                diameter = 2 * radius
                cv2.circle(resultado_circulos, center, radius, (0, 255, 0), 2)
                cv2.putText(resultado_circulos, f"D={diameter}", (center[0] - 40, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    cv2.imshow("Resultado", resultado_circulos)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return jsonify(msg=f"Imagem processada e salva com sucesso {nome}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)