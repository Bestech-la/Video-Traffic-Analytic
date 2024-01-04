from datetime import datetime, timedelta
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import VideoSerializer
from apps.video.models import Video
from apps.infraction_tracker.models import InfractionTracker
from rest_framework.parsers import MultiPartParser, FormParser
import cv2
import os
import numpy as np
from PIL import Image
import tempfile
from django.core.files import File
import re
import pytesseract
from datetime import datetime
import time 
import imutils

class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        video_file = self.request.data.get('video')
        yOne = self.request.data.get('yOne')
        yTwo = self.request.data.get('yTwo')
        date_time = self.request.data.get('date_time')
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

        if video_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            created_video = serializer.save()
            video_id = created_video.id

            car_cascade = cv2.CascadeClassifier('model/haarcascade_cars.xml')
            height = 720
            width = 1280

            min_width = 900
            min_height = 300

            cap = cv2.VideoCapture(temp_video_path)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')

            captured_car_plates = set()

            yOne = int(yOne)
            yTwo = int(yTwo)
            red_line_y = yTwo
            green_line_y = yOne

            start_time = None

            while True:
                ret, frame = cap.read()

                if not ret:
                    break
                
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                if start_time is None:
                    start_time = current_time
                    
                timestamp = date_time + timedelta(seconds=current_time)

                cv2.line(frame, (0, red_line_y), (frame.shape[1], red_line_y), (0, 0, 255), 2)
                cv2.line(frame, (0, green_line_y), (frame.shape[1], green_line_y), (0, 255, 0), 2)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in cars:
                    if y + h > red_line_y:
                        car_id = f'{x}-{y}-{w}-{h}'
                        if car_id not in captured_car_plates:
                            text_part = ""
                            number_part = ""
                            hsv_roi = frame[y:y + h, x:x + w]

                            if y < green_line_y:
                                continue  # Skip capturing if it's crossing a green light

                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3:, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            image = cv2.imread(img_path_car)
                            roi_height = image.shape[0] // 5
                            roi = image[0:roi_height, :]

                            hsv_roi_car_color = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                            hist_hue = cv2.calcHist([hsv_roi_car_color], [0], None, [180], [0, 180])

                            dominant_hue = np.argmax(hist_hue)
                            dominant_color = None

                            if 0 <= dominant_hue < 15 or 160 <= dominant_hue <= 180:
                                dominant_color = "ສີແດງ"
                            elif 15 <= dominant_hue < 35:
                                dominant_color = "ສີເຫຼືອງ"
                            elif 35 <= dominant_hue < 85:
                                dominant_color = "ສີຂຽວ"
                            elif 85 <= dominant_hue < 110:
                                dominant_color = "ສີຟ້າ"
                            elif 110 <= dominant_hue < 125:
                                dominant_color = "ສີດໍາ"
                            elif 125 <= dominant_hue < 150:
                                dominant_color = "ສີເທົາ"
                            elif 150 <= dominant_hue < 180:
                                dominant_color = "ສີຂາວ"

                            hsv_car_plate = cv2.cvtColor(hsv_roi, cv2.COLOR_BGR2HSV)
                            lower_yellow = np.array([20, 100, 100])
                            upper_yellow = np.array([30, 255, 255])
                            
                            

                            # Blue Car Plate Detection
                            lower_blue = np.array([100, 100, 100])
                            upper_blue = np.array([140, 255, 255])
                            output_cropped_path_blue = f'captured_images/blue_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                            detect_and_crop_car_plate(img_path_cars, output_cropped_path_blue, lower_blue, upper_blue, 'blue')

                            # Red Car Plate Detection
                            lower_red = np.array([0, 100, 100])
                            upper_red = np.array([10, 255, 255])
                            output_cropped_path_red = f'captured_images/red_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                            detect_and_crop_car_plate(img_path_cars, output_cropped_path_red, lower_red, upper_red, 'red')
                            
                            lower_yellow = np.array([20, 100, 100])
                            upper_yellow = np.array([30, 255, 255])
                            output_cropped_path_yellow = f'captured_images/yellow_1_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                            detect_and_crop_car_plate(img_path_cars, output_cropped_path_yellow, lower_yellow, upper_yellow, 'yellow')

                            yellow_mask = cv2.inRange(hsv_car_plate, lower_yellow, upper_yellow)
                            contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            if contours:
                                max_yellow_area = max(contours, key=cv2.contourArea)
                                x, y, w, h = cv2.boundingRect(max_yellow_area)

                                yellow_car_plate = hsv_roi[y:y + h, x:x + w]

                                if yellow_car_plate.shape[1] < min_width or yellow_car_plate.shape[0] < min_height:
                                    aspect_ratio = yellow_car_plate.shape[1] / yellow_car_plate.shape[0]
                                    new_width = min(min_width, int(min_height * aspect_ratio))
                                    new_height = min(min_height, int(min_width / aspect_ratio))
                                    yellow_car_plate = cv2.resize(yellow_car_plate, (new_width, new_height))

                                img_path = f'captured_images/yellow_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path, yellow_car_plate)

                                image_plate = cv2.imread(img_path)
                                roi_height = image_plate.shape[0] // 5
                                roi = image_plate[0:roi_height, :]

                                hsv_roi_plates_color = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                                hist_hue_plate = cv2.calcHist([hsv_roi_plates_color], [0], None, [180], [0, 180])

                                dominant_hue_plate = np.argmax(hist_hue_plate)
                                dominant_plate_color = None

                                if 0 <= dominant_hue_plate < 15 or 160 <= dominant_hue_plate <= 180:
                                    dominant_plate_color = "ສີແດງ"
                                elif 15 <= dominant_hue_plate < 35:
                                    dominant_plate_color = "ສີເຫຼືອງ"
                                elif 35 <= dominant_hue_plate < 85:
                                    dominant_plate_color = "ສີຂຽວ"
                                elif 85 <= dominant_hue_plate < 110:
                                    dominant_plate_color = "ສີຟ້າ"
                                elif 110 <= dominant_hue_plate < 125:
                                    dominant_plate_color = "ສີດໍາ"
                                elif 125 <= dominant_hue_plate < 150:
                                    dominant_plate_color = "ສີເທົາ"
                                elif 150 <= dominant_hue_plate < 180:
                                    dominant_plate_color = "ສີຂາວ"

                                image = Image.open(img_path)
                                dpi = (300, 300)
                                image.info['dpi'] = dpi
                                image.save(img_path, dpi=dpi)
                                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                car_info = pytesseract.image_to_string(yellow_car_plate, config=custom_config, lang='lao')
                                match = re.match(r'([ກ-ໝ]{2})(\d{4})', car_info)
                                if match:
                                    text_part = match.group(1)
                                    number_part = match.group(2)
                                    if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                        car_plate = f'{text_part} {number_part}'
                                        if car_plate not in captured_car_plates:
                                            captured_car_plates.add(car_plate)
                                            with open(img_path, 'rb') as img_file:
                                                image_file = File(img_file)
                                                report = InfractionTracker.objects.create(
                                                    vehicle_registration_number=car_plate,
                                                    vehicle_color=dominant_color,
                                                    vehicle_registration_color=dominant_plate_color,
                                                    video=created_video,
                                                    date_time=timestamp,
                                                )
                                                report.image_one.save(os.path.basename(img_path), image_file)
                                                img_file.close()

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)

            cap.release()

