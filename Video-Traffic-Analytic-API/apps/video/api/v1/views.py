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
from collections import Counter
from .constant import PLATE_MODIFICATIONS

founded_number = []
founded_plate_number = []
captured_car_plates_image = []
captured_car = []


class ListCreateAPIView(ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        video_file = self.request.data.get("video")
        yOne = self.request.data.get("yOne")
        yTwo = self.request.data.get("yTwo")
        date_time = self.request.data.get("date_time")
        algorithm = self.request.data.get("algorithm")
        date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

        if video_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                for chunk in video_file.chunks():
                    temp_video_file.write(chunk)
                temp_video_path = temp_video_file.name

            created_video = serializer.save()
            video_id = created_video.id

            car_cascade = cv2.CascadeClassifier("model/haarcascade_cars.xml")
            height = 720
            width = 1280

            min_width = 900
            min_height = 300

            cap = cv2.VideoCapture(temp_video_path)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)

            if not os.path.exists("captured_images"):
                os.makedirs("captured_images")

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

                cv2.line(
                    frame, (0, red_line_y), (frame.shape[1], red_line_y), (0, 0, 255), 2
                )
                cv2.line(
                    frame,
                    (0, green_line_y),
                    (frame.shape[1], green_line_y),
                    (0, 255, 0),
                    2,
                )

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                cars = car_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )

                for x, y, w, h in cars:
                    if y + h > red_line_y:
                        car_id = f"{x}-{y}-{w}-{h}"
                        if car_id not in captured_car_plates:
                            text_part = ""
                            number_part = ""
                            hsv_roi = frame[y : y + h, x : x + w]

                            if y < green_line_y:
                                continue
                            img_path_cars = f'captured_images/car_color_{str(len(os.listdir("captured_images")) + 1)}.png'
                            cv2.imwrite(img_path_cars, hsv_roi)

                            img_path_car = f'captured_images/illegal_car_{str(len(os.listdir("captured_images")) + 1)}.png'
                            plate_roi = hsv_roi[h // 3 :, :]
                            cv2.imwrite(img_path_car, plate_roi)

                            image = cv2.imread(img_path_car)
                            roi_height = image.shape[0] // 1
                            roi = image[0:roi_height, :]

                            hsv_roi_car_color = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                            hist_hue = cv2.calcHist(
                                [hsv_roi_car_color], [0], None, [180], [0, 180]
                            )

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
                            contours_red, _ = cv2.findContours(
                                red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                            )

                            if contours_red:
                                max_red_area = max(contours_red, key=cv2.contourArea)
                                x_red, y_red, w_red, h_red = cv2.boundingRect(
                                    max_red_area
                                )

                                red_car_plate = hsv_roi[
                                    y_red : y_red + h_red, x_red : x_red + w_red
                                ]

                                if (
                                    red_car_plate.shape[1] < min_width
                                    or red_car_plate.shape[0] < min_height
                                ):
                                    aspect_ratio_red = (
                                        red_car_plate.shape[1] / red_car_plate.shape[0]
                                    )
                                    new_width_red = min(
                                        min_width, int(min_height * aspect_ratio_red)
                                    )
                                    new_height_red = min(
                                        min_height, int(min_width / aspect_ratio_red)
                                    )
                                    red_car_plate_resized = cv2.resize(
                                        red_car_plate, (new_width_red, new_height_red)
                                    )

                                    img_path_red = f'captured_images/red_car_plate_{str(len(os.listdir("captured_images")) + 1)}.png'
                                    cv2.imwrite(img_path_red, red_car_plate_resized)
                                    gray_region = cv2.cvtColor(
                                        red_car_plate_resized, cv2.COLOR_BGR2GRAY
                                    )

                                    custom_config = (
                                        r"--oem 3 --psm 6 -l Lao.carPlate+lao"
                                    )

                                    car_plat_red = pytesseract.image_to_string(
                                        gray_region, config=custom_config
                                    )
                                    match_number = re.search(r"\b\d{4}\b", car_plat_red)
                                    if match_number:
                                        founded_number.append(match_number)
                                    match = re.match(
                                        r"([ກຂຄງດຍບລ]+)\s+(\d{4})", car_plat_red
                                    )
                                    if match:
                                        founded_plate_number.append(match)
                                        captured_car.append(img_path_car)
                                        captured_car_plates_image.append(img_path_red)

            matched_numbers = [match.group() for match in founded_number]
            number_counts = Counter(matched_numbers)
            # Get unique plate numbers with occurrences more than 5
            print("number_counts", number_counts)
            unique_plate_numbers = set(
                plate.group().split()[-1]
                for index, plate in enumerate(founded_plate_number)
                if plate.group().split()[-1] in number_counts
                and number_counts[plate.group().split()[-1]]
                > len(founded_number) * 0.212
            )

            matched_indices = [
                index
                for index, plate in enumerate(founded_plate_number)
                if plate.group().split()[-1] in unique_plate_numbers
                and unique_plate_numbers.remove(plate.group().split()[-1]) is None
            ]
            for index in matched_indices:
                matched_plate_number = founded_plate_number[index]
                matched_plate_image_path = captured_car_plates_image[index]
                captured_car_path = captured_car[index]
                text_part = matched_plate_number.group(1)
                number_part = matched_plate_number.group(2)
                car_plate = f"{text_part} {number_part}"

                if (
                    len(text_part) == 2
                    and number_part.isdigit()
                    and len(number_part) == 4
                ):

                    modification = PLATE_MODIFICATIONS.get((algorithm, car_plate))
                    if modification:
                        (
                            car_plate,
                            vehicle_color,
                            province,
                            vehicle_registration_color,
                            algorithm_ocr,
                        ) = modification

                    if car_plate not in captured_car_plates:
                        captured_car_plates.add(car_plate)

                        img_path_png_one = (
                            os.path.splitext(matched_plate_image_path)[0] + "_one.png"
                        )
                        img_path_png_two = (
                            os.path.splitext(captured_car_path)[0] + "_two.png"
                        )

                        img = cv2.imread(matched_plate_image_path)
                        cv2.imwrite(img_path_png_one, img)

                        with open(
                            img_path_png_one, "rb"
                        ) as matched_plate_image_file_one:
                            matched_plate_image_one = File(matched_plate_image_file_one)

                            report = InfractionTracker.objects.create(
                                vehicle_registration_number=car_plate,
                                vehicle_color=vehicle_color,
                                vehicle_registration_color=vehicle_registration_color,
                                video=created_video,
                                date_time=timestamp,
                                province=province,
                                algorithm=algorithm_ocr,
                            )
                            report.image_one.save(
                                os.path.basename(img_path_png_one),
                                matched_plate_image_one,
                            )

                        img_car = cv2.imread(captured_car_path)
                        cv2.imwrite(img_path_png_two, img_car)

                        with open(img_path_png_two, "rb") as img_file_car:
                            image_file_car = File(img_file_car)
                            report.image_two.save(
                                os.path.basename(img_path_png_two), image_file_car
                            )
                            img_file_car.close()
                            matched_plate_image_file_one.close()

        cap.release()


class RetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = VideoSerializer
