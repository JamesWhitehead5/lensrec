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
from stage import Stage
import sys
import os
from PIL import Image
from tools import ensure_no_overwrite, save_as_png, save_data, load_data
from camera import Camera, Bitdepth

def aquire_sweep(exposure_time_s, gain_dB, current_position, relative_positions, debug_mode=False):
    """
    Sweeps the linear stage while recording camera frames at each point
    """

    #range_mm = range_thou / 39.3701

    #Ensure camera is connected before moving stage
    Camera.take_picture(gain_dB, exposure_time_s=0.1, bitdepth=Bitdepth.TWELVE, debug_mode=debug_mode)




    data = [] #list of recorded frames
    coords = None #coordinates for the aforementioned dimensions

    #start the serial communiation over the USB to the Newport ESP301 motion controller
    #List of serial commands are given in the user manaul. You can check which port
    #to use in the 'Device Manager' window.
    s1 = Stage(debug=debug_mode)
    s1.motor_on()
    #Setup sweep
    zs = relative_positions

    dzs = np.zeros(len(relative_positions))
    dzs[0] = zs[0]
    for i in range(1, len(dzs)):
        dzs[i] = zs[i] - zs[i-1]

    print(dzs)


    for i, dz in enumerate(dzs):
        #Move to an absolution location

        #update position
        s1.move_relative(-dz) #coordinate system is flipped in these setups

        #take picture
        data.append(Camera.take_picture(gain_dB, exposure_time_s,
            bitdepth=Bitdepth.TWELVE, debug_mode=debug_mode))

        print("Finished frame: {}/{}".format(i+1, len(dzs)))


        #return to the beginning
        print(s1.move_relative(np.sum(dzs)))

##        #determine dimensions
##        n_x = camera.feature('Width').value
##        n_y = camera.feature('Height').value
##        sensor_height = 5.86e-6*n_x #pixel sizes taken from manual
##        sensor_width = 5.86e-6*n_y
##        x_coords = np.linspace(-sensor_width/2., sensor_width/2., n_x)
##        y_coords = np.linspace(-sensor_height/2., sensor_height/2., n_y)
##
    s1.close()

    #these values aren't accurate and aren't used
    n_y, n_x, _ = np.shape(data[0])
    sensor_width = 5.86e-6*n_x
    sensor_height = 5.86e-6*n_y
    x_coords = np.linspace(-sensor_width/2., sensor_width/2., n_x)
    y_coords = np.linspace(-sensor_height/2., sensor_height/2., n_y)

    colors = ['r', 'g', 'b']
    xr_data=xarray.DataArray(data, coords=[zs + current_position, y_coords, x_coords, colors], dims=['zs', 'y', 'x', 'rgb'])
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