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
from PIL import Image
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

            yOne = int(100)
            yTwo = int(520)
            red_line_y = 471
            green_line_y = 100

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
                                continue 
                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3:, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            image = cv2.imread(img_path_car)
                            roi_height = image.shape[0] // 1
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
                                dominant_color = "ສີເທົາ"
                            elif 125 <= dominant_hue < 150:
                                dominant_color = "ສີດໍາ"
                            elif 150 <= dominant_hue < 180:
                                dominant_color = "ສີຂາວ"                            
                            

                            hsv_car_plate = cv2.cvtColor(hsv_roi, cv2.COLOR_BGR2HSV)
                                                 
                            lower_red = np.array([0, 100, 100])
                            upper_red = np.array([1000, 255, 255])
                            red_mask = cv2.inRange(hsv_car_plate, lower_red, upper_red)
                            contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                   
                            if contours_red:
                                max_red_area = max(contours_red, key=cv2.contourArea)
                                x_red, y_red, w_red, h_red = cv2.boundingRect(max_red_area)

                                red_car_plate = hsv_roi[y_red:y_red + h_red, x_red:x_red + w_red]

                                if red_car_plate.shape[1] < min_width or red_car_plate.shape[0] < min_height:
                                    aspect_ratio_red = red_car_plate.shape[1] / red_car_plate.shape[0]
                                    new_width_red = min(min_width, int(min_height * aspect_ratio_red))
                                    new_height_red = min(min_height, int(min_width / aspect_ratio_red))
                                    red_car_plate_resized = cv2.resize(red_car_plate, (new_width_red, new_height_red))

                                    img_path_red = f'captured_images/red_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                    cv2.imwrite(img_path_red, red_car_plate_resized)
                                    gray_region = cv2.cvtColor(red_car_plate_resized, cv2.COLOR_BGR2GRAY)

                                    custom_config = r'--oem 3 --psm 6 -l lao'


                                    car_plat_red = pytesseract.image_to_string(gray_region, config=custom_config, lang='lao')
                                    print("car_plat_red:", match)
                                    
                                    match = re.match(r'([ກ-ຂກ-ໝ]{2})\s*(\d{4})(?:[\s|,|\\|/]+|,\s*)', car_plat_red)

                                    print("match:", match)
                                    
                                    if match:
                                        text_part = match.group(1)
                                        number_part = match.group(2)
                                        if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                            car_plate = f'{text_part} {number_part}'
                                            if car_plate not in captured_car_plates:
                                                captured_car_plates.add(car_plate)
                                                with open(img_path_red, 'rb') as img_file_red:
                                                    image_file_red = File(img_file_red)
                                                    report = InfractionTracker.objects.create(
                                                        vehicle_registration_number=car_plate,
                                                        vehicle_color=dominant_color,
                                                        vehicle_registration_color="ສີເຫຼືອງ",
                                                        video=created_video,
                                                        date_time=timestamp,
                                                        province="ກໍາແພງນະຄອນ",
                                                    )
                                                    report.image_one.save(os.path.basename(img_path_red), image_file_red)
                                                    img_file_red.close()

                                                with open(img_path_car, 'rb') as img_file_car:
                                                    image_file_car = File(img_file_car)
                                                    report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                    img_file_car.close()


                            lower_white = np.array([0, 0, 200])
                            upper_white = np.array([180, 50, 255])
                            white_mask = cv2.inRange(hsv_car_plate, lower_white, upper_white)
                            contours_white, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            if contours_white:
                                max_white_area = max(contours_white, key=cv2.contourArea)
                                x_white, y_white, w_white, h_white = cv2.boundingRect(max_white_area)
                                white_car_plate = hsv_roi[y_white:y_white + h_white, x_white:x_white + w_white]
                                if white_car_plate.shape[1] < min_width or white_car_plate.shape[0] < min_height:
                                    aspect_ratio_white = white_car_plate.shape[1] / white_car_plate.shape[0]
                                    new_width_white = min(min_width, int(min_height * aspect_ratio_white))
                                    new_height_white = min(min_height, int(min_width / aspect_ratio_white))
                                    white_car_plate_resized = cv2.resize(white_car_plate, (new_width_white, new_height_white))

                                    img_path_white = f'captured_images/white_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                    cv2.imwrite(img_path_white, white_car_plate_resized)
                                    
                                    gray_white_plate = cv2.cvtColor(white_car_plate_resized, cv2.COLOR_BGR2GRAY)
                                    # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                    # custom_config = r'--oem 3 --psm 6 -l lao'
                                    # Adjusted custom_config for Windows and Lao language
                                    custom_config = r'--oem 3 --psm 6 -l lao -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'

                                    car_plate_white = pytesseract.image_to_string(gray_white_plate, config=custom_config, lang='lao')
                                    match = re.match(r'([ກ-ໝ]{2})(\d{4})', car_plate_white)
                                    if match:
                                        text_part = match.group(1)
                                        number_part = match.group(2)
                                        if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                            car_plate = f'{text_part} {number_part}'
                                            if car_plate not in captured_car_plates:
                                                captured_car_plates.add(car_plate)
                                                with open(img_path_white, 'rb') as img_file_white:
                                                    image_file_white = File(img_file_white)
                                                    report = InfractionTracker.objects.create(
                                                        vehicle_registration_number=car_plate,
                                                        vehicle_color=dominant_color,
                                                        vehicle_registration_color="ສີຂາວ", 
                                                        video=created_video,
                                                        date_time=timestamp,
                                                    )
                                                    report.image_one.save(os.path.basename(img_path_white), image_file_white)
                                                    img_file_white.close()

                                                with open(img_path_car, 'rb') as img_file_car:
                                                    image_file_car = File(img_file_car)
                                                    report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                    img_file_car.close()


                            lower_blue = np.array([100, 150, 0])
                            upper_blue = np.array([140, 255, 255])
                            blue_mask = cv2.inRange(hsv_car_plate, lower_blue, upper_blue)
                            contours_blue, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                                            
                            if contours_blue:
                                max_blue_area = max(contours_blue, key=cv2.contourArea)
                                x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(max_blue_area)

                                blue_car_plate = hsv_roi[y_blue:y_blue + h_blue, x_blue:x_blue + w_blue]

                                if blue_car_plate.shape[1] < min_width or blue_car_plate.shape[0] < min_height:
                                    aspect_ratio_blue = blue_car_plate.shape[1] / blue_car_plate.shape[0]
                                    new_width_blue = min(min_width, int(min_height * aspect_ratio_blue))
                                    new_height_blue = min(min_height, int(min_width / aspect_ratio_blue))
                                    blue_car_plate = cv2.resize(blue_car_plate, (new_width_blue, new_height_blue))

                                img_path_blue = f'captured_images/blue_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path_blue, blue_car_plate)

                                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                car_plat_blue = pytesseract.image_to_string(blue_car_plate, config=custom_config, lang='lao')
                                match = re.match(r'([ກ-ໝ]{2})(\d{4})', car_plat_blue)
                                if match:
                                    text_part = match.group(1)
                                    number_part = match.group(2)
                                    if len(text_part) == 2 and number_part.isdigit() and len(number_part) == 4:
                                        car_plate = f'{text_part} {number_part}'
                                        if car_plate not in captured_car_plates:
                                            captured_car_plates.add(car_plate)
                                            with open(img_path_blue, 'rb') as img_file_blue:
                                                image_file_blue = File(img_file_blue)
                                                report = InfractionTracker.objects.create(
                                                    vehicle_registration_number=car_plate,
                                                    vehicle_color=dominant_color,
                                                    vehicle_registration_color="ສີຟ້າ",
                                                    video=created_video,
                                                    date_time=timestamp,
                                                )
                                                report.image_one.save(os.path.basename(img_path_blue), image_file_blue)
                                                img_file_blue.close()

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(img_file_car)
                                                report.image_two.save(os.path.basename(img_path_car), image_file_car)
                                                img_file_car.close()

            cap.release()
class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer
    

import cv2
import pytesseract

def read_text(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Unable to load image file: {image_path}")

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('preprocessed_image.png', gray_image)
        # custom_config = r'--oem 3 --psm 6 -l lao -c tessedit_char_whitelist=0123456789ຂກຄຈຍດຕທນບຜພມລວສຫອຮ'
        # custom_config = r'--oem 3 --psm 6 -l lao '
        # custom_config = r'--oem 3 --psm 6 Lao.carPlate+la'
        custom_config = r'--oem 3 --psm 6 -l lao '
        
        car_plate_text = pytesseract.image_to_string(gray_image, config=custom_config, lang='lao')
        print("car_plate_text:", car_plate_text)
        
        return car_plate_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

input_image_path = 'apps/image_test/8840.png'
result = read_text(input_image_path)

if result is not None:
    print("Car Plate Text:", result)
else:
    print("Failed to extract text from the image.")
