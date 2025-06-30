import cv2
import mediapipe as mp
import numpy as np

class FaceMeshDetector:
    """
    Face mesh detection using MediaPipe for eye tracking.
    """
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # MediaPipe face mesh indices for eyes
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
    def get_eye_features(self, frame):
        """
        Extract eye features from the frame.
        
        Args:
            frame (np.ndarray): Input frame in BGR format
            
        Returns:
            np.ndarray: Eye feature vector or None if no face detected
        """
        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return None
            
        # Get face landmarks
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extract eye regions
        left_eye = self._extract_eye_region(frame, face_landmarks, self.LEFT_EYE_INDICES)
        right_eye = self._extract_eye_region(frame, face_landmarks, self.RIGHT_EYE_INDICES)
        
        if left_eye is None or right_eye is None:
            return None
            
        # Combine features from both eyes
        features = np.concatenate([left_eye, right_eye])
        return features
    
    def _extract_eye_region(self, frame, landmarks, eye_indices):
        """
        Extract and process eye region.
        
        Args:
            frame (np.ndarray): Input frame
            landmarks: MediaPipe face landmarks
            eye_indices: Indices of eye landmarks
            
        Returns:
            np.ndarray: Processed eye features
        """
        # Get eye landmarks
        eye_points = []
        for idx in eye_indices:
            landmark = landmarks.landmark[idx]
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            eye_points.append((x, y))
            
        # Convert to numpy array
        eye_points = np.array(eye_points)
        
        # Get bounding box
        x_min, y_min = np.min(eye_points, axis=0)
        x_max, y_max = np.max(eye_points, axis=0)
        
        # Add padding
        padding = 5
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(frame.shape[1], x_max + padding)
        y_max = min(frame.shape[0], y_max + padding)
        
        # Extract eye region
        eye_region = frame[y_min:y_max, x_min:x_max]
        
        if eye_region.size == 0:
            return None
            
        # Resize to fixed size
        eye_region = cv2.resize(eye_region, (10, 6))
        
        # Convert to grayscale
        eye_region = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        
        # Normalize
        eye_region = eye_region.astype(np.float32) / 255.0
        
        # Flatten
        return eye_region.flatten()
    
    def draw_face_mesh(self, frame, landmarks):
        """
        Draw face mesh on the frame.
        
        Args:
            frame (np.ndarray): Input frame
            landmarks: MediaPipe face landmarks
            
        Returns:
            np.ndarray: Frame with face mesh drawn
        """
        frame_copy = frame.copy()
        
        # Draw all landmarks
        for landmark in landmarks.landmark:
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            cv2.circle(frame_copy, (x, y), 1, (0, 255, 0), -1)
            
        # Draw eye regions
        for eye_indices in [self.LEFT_EYE_INDICES, self.RIGHT_EYE_INDICES]:
            points = []
            for idx in eye_indices:
                landmark = landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                points.append((x, y))
            points = np.array(points, np.int32)
            cv2.polylines(frame_copy, [points], True, (0, 0, 255), 1)
            
        return frame_copy 