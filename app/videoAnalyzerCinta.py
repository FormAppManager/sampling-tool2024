import datetime
import numpy as np
import pandas as pd
import cv2
import os
from ultralytics import YOLO

class VideoAnalyzerCinta:
    def __init__(self, path, roiArea, name):
        self.nameVideo = name
        self.cap = cv2.VideoCapture(path)
        self.CONFID = 0.2
        self.aparicion = []
        self.tipoObj = []
        self.difTiempo = []
        self.size = (640, 640)
        self.classNames = {1: 'vacio', 3: "carrito completo", 2: "Carrito incompleto", 0: "Carrito vacio"}
        self.roiArea = roiArea
        self.df = pd.DataFrame(columns=["Tiempo de aparición", "Tipo de objeto", "Diferencia de tiempo"])
        self.model = YOLO("src/models/best.pt")
        self.skip_frames = 15  # Number of frames to skip after detection
        self.frame_skip_counter = 0
        self.analysis_interval = 5  # Analyze every 5 frames

    def __del__(self):
        self.cap.release()

    @staticmethod
    def format_timedelta(delta):
        seconds = int(delta.total_seconds())
        secs_in_a_hour = 3600
        secs_in_a_min = 60
        hours, seconds = divmod(seconds, secs_in_a_hour)
        minutes, seconds = divmod(seconds, secs_in_a_min)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def analyze(self):
        frame_count = 0
        prev_time = None

        while True:
            frame_count += 1
            check, frame = self.cap.read()
            if not check:
                break

            # Skip frames if necessary
            if frame_count % self.analysis_interval != 0:
                continue

            if self.frame_skip_counter > 0:
                self.frame_skip_counter -= 1
                continue

            # Resize frame to YOLO input size
            frame_resized = cv2.resize(frame, self.size)
            # Create a mask for the ROI
            mask = np.zeros(frame_resized.shape[:2], dtype=np.uint8)
            roi_coords = np.array(self.roiArea.area).reshape(-1, 2)
            print("ROI Coordinates:", roi_coords)  # Print the coordinates for debugging
            maskcrop = cv2.fillPoly(mask, [roi_coords], 255)
            
            # Apply mask to the resized frame
            masked_frame = cv2.bitwise_and(frame_resized, frame_resized, mask=maskcrop)

            # Combine the original and masked frames for visualization
            combined_frame = cv2.addWeighted(frame_resized, 0.7, cv2.cvtColor(maskcrop, cv2.COLOR_GRAY2BGR), 0.3, 0)

            # Run the model on the masked frame
            results = self.model(frame_resized)

            # Analyze results
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls)
                    confidence = box.conf
                    if confidence > self.CONFID:
                        xyxy = box.xyxy[0].cpu().numpy()  # Extraer el tensor y convertir a numpy array
                        startX, startY, endX, endY = map(int, xyxy)

                        label = self.classNames.get(class_id, 'Unknown')

                        # Draw bounding box
                        cv2.rectangle(frame_resized, (startX, startY), (endX, endY), (0, 255, 0), 2)
                        cv2.putText(frame_resized, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Calculate time and difference
                        current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                        current_time = datetime.timedelta(milliseconds=current_time)
                        time_difference = (current_time - prev_time) if prev_time else datetime.timedelta(seconds=0)
                        prev_time = current_time

                        # Save to list
                        self.aparicion.append(self.format_timedelta(current_time))
                        self.tipoObj.append(label)
                        self.difTiempo.append(self.format_timedelta(time_difference))

                        # Skip frames for a short period to avoid multiple detections of the same object
                        self.frame_skip_counter = self.skip_frames

            # Display frames for debugging (optional)
            cv2.imshow("Masked Frame", frame_resized)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Populate dataframe
        self.df["Tiempo de aparición"] = self.aparicion
        self.df["Tipo de objeto"] = self.tipoObj
        self.df["Diferencia de tiempo"] = self.difTiempo

        # Save results to CSV
        self.df.to_csv(os.path.sep.join(["src/Cinta", self.nameVideo +".csv"]), index=False)
        self.cap.release()
        cv2.destroyAllWindows()
        return self.df
