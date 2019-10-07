import sys
sys.path.append(r"C:\Users\IR-Computer\NOISE_data\Common\motion_controller_camera\code")
from tools import get_image_files, mkdir_no_overwrite, save_as_16bit_tiff
import os
from display import Display
import cv2
from camera import Camera, Bitdepth

def aquire_slidshow(pathname_out, number=-1):
    images = get_image_files("./images/")
    mkdir_no_overwrite(pathname_out)


    gain_dB = 0
    exposure_time_s = 30

    disp = Display()

    if number < 0:
        number = len(images)

    for image_file in images[0:number]:
        disp_image = cv2.imread(image_file)
        #disp_image = cv2.cvtColor(disp_image, cv2.COLOR_BGR2RGB)
        disp.start_display(disp_image, scale=1)
        out_file = os.path.join(pathname_out, os.path.basename(image_file))
        out_file = os.path.splitext(out_file)[0]

        props = {'display image': disp_image, 'output file': out_file}
        cam_image = Camera.take_picture(
            gain_dB=gain_dB,
            exposure_time_s=exposure_time_s,
            props=props,
            bitdepth=Bitdepth.TWELVE)

        save_as_16bit_tiff(data=cam_image, filename=out_file)

    disp.close()

if __name__=="__main__":
    aquire_slidshow(pathname_out="30s_0dB", number=-1)