class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer
    
def detect_and_crop_car_plate(image_path, output_path, color_lower, color_upper, color_name, min_width=900, min_height=300):
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Error: Unable to read image at path {image_path}")
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv, color_lower, color_upper)
        
        cv2.imwrite(resized_plate_path, resized_plate_path_contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
                
        if contours:
            max_contour = contours[0]
            (x, y, w, h) = cv2.boundingRect(max_contour)
            plate = img[y:y + h, x:x + w]
            black_mask = cv2.inRange(plate, (0, 0, 0), (1, 1, 1))
            plate[black_mask == 255] = [255, 255, 255]
            cv2.imwrite(output_path, plate)
            
            if plate.shape[1] < min_width or plate.shape[0] < min_height:
                aspect_ratio = plate.shape[1] / plate.shape[0]
                new_width = min(min_width, int(min_height * aspect_ratio))
                new_height = min(min_height, int(min_width / aspect_ratio))
                plate = cv2.resize(plate, (new_width, new_height))
                
            # Resize the plate
            resized_plate_path = f'captured_images/resized_{color_name.lower()}_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
            resize_and_save(output_path, resized_plate_path, min_width, min_height)

            # Save the resized plate
            cv2.imwrite(resized_plate_path, plate)
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
            car_info = pytesseract.image_to_string(resized_plate_path, config=custom_config, lang='lao')
            print(f"Detected {color_name} car plate number is:", car_info)
        else:
            print(f"{color_name.capitalize()} car plate not detected.")
    except Exception as e:
        print(f"Error: {e}")
        return
    
def resize_and_save(image_path, output_path, min_width, min_height):
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Unable to read image at path {image_path}")
            return None
        resized_img = cv2.resize(img, (min_width, min_height))
        cv2.imwrite(output_path, resized_img)
        return output_path
    except Exception as e:
        print(f"Error during image resizing: {e}")
        return None

