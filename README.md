<!--- CPS
Author: <NAME>  Date: <JJJJ MMM DD> 
Changes by:
<NAME> - <JJJJ MMM DD> - <comment> 

--->
**Cyber Physical Systems**   <img style="float:right" src="./files/HM_SchriftzugLogo_RGB.png" width="200">  
Fakultät 04 
***

# Modularbeit: AI on the edge
## Autor: Sebastian Veigl

***

## Objectives

- Use an esp32cam as AI on the edge device detecting digits on an 7-segment display
- Utilizing the [AI-on-the-edge-device](https://github.com/jomjol/AI-on-the-edge-device) github-repository by [jomjol](https://github.com/jomjol)
- Training the used neural net for the special use case of the 7-segment display

## Prerequisites and required equipment

### For AI on the edge device using the 7-segment display:
- esp32cam
  - min. 4 MB of PSRAM (see [Hardware Compatibility](https://jomjol.github.io/AI-on-the-edge-device-docs/Hardware-Compatibility/) for known-working models)
  - OV2640 camera module
- micro SD-Card (preferable max. 16-32 GB)
- 5V voltage supply ([USB-breakout board](https://www.reichelt.de/entwicklerboards-breakout-board-mit-microusb-debo-microusb-p235502.html?PROVID=2788&gclid=CjwKCAiAp5qsBhAPEiwAP0qeJlUKYR2Ky4i1cNpVwsTMjPRNG9YKlgDQA9UiotmsCMJM1c-haZ3J7hoC8_EQAvD_BwE))
- 3.3V USB-TTL connector (e.g. https://www.amazon.de/DSD-TECH-Seriell-Adapter-Kompatibel/dp/B07BBPX8B8)
- TM1637 7-segment display
- (3D-printed) Holder for keeping the esp32cam in place over the display

### For training:
- Raspberry Pi 
  - Python 3.9 interpreter
- "Powerful" machine for training of the neural network

## Solutions Steps

### Installation and setup of AI-on-the-edge-device on the esp32cam

1. **Flashing the firmware**  
Connect the esp32cam-board with the USB-TTL connector as shown in the wiring diagram.  
<img src="./files/ESP32CAM_flash_Steckplatine.svg" width="600">  
Before flashing the firmware to the esp32cam, we have to bring the module into flash mode. Therefore, pin *IO0* has to be pulled low by connecting the pin with *GND*.
Then the *RST* button has to be pressed.  
There are multiple ways of flashing the firmware described in the [installation documentation](https://jomjol.github.io/AI-on-the-edge-device-docs/Installation/), we will be using the provided [Web Installer](https://jomjol.github.io/AI-on-the-edge-device/).
Enter the installer with your esp32cam connected to the computer using the USB-TTL connector **(make sure to use a 3.3V connector for the ESP32!)**. Select the corresponding COM-Port and start the installation of the current firmware version (this could take a few minutes).  
After getting the message of successful installation, you have to disconnect the bridge from *IO0* to *GND*.
2. **Setting up the SD-card**  
Before booting the esp32cam for the first time, we have to set up the SD-card expected by the firmware. First, format the SD-card in FAT32 format (see [Notes on the SD card](https://jomjol.github.io/AI-on-the-edge-device-docs/Installation/#manual-setup-with-an-sd-card-reader-on-a-pc)).  
Download the current SD-card content form the [release page](https://github.com/jomjol/AI-on-the-edge-device/releases). There you have to download the *AI-on-the-edge-device__manual-setup__vXX.X.X.zip* file and copy the contents of the extracted *sd-card* sub-folder to your microSD-card.
The content should look like this:  
<img src="./files/sd-card-content.png" width=150>  
With editing the included *wlan.ini* file, we can set up the WI-FI connection. Insert the SSID and password into the file. The hostname and other connection parameters can also be changed inside this file.  
When everything is set up you can insert the SD-card into the esp32cam.
3. **5V voltage supply**  
Connect to a 5V supply while unplugging the voltage supply of the USB-TTL connector as shown in the wiring diagram. The remaining connection to the USB-TTL connector is optional and can be used for debugging via a serial monitor.  
<img src="./files/ESP32CAM_run_Steckplatine.svg" width=750>
4. **Configuration using the Web-UI**  
Enter the Web-UI using the IP address given to your esp32cam. If everything was successful, you should be welcomed with the configuration page.  
The first step is to take a reference picture. This will be the basis for the coordinate system of the ROIs (Regions of Interest) later on.  
With this being the first time to see a picture taken by the esp32cam, we can **adjust the focus** of the camera module. Therefore, you have to remove the glue used for fixing the focus ring into place and turn the ring with a pair of pliers in order to set the focal length.  
<img src="./files/focus_adjustment.jpg" width=300>  
With the focus being set, you can proceed with the configuration. After taking the **reference image** and aligning it horizontally, you can define two **alignment references**.
These will be used to check and adjust the alignment. It is recommended to use unique structures with good contrast.  
The most important part during configuration is to set up the ROIs. These will later be used for the digit classification. As we are using a 7-segment display, only digit ROIs have to be set up. I was using the display as temperature display, so only ROIs where set up (up to 4 digits would be possible with this display).    
<img src="./files/ROI_setup.png" width=600>  
After everything is set up correctly, you have to reboot the esp32cam.  
For further information on how to configure the AI-on-the-edge-device firmware have a look at the [documentation](https://jomjol.github.io/AI-on-the-edge-device-docs/Reference-Image/).
5. **Selecting the trained neural model**  
After reboot you might be recognizing (assuming the display is already showing something) that the preconfigured neural network used for the classification of the digits is not working properly with the 7-segment display.  
Therefore, we will have to change the model by importing the *7seg1912.tflite* model that was already trained on over 1300 digits (see next chapter for instructions) into the file server running on the esp32cam (*System -> File Server -> Upload*).  
Now it will be an available option under *Settings -> Configuration -> Digit ROI Processing -> Model*.


### Auto-training on the 7-segment display using the Raspberry Pi

## Further Inputs
- The code used for getting the training data and training th neural net can be found under: <https://github.com/SebastianVeigl/AI_on_the_edge_segment_train>
- The SD-card content (incl. setting, etc.) used for my implementation can be found in the repository 

## Hints and pitfalls

### Installation  
- It might be necessary to supply the esp32cam with 5V during flashing the firmware, if you have problems during installation.
- You can check if the flash mode was entered successfully by checking the Logs on the [Web Installer](https://jomjol.github.io/AI-on-the-edge-device/). After pressing the *RST* button on the board, the log should show something like *"waiting for download"*.
- Status indication by blinking:
  - **fast, endless blinking:** Problem with the SD-card
  - **5 x fast blinking (< 1 second):** connection still pending 
  - **3 x slow blinking (1 second on/off):** WLAN connection established

### Set-up
- For setting up the focus of the camera you can use the included livestream function (<http://$CAM-IP$/stream>)
- I have disabled the alignment algorithm by setting the *Alignment Algorithm* option in the Configuration to *Off*. This resulted in faster computation (no alignment step) and was sufficiently accurate.

## Useful Resources for Own Searches

### Links

AI-on-the-edge docs: 
<https://jomjol.github.io/AI-on-the-edge-device-docs/>

Tensorflow Lite guide:
<https://www.tensorflow.org/lite/guide>

raspberrypi-tm1637:
<https://github.com/depklyon/raspberrypi-tm1637>
