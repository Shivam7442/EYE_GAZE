import cv2
import mediapipe as mp
import numpy as np
import time
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# Constants
LEFT_IRIS = 468
RIGHT_IRIS = 473
canvas_width, canvas_height = 800, 600

# 12-point calibration
calibration_targets = [
    (int(canvas_width * 0.1), int(canvas_height * 0.1)),  # Top-left
    (int(canvas_width * 0.9), int(canvas_height * 0.1)),  # Top-right
    (int(canvas_width * 0.1), int(canvas_height * 0.9)),  # Bottom-left                                
    (int(canvas_width * 0.9), int(canvas_height * 0.9)),  # Bottom-right
    (int(canvas_width * 0.5), int(canvas_height * 0.1)),  # Top-center
    (int(canvas_width * 0.5), int(canvas_height * 0.9)),  # Bottom-center
    (int(canvas_width * 0.1), int(canvas_height * 0.5)),  # Left-center
    (int(canvas_width * 0.9), int(canvas_height * 0.5)),  # Right-center
    (int(canvas_width * 0.3), int(canvas_height * 0.3)),  # Inner top-left
    (int(canvas_width * 0.7), int(canvas_height * 0.3)),  # Inner top-right
    (int(canvas_width * 0.3), int(canvas_height * 0.7)),  # Inner bottom-left
    (int(canvas_width * 0.7), int(canvas_height * 0.7)),  # Inner bottom-right
]

input_iris = []
output_screen = []

# Init video capture
cap = cv2.VideoCapture(0)
print("🧠 Calibration: Look at the red dots...")

# Setup MediaPipe
mp_face_mesh = mp.solutions.face_mesh
drawing_utils = mp.solutions.drawing_utils
drawing_spec = drawing_utils.DrawingSpec(thickness=1, circle_radius=1)

with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
    for point in calibration_targets:
        tx, ty = point
        start_time = time.time()
        while time.time() - start_time < 2:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (canvas_width, canvas_height))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            # Draw face mesh if detected
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    drawing_utils.draw_landmarks(
                        frame,
                        face_landmarks,
                        mp_face_mesh.FACEMESH_TESSELATION,
                        drawing_spec,
                        drawing_spec,
                    )
                landmarks = results.multi_face_landmarks[0].landmark
                lx, ly = landmarks[LEFT_IRIS].x, landmarks[LEFT_IRIS].y
                rx, ry = landmarks[RIGHT_IRIS].x, landmarks[RIGHT_IRIS].y
                cx, cy = (lx + rx) / 2, (ly + ry) / 2
                input_iris.append([cx, cy])
                output_screen.append([tx, ty])

            # Draw red calibration dot
            cv2.circle(frame, (tx, ty), 20, (0, 0, 255), -1)

            # Show full-screen window
            cv2.namedWindow("Calibration", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Calibration", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                exit()

    cv2.destroyWindow("Calibration")
    print("✅ Calibration complete. Building model...")

    # Train regression model
    model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    model.fit(np.array(input_iris), np.array(output_screen))

    print("🎯 Model ready. Launching real-time gaze tracker...")

    # Gaze Tracker
    smooth_x, smooth_y = canvas_width // 2, canvas_height // 2
    smoothing_factor = 0.15

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if 'canvas' not in locals():
            canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            lx, ly = landmarks[LEFT_IRIS].x, landmarks[LEFT_IRIS].y
            rx, ry = landmarks[RIGHT_IRIS].x, landmarks[RIGHT_IRIS].y
            cx, cy = (lx + rx) / 2, (ly + ry) / 2

            pred_x, pred_y = model.predict([[cx, cy]])[0]
            smooth_x = int((1 - smoothing_factor) * smooth_x + smoothing_factor * pred_x)
            smooth_y = int((1 - smoothing_factor) * smooth_y + smoothing_factor * pred_y)

        canvas[:] = 255
        cv2.circle(canvas, (smooth_x, smooth_y), 20, (0, 0, 255), -1)

        cv2.namedWindow("Gaze Tracker", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Gaze Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Gaze Tracker", canvas)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()