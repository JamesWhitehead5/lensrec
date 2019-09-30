#!/bin/env/python3

from pymba import Vimba, VimbaException
from display_frame import display_frame
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
import xarray
import pickle
import os.path
from Stage import Stage
import sys

def take_a_picture(exposure_time_s, gain_dB):
    """
    Sweeps the linear stage while recording camera frames at each point
    """
    image = None

    #Connect to the Prosilica GT camera via a Power over Ethernet cable. Make
    #sure that the drivers are installed. This is tested the the Vimba 3.0 SDK.
    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        camera.feature('ExposureTimeAbs').value = int(exposure_time_s*1e6) #exposure time in us
        camera.feature('Gain').value = gain_dB #gain in dB
        camera.feature("BlackLevel").value = 0
        camera.arm('SingleFrame')
        
        try:
            t_start = time.time()
            print("Started capture of image")
            frame = camera.acquire_frame(timeout_ms=int(exposure_time_s*1000 + 1000))
            print("Finished capture of image. Took {} seconds".format(time.time()-t_start))
            image = np.array(frame.buffer_data_numpy())
        except VimbaException as e:
            # rearm camera upon frame timeout
            if e.error_code == VimbaException.ERR_TIMEOUT:
                print(e)
                camera.disarm()
                camera.arm('SingleFrame')
            else:
                raise

        
        #determine dimensions
        n_x = camera.feature('Width').value
        n_y = camera.feature('Height').value
        sensor_height = 5.86e-6*n_x #pixel sizes taken from manual
        sensor_width = 5.86e-6*n_y
        x_coords = np.linspace(-sensor_width/2., sensor_width/2., n_x)
        y_coords = np.linspace(-sensor_height/2., sensor_height/2., n_y)

        camera.disarm()
        camera.close()

       
    #process the data
    PIXEL_FORMATS_CONVERSIONS = {
        'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
    }  

    #demosaic the data
    try:
        image =cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[frame.pixel_format])
    except KeyError:
        pass

    #and rearrange the colors
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    colors = ['r', 'g', 'b']
    xr_data=xarray.DataArray(image, coords={'y': y_coords, 'x': x_coords, 'rgb': colors, 'time': exposure_time_s, 'gain': gain_dB}, dims=['y', 'x', 'rgb'])
    return xr_data

#https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


if __name__=='__main__':
    filename = './dose_sweep.pickle'
    aquire = True

    if aquire:
        #check if the file exists
        if (os.path.exists(filename)):
            overwrite = query_yes_no("Filename {} already exists. Do you want to overwrite?".format(filename))
            if overwrite:
                pass
            else:
                sys.exit(1)

        n_gain = 0
        n_exposure_time = 5


        gains = np.linspace(0, 40, n_gain)
        times = np.linspace(0.1, 75, n_exposure_time) #max time is 75-100
        

        images = [[take_a_picture(exposure_time, gain) for gain in gains] for exposure_time in times] 


        #images=xarray.DataArray(images, coords=[gains, times], dims=['gains', 'times'])
        rows = []
        for i in range(n_exposure_time):
            rows.append(xarray.concat(images[i], 'gain'))
        images = xarray.concat(rows, 'time')

        print("\nSaving the data to the hard drive. Filename: {}".format(filename))
        pickle.dump(images, open(filename, "wb" )) #save the data
        print("Finished saving!")

    
    #reload the file
    print("Loading files from the hard drive: Filename: {}".format(filename))
    images = pickle.load(open(filename, "rb" ))
    print("Finished loading!!!")

    #plot a frame at an index

    fig, axs = plt.subplots(len(images.gain), len(images.time))
    fig.suptitle('Title')

    for i, gain in enumerate(images.gain):
        for j, time in enumerate(images.time):
            #axs[i, j].imshow(images.isel(gains=i, time=j))
            images.isel(gain=i, time=j).plot.imshow(ax=axs[i, j])
            axs[i, j].axis('off')

            gain_nice = np.round(gain.data, 1)
            time_nice = np.round(time.data, 1)
            axs[i, j].title.set_text('Gain(dB): {}, Time(s): {}'.format(gain_nice, time_nice))
            
        
    plt.show()
