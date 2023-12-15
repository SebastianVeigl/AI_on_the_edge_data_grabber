import datetime
import io
import os.path
import random
import re
from dataclasses import dataclass
from typing import List

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

        while True:
            self.gather_data()

    def gather_data(self):
        number = random.Random().randint(0, 99)
        self.display.temperature(number)
        print(f'Displaying: {number}')

        digits = [number // 10, number % 10]

        image = self.get_image(light=False)

        for roi in self.roi_bounds:
            digit_value = digits[roi.dig_num - 1]

            image_cutout = image[roi.y:roi.y + roi.height, roi.x:roi.x + roi.width]  # TODO check if boxes are right

            plt.imsave(f'digits/{digit_value}/{digit_value}_{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.jpeg', image_cutout)

            # plt.imshow(image_cutout)
            # plt.show()

    def show_boxes(self, image: np.ndarray):
        # Create figure and axes
        fig, ax = plt.subplots()

        # Display the image
        ax.imshow(image)

        # Create a Rectangle patch
        roi1 = self.roi_bounds[0]
        rect1 = patches.Rectangle((roi1.x + roi1.width / 2, roi1.y + roi1.height / 2), roi1.width,
                                  roi1.height, linewidth=1, edgecolor='b', facecolor='none')
        roi2 = self.roi_bounds[1]
        rect2 = patches.Rectangle((roi2.x + roi2.width / 2, roi2.y + roi2.height / 2), roi2.width,
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

    def get_image(self, light: bool = False) -> np.ndarray:
        if light:
            image_bytes = requests.get(f'http://{self.esp_ip}/capture_with_flashlight').content
        else:
            image_bytes = requests.get(f'http://{self.esp_ip}/capture').content
        image = np.array(Image.open(io.BytesIO(image_bytes)))

        return image


if __name__ == '__main__':
    ip = '192.168.169.52'
    picture_grabber = PictureGrabber(ip, 5, 4)
