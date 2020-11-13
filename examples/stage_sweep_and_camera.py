import os
import sys

from code.camera_tests import save_data, load_data

# sys.path.append(r"C:\Users\IR-Computer\NOISE_data\Common\motion_controller_camera")

# from record_and_sweep import aquire_sweep, plot_data
# from tools import ensure_no_overwrite
from code.record_and_sweep import aquire_sweep, plot_data
from code.tools import ensure_no_overwrite

import numpy as np
if __name__=='__main__':
    # make sure that folder has been created
    pathname = "data"
    filename = os.path.join(pathname, 'test.pickle')

    # make sure that the selected file hasn't already been created
    ensure_no_overwrite(filename)

    # make sure that I can write to the file
    save_data(None, filename)

    # run the sweep
    relative_positions = np.linspace(-3, 3, 3);
    xr_data = aquire_sweep(exposure_time_s=0.050, gain_dB=0., current_position=9, relative_positions=relative_positions)
    save_data(xr_data, filename)

    # # reload the file
    # xr_data = load_data(filename)

    plot_data(xr_data, pathname)
