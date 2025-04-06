import cv2  # OpenCV: procesamiento de imagen y cámara
import mediapipe as mp  # MediaPipe: para seguimiento de manos
import numpy as np  # NumPy: operaciones matemáticas

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Configurar cámara
cap = cv2.VideoCapture(0)

# Objeto virtual (una caja)
box_center = [250, 250]
box_size = 100
dragging = False

def is_pinching(hand_landmarks):
    """Detecta si el índice y el pulgar están cerca (gesto de pinza)"""
    index_tip = hand_landmarks.landmark[8]
    thumb_tip = hand_landmarks.landmark[4]
    distance = np.linalg.norm(np.array([index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y]))
    return distance < 0.05

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Procesar imagen
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Obtener posición del dedo índice
            index_finger = hand_landmarks.landmark[8]
            cx, cy = int(index_finger.x * w), int(index_finger.y * h)

            # Comprobar si está haciendo "pinza"
            if is_pinching(hand_landmarks):
                # Si está sobre el objeto, activar el drag
                if (box_center[0] - box_size//2 < cx < box_center[0] + box_size//2 and
                    box_center[1] - box_size//2 < cy < box_center[1] + box_size//2):
                    dragging = True

                # Si está arrastrando, mover el objeto
                if dragging:
                    box_center = [cx, cy]
            else:
                dragging = False

            # Mostrar punto del índice
            cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)

    # Dibujar caja
    top_left = (box_center[0] - box_size//2, box_center[1] - box_size//2)
    bottom_right = (box_center[0] + box_size//2, box_center[1] + box_size//2)
    color = (0, 255, 0) if dragging else (0, 0, 255)
    cv2.rectangle(frame, top_left, bottom_right, color, -1)

    # Mostrar frame
    cv2.imshow("Drag & Drop con la Mano", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()