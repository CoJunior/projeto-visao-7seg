

import cv2
import numpy as np
from collections import deque
import time

# Importa o módulo MQTT que criamos no outro arquivo
from comunicacao_mqtt import TransmissorMQTT

# --- CONFIGURAÇÕES DA CÂMERA E TELA ---
CAMERA_INDEX = 1  
CAM_WIDTH = 640
CAM_HEIGHT = 480
ROI_W = 560
ROI_H = 260
MOSTRAR_ROIS = True

# --- LIMIARES DE DETECÇÃO ---
LIMIAR_AZUL = 0.45  
LIMIAR_ICONE = 15  

# --- HISTÓRICO INDIVIDUALIZADO ---
HIST_SIZE = 2  
hist_D1 = deque(maxlen=HIST_SIZE)
hist_D2 = deque(maxlen=HIST_SIZE)
hist_D3 = deque(maxlen=HIST_SIZE)
hist_floco = deque(maxlen=HIST_SIZE)
hist_bateria = deque(maxlen=HIST_SIZE)

def abrir_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    return cap

def media_estavel(hist, valor):
    hist.append(valor)
    if len(hist) == 0: return valor
    return int(round(np.mean(hist)))

def criar_mascara_azul(hsv):
    lower_blue = np.array([95, 120, 120])
    upper_blue = np.array([135, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

def criar_mascara_vermelha(hsv):
    lower_red1 = np.array([0, 150, 120])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 150, 120])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

def densidade_roi(mask, roi):
    x, y, w, h = roi
    h_img, w_img = mask.shape
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(w_img, x + w), min(h_img, y + h)
    if x2 <= x1 or y2 <= y1: return 0.0
    recorte = mask[y1:y2, x1:x2]
    return np.sum(recorte == 255) / recorte.size

def intensidade_roi(mask, roi):
    x, y, w, h = roi
    h_img, w_img = mask.shape
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(w_img, x + w), min(h_img, y + h)
    if x2 <= x1 or y2 <= y1: return 0.0
    recorte = mask[y1:y2, x1:x2]
    return np.mean(recorte)

def verificar_segmentos(mask_blue, digito_roi):
    x, y, w, h = digito_roi
    rois = {
        "A": (x + int(w * 0.25), y + int(h * 0.02), int(w * 0.50), int(h * 0.08)), 
        "B": (x + int(w * 0.82), y + int(h * 0.18), int(w * 0.12), int(h * 0.25)), 
        "C": (x + int(w * 0.82), y + int(h * 0.58), int(w * 0.12), int(h * 0.25)), 
        "D": (x + int(w * 0.25), y + int(h * 0.90), int(w * 0.50), int(h * 0.08)), 
        "E": (x + int(w * 0.05), y + int(h * 0.58), int(w * 0.12), int(h * 0.25)), 
        "F": (x + int(w * 0.05), y + int(h * 0.18), int(w * 0.12), int(h * 0.25)), 
        "G": (x + int(w * 0.25), y + int(h * 0.46), int(w * 0.50), int(h * 0.08)), 
    }
    status = {}
    for seg, roi in rois.items():
        densidade = densidade_roi(mask_blue, roi)
        status[seg] = "ON" if densidade > LIMIAR_AZUL else "OFF"
    return status, rois

