from lensrec.tools import get_image_files, mkdir_no_overwrite
import os
from ..display import Display
import cv2
from ..camera import Camera, Bitdepth

def aquire_slidshow(pathname_out, number=-1):
    images = get_image_files("./images/")
    mkdir_no_overwrite(pathname_out)

    gain_dB = 0
    exposure_time_s = 1

    disp = Display()

    if number < 0:
        number = len(images)

    for image_file in images[0:number-1]:
        disp_image = cv2.imread(image_file)
        disp_image = cv2.cvtColor(disp_image, cv2.COLOR_BGR2RGB)
        disp.start_display(disp_image)
        out_file = os.path.join(pathname_out, os.path.basename(image_file))

        props = {'display image': disp_image, 'output file': out_file}
        cam_image = Camera.take_picture(
            gain_dB=gain_dB,
            exposure_time_s=exposure_time_s,
            props=props,
            bitdepth=Bitdepth.EIGHT)

        # save_single_for_ndarray(data=cam_image, file=out_file)

    disp.close()

if __name__=="__main__":
    aquire_slidshow(pathname_out="test", number=5)