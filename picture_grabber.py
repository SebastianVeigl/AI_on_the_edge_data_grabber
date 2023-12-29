import datetime
import io
import os.path
import random
import re
import sys
from dataclasses import dataclass
from time import sleep
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import requests
import tm1637
from PIL import Image
from matplotlib import patches


@dataclass
class ROI:
    dig_num: int
    x: int
    y: int
    width: int
    height: int


class PictureGrabber:
    def __init__(self, esp_ip, display_clk, display_dio):
        self.esp_ip = esp_ip
        self.display = tm1637.TM1637(display_clk, display_dio)

        self.roi_bounds = self.get_config()

        for i in range(10):
            if not os.path.exists(f'digits/{i}'):
                os.mkdir(f'digits/{i}')

    def start_gathering(self, sleep_time: float, n: Optional[int]):
        while not self.check_finished():
            sleep(1)
            print('A flow is already running, waiting for it to finish, before continuing...')

        if n is None:
            while True:
                self.gather_data()
                sleep(sleep_time)

        for _ in range(n):
            self.gather_data()
            sleep(sleep_time)

    def gather_data(self):
        number = random.Random().randint(0, 99)
        self.display.temperature(number)
        print(f'Displaying: {number}')

        digits = list(reversed([number // 10, number % 10]))

        image = self.get_image()
        # self.show_boxes(image)

        sleep(3)
        detected_number = requests.get(f'http://{self.esp_ip}/json').json()
        detected_number = detected_number['main']['value']
        print(f'Detected: {detected_number}')
        if int(detected_number) != int(number):
            print(f'Uncorrect detection {number} vs. {detected_number}')

        for roi in self.roi_bounds:
            digit_value = digits[roi.dig_num - 1]

            image_cutout = image[roi.y:roi.y + roi.height, roi.x:roi.x + roi.width]

            plt.imsave(
                f'digits/{digit_value}/{digit_value}_{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.jpeg',
                image_cutout)

    def show_boxes(self, image: np.ndarray):
        # Create figure and axes
        fig, ax = plt.subplots()

        # Display the image
        ax.imshow(image)

        # Create a Rectangle patch
        roi1 = self.roi_bounds[0]
        rect1 = patches.Rectangle((roi1.x, roi1.y), roi1.width,
                                  roi1.height, linewidth=1, edgecolor='b', facecolor='none')
        roi2 = self.roi_bounds[1]
        rect2 = patches.Rectangle((roi2.x, roi2.y), roi2.width,
                                  roi2.height, linewidth=1, edgecolor='r', facecolor='none')

        # Add the patch to the Axes
        ax.add_patch(rect1)
        ax.add_patch(rect2)

        plt.show()

    def get_config(self) -> List[ROI]:
        req = requests.get(f'http://{self.esp_ip}/fileserver/config/config.ini')
        config_str = str(req.content, req.encoding)

        config_str = config_str.split('\n')
        roi_config = {re.findall(r'dig(\d+)', s)[0]: s for s in config_str if re.findall(r'dig\d+', s)}

        rois = []
        for dig_n, dig_conf in roi_config.items():
            roi_data = dig_conf.split(' ')

            rois.append(ROI(dig_num=int(dig_n),
                            x=int(roi_data[1]),
                            y=int(roi_data[2]),
                            width=int(roi_data[3]),
                            height=int(roi_data[4])))

        return rois

    def check_finished(self, status_set: Optional[set] = None) -> bool:
        req = requests.get(f'http://{self.esp_ip}/statusflow')
        resp = str(req.content, req.encoding)
        if status_set is not None:
            status_set.add(resp)
        return 'FINISHED' in resp.upper()

    def get_image(self) -> np.ndarray:
        while not self.check_finished():
            print('Flow already running, waiting for finish')
            sleep(1)

        requests.get(f'http://{self.esp_ip}/flow_start')
        sleep(1)

        status_set = set()

        while not self.check_finished(status_set):
            sleep(0.1)

        print(status_set)

        image_bytes = requests.get(f'http://{self.esp_ip}/img_tmp/alg.jpg').content

        img = Image.open(io.BytesIO(image_bytes))
        image = np.array(img)

        return image


if __name__ == '__main__':
    if len(sys.argv) < 2:
        ip = '192.168.137.110'
    else:
        ip = sys.argv[1]

    picture_grabber = PictureGrabber(ip, 5, 4)
    picture_grabber.start_gathering(0, None)