def desenhar_rois_segmentos(img, rois, status):
    for seg, (x, y, w, h) in rois.items():
        cor = (0, 255, 0) if status[seg] == "ON" else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), cor, 1)
        cv2.putText(img, seg, (x + int(w/2) - 5, y + int(h/2) + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor, 1)

# --- INÍCIO DO PROGRAMA PRINCIPAL ---
cap = abrir_camera()
mqtt_app = TransmissorMQTT()
mqtt_app.iniciar_conexao()

print("\n--- SISTEMA DE INSPEÇÃO QA (MODULARIZADO) ---")
print("Pressione 'q' na janela do vídeo para encerrar.")

while True:
    if not cap.isOpened():
        cap.release()
        time.sleep(1)
        cap = abrir_camera()
        continue

    ret, frame = cap.read()
    if not ret or frame is None:
        time.sleep(0.5)
        continue

    frame = cv2.flip(frame, -1)
    h_frame, w_frame = frame.shape[:2]
    x_roi = (w_frame - ROI_W) // 2
    y_roi = (h_frame - ROI_H) // 2
    
    cv2.rectangle(frame, (x_roi, y_roi), (x_roi + ROI_W, y_roi + ROI_H), (255, 255, 255), 2)
    painel = frame[y_roi:y_roi + ROI_H, x_roi:x_roi + ROI_W].copy()

    hsv_painel = cv2.cvtColor(painel, cv2.COLOR_BGR2HSV)
    mask_blue = criar_mascara_azul(hsv_painel)
    mask_red = criar_mascara_vermelha(hsv_painel)

    digitos = {
        "D1": (120, 80, 75, 120),
        "D2": (225, 80, 75, 120),
        "D3": (315, 80, 75, 120),
    }

    roi_bateria = (430, 60, 60, 50)
    roi_floco = (430, 150, 60, 50)

    # Lógica Floco
    intensidade_floco = intensidade_roi(mask_blue, roi_floco)
    floco_estavel = media_estavel(hist_floco, intensidade_floco)
    estado_floco, cor_floco = ("LIGADO", (255, 255, 0)) if floco_estavel > LIMIAR_ICONE else ("APAGADO", (200, 200, 200))

    # Anti-Bleeding (Erosão) e Zonas Cegas
    mask_blue_digits = mask_blue.copy()
    kernel_erosao = np.ones((3, 3), np.uint8)
    mask_blue_digits = cv2.erode(mask_blue_digits, kernel_erosao, iterations=2)
    mask_blue_digits[:, 195:220] = 0  
    mask_blue_digits[:, 390:560] = 0 

    textos_d = {}
    cores_d = {}
    
    # Dicionário temporário para repassar ao MQTT
    status_para_mqtt = {}

    for nome, roi_digito in digitos.items():
        status, rois_seg = verificar_segmentos(mask_blue_digits, roi_digito)
        status_para_mqtt[nome] = status 
        
        ligados = [s for s, v in status.items() if v == "ON"]
        apagados = [s for s, v in status.items() if v == "OFF"]
        qtd_ligados = len(ligados)
        
        estavel = media_estavel(eval(f"hist_{nome}"), qtd_ligados)
            
        if estavel == 7:
            textos_d[nome] = f"{nome}: TODOS ACESOS (OK)"
            cores_d[nome] = (0, 255, 0)
        elif estavel == 0:
            textos_d[nome] = f"{nome}: APAGADO (OFF)"
            cores_d[nome] = (0, 255, 255) 
        else:
            str_on = ",".join(ligados) if ligados else "-"
            str_off = ",".join(apagados) if apagados else "-"
            textos_d[nome] = f"{nome}: ON [{str_on}] | QUEIMADOS: [{str_off}]"
            cores_d[nome] = (0, 0, 255)

        if MOSTRAR_ROIS:
            desenhar_rois_segmentos(painel, rois_seg, status)
            x, y, w, h = roi_digito
            cv2.rectangle(painel, (x, y), (x + w, y + h), (255, 255, 255), 1)
            cv2.putText(painel, f"{nome}: {estavel}/7", (x - 5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, cores_d[nome], 2)

    # Lógica Bateria
    intensidade_bateria = intensidade_roi(mask_red, roi_bateria)
    bateria_estavel = media_estavel(hist_bateria, intensidade_bateria)
    estado_bateria, cor_bateria = ("LIGADA", (0, 0, 255)) if bateria_estavel > LIMIAR_ICONE else ("APAGADA", (200, 200, 200))

    # --- ENVIO DOS DADOS (Chamando o módulo modularizado) ---
    mqtt_app.publicar_status(status_para_mqtt, estado_floco, estado_bateria)

    # Interface Visual
    if MOSTRAR_ROIS:
        for nome, roi_aux, cor in [("BATERIA", roi_bateria, cor_bateria), ("FLOCO", roi_floco, cor_floco)]:
            x, y, w, h = roi_aux
            cv2.rectangle(painel, (x, y), (x + w, y + h), cor, 2)
            cv2.putText(painel, nome, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, cor, 1)

    cv2.putText(frame, "STATUS DOS DIGITOS:", (x_roi, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, textos_d["D1"], (x_roi, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cores_d["D1"], 2)
    cv2.putText(frame, textos_d["D2"], (x_roi, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cores_d["D2"], 2)
    cv2.putText(frame, textos_d["D3"], (x_roi, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cores_d["D3"], 2)
    cv2.putText(frame, "ALINHE A PLACA (MIRA) AQUI DENTRO", (x_roi, y_roi - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    y_bottom = y_roi + ROI_H + 25 
    cv2.putText(frame, f"FLOCO: {estado_floco}", (x_roi, y_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_floco, 2)
    cv2.putText(frame, f"BATERIA: {estado_bateria}", (x_roi + 250, y_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_bateria, 2)

    cv2.imshow("Sistema QA - Camera", frame)
    cv2.imshow("Gabarito de Inspecao (Alinhado)", painel)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Encerramento limpo
mqtt_app.encerrar()
cap.release()
cv2.destroyAllWindows()

    
    
    
    
  