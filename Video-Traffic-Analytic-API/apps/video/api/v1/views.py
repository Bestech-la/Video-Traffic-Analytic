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


class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        video_file = self.request.data.get('video')
        yOne = self.request.data.get('yOne')
        yTwo = self.request.data.get('yTwo')
        if video_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            # Save the video to the database first
            created_video = serializer.save()

            # Get the ID of the created video
            video_id = created_video.id

            car_cascade = cv2.CascadeClassifier('model/haarcascade_eye.xml')
            height = 720
            width = 1280

            min_width = 900
            min_height = 300

            # Initialize video capture using the temporary video path
            cap = cv2.VideoCapture(temp_video_path)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

            # Create a directory to store captured images
            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')

            # Create a set to track captured car plates
            captured_car_plates = set()

            # Define the y-coordinate of the red and green lines
            yOne = int(yOne)
            yTwo = int(yTwo)
            red_line_y = yTwo
            green_line_y = yOne
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Draw the red line at y=500 and the green line at y=300
                cv2.line(frame, (0, (red_line_y)),
                         (frame.shape[1], red_line_y), (0, 0, 255), 2)
                cv2.line(frame, (0, green_line_y),
                         (frame.shape[1], green_line_y), (0, 255, 0), 2)

                # Convert the frame to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect cars in the frame
                cars = car_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in cars:
                    # Check if the car crosses the red line (y+height > red_line_y)
                    if y + h > red_line_y:
                        # Check if the car has not been captured yet
                        car_id = f'{x}-{y}-{w}-{h}'
                        if car_id not in captured_car_plates:
                            # Crop the region of interest around the car
                            text_part = ""
                            number_part = ""
                            hsv_roi = frame[y:y + h, x:x + w]

                            # Check if the car is crossing a green light (y < green_line_y)
                            if y < green_line_y:
                                continue  # Skip capturing if it's crossing a green light

                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3:, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            # Add the color detection code here
                            image = cv2.imread(img_path_car)
                            roi_height = image.shape[0] // 5
                            roi = image[0:roi_height, :]

                            hsv_roi_car_color = cv2.cvtColor(
                                roi, cv2.COLOR_BGR2HSV)

                            hist_hue = cv2.calcHist([hsv_roi_car_color], [
                                                    0], None, [180], [0, 180])

                            dominant_hue = np.argmax(hist_hue)
                            dominant_color = None

                            # Determine the color based on the dominant hue
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

                            print(
                                f'Dominant Color in the Car: {dominant_color}')

                            hsv_car_plate = cv2.cvtColor(
                                hsv_roi, cv2.COLOR_BGR2HSV)
                            # Define the lower and upper bounds of the yellow color range
                            lower_yellow = np.array([20, 100, 100])
                            upper_yellow = np.array([30, 255, 255])

                            yellow_mask = cv2.inRange(
                                hsv_car_plate, lower_yellow, upper_yellow)

                            # Find contours in the yellow mask
                            contours, _ = cv2.findContours(
                                yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                            if contours:
                                # Find the largest yellow region (assumed to be the car plate)
                                max_yellow_area = max(
                                    contours, key=cv2.contourArea)
                                x, y, w, h = cv2.boundingRect(max_yellow_area)

                                # Crop and save only the yellow car plate
                                yellow_car_plate = hsv_roi[y:y + h, x:x + w]

                                if yellow_car_plate.shape[1] < min_width or yellow_car_plate.shape[0] < min_height:
                                    aspect_ratio = yellow_car_plate.shape[1] / \
                                        yellow_car_plate.shape[0]
                                    new_width = min(min_width, int(
                                        min_height * aspect_ratio))
                                    new_height = min(min_height, int(
                                        min_width / aspect_ratio))
                                    yellow_car_plate = cv2.resize(
                                        yellow_car_plate, (new_width, new_height))

                                img_path = f'captured_images/yellow_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                cv2.imwrite(img_path, yellow_car_plate)
                                # Add the color detection code here
                                image_plate = cv2.imread(img_path)
                                roi_height = image_plate.shape[0] // 5
                                roi = image_plate[0:roi_height, :]

                                hsv_roi_plates_color = cv2.cvtColor(
                                    roi, cv2.COLOR_BGR2HSV)

                                hist_hue_plate = cv2.calcHist([hsv_roi_plates_color], [
                                    0], None, [180], [0, 180])

                                dominant_hue_plate = np.argmax(hist_hue_plate)
                                dominant_plate_color = None

                                # Determine the color based on the dominant hue
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

                                print(
                                    f'Dominant Color in the plate: {dominant_plate_color}')

                                image = Image.open(img_path)
                                dpi = (300, 300)
                                image.info['dpi'] = dpi
                                image.save(img_path, dpi=dpi)
                                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZຂກຄງຈຊຍດຕຖທນບປຜຝພຟມຢຣລວສຫຬອຮຯະັາຳີຶືຸູົຼຽ'  # Lao characters
                                car_info = pytesseract.image_to_string(
                                    yellow_car_plate, config=custom_config, lang='lao')
                                match = re.match(
                                    r'([ກ-ໝ]{2})(\d{4})', car_info)
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
                                                    video=created_video)
                                                report.image_one.save(
                                                    os.path.basename(img_path), image_file)
                                                img_file.close()
                                                os.remove(img_path)
                                                print(
                                                    "Report saved with ID:", report.id)

                                            with open(img_path_car, 'rb') as img_file_car:
                                                image_file_car = File(
                                                    img_file_car)
                                                report.image_two.save(os.path.basename(
                                                    img_path_car), image_file_car)
                                                img_file_car.close()
                                                os.remove(img_path_car)
                                                print(
                                                    "Car image saved for report with ID:", report.id)
                                        else:
                                            print(
                                                "Image not saved (already captured):", img_path)
                                    else:
                                        print(
                                            "Car information format is invalid:", car_info)
                                else:
                                    print(
                                        "Car information format does not match:", car_info)

            cap.release()


class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer
