import os
import sys
import time
import numpy as np


from lensrec.camera import Camera, Bitdepth
from lensrec.stage import Stage, position_to_displacement
from lensrec.tools import ensure_no_overwrite, save_as_16bit_tiff, make_dir

if __name__=='__main__':
    # connect to stage
    s1 = Stage() # remember to turn the motor on manually.

    # setup output path
    image_output_path = 'data'
    make_dir(image_output_path)

    # make sure that the selected file hasn't already been created
    ensure_no_overwrite(filename)

    relative_positions_mm = np.linspace(-1, 1, 3);
    stage_displacements_mm = position_to_displacement(relative_positions_mm)

    print("Started sweep at {}".fromat(time.now()))

    # Iterate over the displacement
    for i, (z, dz) in enumerate(zip(relative_positions_mm, stage_displacements_mm)):
        print("Started aquisition {}/{}".format(i + 1, len(relative_positions)))

        print("moving stage to {}mm".format(z))
        # move stage by dz
        s1.move_relative(-dz)
        time.sleep(0.5) # wait for stage to settle
        print("moved stage to {}mm".format(-s1.get_position()))

        # take picture...
        cam_image = Camera.take_picture(
            gain_dB=0,
            exposure_time_s=0.1,
            props=props,
            bitdepth=Bitdepth.TWELVE,
        )

        # ...and save it
        save_as_16bit_tiff(data=cam_image, filename=out_file)

    print("Completed sweep")
