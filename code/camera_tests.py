#!/bin/env/python3

from pymba import Vimba, VimbaException
#from display_frame import display_frame
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
import os
from PIL import Image

def aquire_sweep(exposure_time_s, gain_dB, frames, range_mm):
    """
    Sweeps the linear stage while recording camera frames at each point
    """

    #range_mm = range_thou / 39.3701


    data = [] #list of recorded frames
    coords = None #coordinates for the aforementioned dimensions
    
    #start the serial communiation over the USB to the Newport ESP301 motion controller
    #List of serial commands are given in the user manaul. You can check which port
    #to use in the 'Device Manager' window.
    s1 = Stage()
    s1.motor_on()


    #Connect to the Prosilica GT camera via a Power over Ethernet cable. Make
    #sure that the drivers are installed. This is tested the the Vimba 3.0 SDK.
    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        camera.feature('ExposureTimeAbs').value = int(exposure_time_s*1e6) #exposure time in us
        camera.feature('Gain').value = gain_dB #gain in dB
        camera.feature("BlackLevel").value = 0

        #Setup sweep
        distance = range_mm #mm
        num = frames #number of frames

        camera.arm('SingleFrame')

        zs = np.linspace(0., distance, num)

        dzs = np.zeros(num)
        for i in range(1, num):
            dzs[i] = zs[i] - zs[i-1]


        for i, dz in enumerate(dzs):
            #Move to an absolution location
            
            #update position
            print("Moving stage by {}mm".format(dz))
            print(s1.move_relative(-dz))
            
            try:
                t_start = time.time()
                print("Started capture of image")
                frame = camera.acquire_frame(timeout_ms=int(exposure_time_s*1000 + 1000))
                print("Finished capture of image. Took {} seconds".format(time.time()-t_start))
                frame_array = np.array(frame.buffer_data_numpy())
                data.append(frame_array)
            except VimbaException as e:
                # rearm camera upon frame timeout
                if e.error_code == VimbaException.ERR_TIMEOUT:
                    print(e)
                    camera.disarm()
                    camera.arm('SingleFrame')
                else:
                    raise

            print("Finished frame: {}/{}".format(i, len(dzs)))


        #return to the beginning
        print(s1.move_relative(np.sum(dzs)))
        
        #determine dimensions
        n_x = camera.feature('Width').value
        n_y = camera.feature('Height').value
        sensor_height = 5.86e-6*n_x #pixel sizes taken from manual
        sensor_width = 5.86e-6*n_y
        x_coords = np.linspace(-sensor_width/2., sensor_width/2., n_x)
        y_coords = np.linspace(-sensor_height/2., sensor_height/2., n_y)

        camera.disarm()
        camera.close()
    s1.close()
       
    #process the data
    PIXEL_FORMATS_CONVERSIONS = {
        'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
    }  
    for i in range(len(data)):
        #demosaic the data
        try:
            data[i] =cv2.cvtColor(data[i], PIXEL_FORMATS_CONVERSIONS[frame.pixel_format])
        except KeyError:
            pass

        #and rearrange the colors
        data[i] = cv2.cvtColor(data[i], cv2.COLOR_BGR2RGB)


    colors = ['r', 'g', 'b']
    xr_data=xarray.DataArray(data, coords=[zs, y_coords, x_coords, colors], dims=['zs', 'y', 'x', 'rgb'])
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
def ensure_no_overwrite(filename):
    #check if the file exists
    if (os.path.exists(filename)):
        overwrite = query_yes_no("Filename {} already exists. Do you want to overwrite?".format(filename))
        if overwrite:
            pass
        else:
            sys.exit(1)

def save_data(xr_data, filename):
    print("\nSaving the data to the hard drive. Filename: {}".format(filename))
    pickle.dump(xr_data, open(filename, "wb" )) #save the data
    print("Finished saving!")

def save_single_for_ndarray(data, file):
    print("SAving files to hard drive")
    im = Image.fromarray(data)
    im.save(file)

def save_as_png(xr_data, path):
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)

    print("SAving files to hard drive")

    for i, z in enumerate(xr_data.coords['zs'].data):
        data = xr_data.isel(zs=i).data
        rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
        print(np.sum(np.sum(rescaled)))
        im = Image.fromarray(rescaled)
        #print("{0:05f}".format(0.1989899989))
        filename = os.path.join(path, "z_{0:03f}mm.png".format(np.round(z, 3)))
        im.save(filename)

    print("Finished saving files to hard drive")

    
    


def load_data(filename):
    print("Loading files from the hard drive: Filename: {}".format(filename))
    xr_data = pickle.load(open(filename, "rb" ))
    print("Finished loading!!!")
    return xr_data


def plot_data(xr_data, pathname):
    #plot a frame at an index
    print("Plotting!!!")
    n = len(xr_data.coords['zs'])
    nx = int(np.ceil(np.sqrt(n)))
    ny = int(np.ceil(n/nx))
    shape = (nx, ny)
    fig, axs = plt.subplots(*shape)

    for i in range(len(xr_data.coords['zs'])):
        index = np.unravel_index(i, shape)
        xr_data.isel(zs=i).plot.imshow(ax=axs[index])

    filename = os.path.join(pathname, "image_array")
    plt.savefig(filename)
    
def plot_data_histograms(xr_data, pathname):
    #plot a frame at an index
    print("Plotting!!!")
    n = len(xr_data.coords['zs'])
    nx = int(np.ceil(np.sqrt(n)))
    ny = int(np.ceil(n/nx))
    shape = (nx, ny)
    fig, axs = plt.subplots(*shape)
    n_bins = 2**8

    for i in range(len(xr_data.coords['zs'])):
        index = np.unravel_index(i, shape)
        data = xr_data.isel(zs=i).data
        data = np.ndarray.flatten(data)
        axs[index].hist(data, bins=n_bins)
        axs[index].set_yscale('log')
        
    filename = os.path.join(pathname, "log_hist_array ")
    plt.savefig(filename)

if __name__=='__main__':
    filename = './test.pickle'

    #make sure that the selected file hasn't already been created
    ensure_no_overwrite(filename)

    #run the sweep
    xr_data = aquire_sweep(exposure_time_s=0.5, gain_dB=0., frames=5, range_mm=0.4)

    save_data(xr_data, filename)
    
    #reload the file
    xr_data = load_data(filename)

    plot_data(xr_data)
    
