# Python Eye Tracking Implementation

This project implements an eye tracking system using Python, OpenCV, and MediaPipe. It provides a calibration-based gaze estimation system similar to WebGazer.js but with improved performance and easier integration into Python applications.

## Features

- Real-time eye tracking using MediaPipe Face Mesh
- Ridge regression-based gaze prediction
- Kalman filtering for smooth predictions
- 9-point calibration system
- Real-time visualization
- Modular design for easy integration

## Requirements

- Python 3.7 or higher
- OpenCV
- MediaPipe
- NumPy
- SciPy
- Matplotlib (for visualization)
- PyQt5 (for GUI)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd pythonimp
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Demo

To run the demo application:

```bash
python examples/calibration_demo.py
```

The demo provides a simple interface for calibrating and testing the eye tracking system:

- Press 'c' to start calibration
- Click on each calibration point 5 times
- After calibration, the system will show your gaze prediction in real-time
- Press 'q' to quit

### Calibration Process

1. Start the demo application
2. Press 'c' to begin calibration
3. A red dot will appear on the screen
4. Click on the dot 5 times while looking at it
5. The dot will move to the next calibration point
6. Repeat for all 9 points
7. After calibration, the system will show your gaze prediction in real-time

### Integration into Your Project

To use the eye tracking system in your own project:

```python
from src.face_mesh import FaceMeshDetector
from src.ridge_regression import RidgeRegression
from src.kalman_filter import KalmanFilter

# Initialize components
face_detector = FaceMeshDetector()
ridge_regression = RidgeRegression()
kalman_filter = KalmanFilter()

# Process a frame
frame = ... # Your video frame
eye_features = face_detector.get_eye_features(frame)

if eye_features is not None:
    # Get prediction
    prediction = ridge_regression.predict(eye_features)
    
    if prediction:
        # Apply Kalman filter for smooth predictions
        filtered_pred = kalman_filter.update([prediction['x'], prediction['y']])
        gaze_x, gaze_y = filtered_pred
```

## Project Structure

```
pythonimp/
├── examples/
│   └── calibration_demo.py
├── src/
│   ├── data_window.py
│   ├── face_mesh.py
│   ├── kalman_filter.py
│   └── ridge_regression.py
├── README.md
└── requirements.txt
```

## Key Components

- `data_window.py`: Implements a circular buffer for storing calibration data
- `face_mesh.py`: Handles face detection and eye feature extraction using MediaPipe
- `kalman_filter.py`: Implements a Kalman filter for smoothing gaze predictions
- `ridge_regression.py`: Implements ridge regression for gaze prediction
- `calibration_demo.py`: Demo application showing the system in action

## Customization

You can customize various aspects of the system:

- Adjust the ridge parameter in `RidgeRegression` for different regularization strengths
- Modify the Kalman filter parameters in `KalmanFilter` for different smoothing levels
- Change the number of calibration points or clicks per point in `CalibrationDemo`
- Adjust the eye feature extraction parameters in `FaceMeshDetector`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 