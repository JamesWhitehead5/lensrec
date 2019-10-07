from pymba import Vimba, VimbaException
import os
from tools import generate_toy_image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpngw import write_png
import png
import time
import csv
from enum import Enum


class Bitdepth(Enum):
        EIGHT = 1
        TWELVE = 2

class Camera():
    PIXEL_FORMAT = {Bitdepth.EIGHT: 'BayerRG8',
                    Bitdepth.TWELVE: 'BayerRG12',
                    }

    def take_picture(gain_dB, exposure_time_s, bitdepth=Bitdepth.EIGHT,
        props={}, debug_mode=False) -> np.ndarray:


        props['ExposureTimeAbs'] = int(exposure_time_s*1e6) #exposure time in us
        props['Gain'] = gain_dB #gain in dB
        props['BlackLevel'] = 0
        props['PixelFormat'] = Camera.PIXEL_FORMAT[bitdepth]

        if debug_mode:
            time.sleep(exposure_time_s)
            return generate_toy_image()
        #Connect to the Prosilica GT camera via a Power over Ethernet cable. Make
        #sure that the drivers are installed. This is tested the the Vimba 3.0 SDK.
        with Vimba() as vimba: #start camera interface
            camera = vimba.camera(0)
            try:
                camera.open()
            except VimbaException:
                print("It is likely that the VimbaViewer is open. \
                \nOnly a single program can access the camera at a time")

            camera.feature('ExposureTimeAbs').value = props['ExposureTimeAbs']
            camera.feature('Gain').value = props['Gain']
            camera.feature("BlackLevel").value = props['BlackLevel']
            camera.feature("PixelFormat").value = props['PixelFormat']
            camera.arm('SingleFrame')


            try:
                frame = camera.acquire_frame(timeout_ms=int(exposure_time_s*1000 + 1000))
            except VimbaException as e:
                # rearm camera upon frame timeout
                if e.error_code == VimbaException.ERR_TIMEOUT:
                    print(e)
                    camera.disarm()
                    camera.arm('SingleFrame')
                else:
                    raise
            image = Camera._frame_to_image(frame)
        return image

    def _save_property_data(props, filename):
        with open(filename, "w") as f:
            w = csv.writer(f)
            for key, val in props.items():
                w.writerow([key, val])

    def _frame_to_image(frame) -> np.ndarray:
        """Converts RAW camera output frame to a RGB array"""
        image = frame.buffer_data_numpy()

        #demosaic the data
        image2 = cv2.cvtColor(image, cv2.COLOR_BAYER_RG2RGB)
        return image2





##Testbenches and examples for the Camera object


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

def aquire_image_and_log():
    props = {'one': 'two'}
    Camera.take_picture(gain_dB=40, exposure_time_s=0.05, props=props)
    fname = os.path.join('./', "test1.out")
    Camera._save_property_data(props, fname)

def _aquire_image() -> np.ndarray:
    return Camera.take_picture(gain_dB=40, exposure_time_s=0.05)

def _display_image_histogram(data: np.ndarray) -> None:
    """Plots a log histogram for image values"""
    n_bins = 256
    data = np.ndarray.flatten(data)
    plt.hist(data, bins=n_bins)
    ax = plt.gca()
    ax.set_yscale('log')
    plt.show()

@timeit
def _save_to_file(data: np.ndarray, fname) -> None:
    """Saves a 3D RGB numpy array to a png"""
    shifted_data = np.left_shift(data, 4)
    write_png(fname, shifted_data, bitdepth=16)

@timeit
def _open_file(f) -> np.ndarray:
    #Tried Pillow/PIL, cv2, scipy, imageio
    """Loads an image file and returns the data as a 3d array"""
    reader = png.Reader(f)
    ny, nx, image_gen, *_ = reader.read()
    data = np.array(list(map(np.uint16, image_gen)))
    data = data.reshape(nx, ny, 3)
    shifted_data = np.right_shift(data, 4)

    return shifted_data

def _describe_array(arr: np.ndarray) -> None:
    """prints array properties"""
    print("Array shape: {}".format(np.shape(arr)))
    print("Array dtype: {}".format(arr.dtype))
    print("All bits or'd: {}".format(bin(_determine_bit_depth(arr))))
    print("Max: {}".format(np.max(arr)))
    print("Min: {}".format(np.min(arr)))
    print()

def _determine_bit_depth(numbers: np.ndarray) -> np.uint16:
    """Performs a bitwise or operator between all elements in the array and returns the result"""
    numbers_flat = np.ndarray.flatten(numbers)
    return np.bitwise_or.reduce(numbers_flat)

def _generate_toy_image() -> np.ndarray:
    """Generates a random color image"""
    #shape = (1216, 1936, 3)
    shape = (4, 5, 3)
    data = np.random.randint(low=0, high=2**16, size=np.prod(shape), dtype=np.uint16).reshape(shape)

    #make data 12 bit
    data = np.right_shift(data, 4)
    return data

def _test_save_and_load():
    #generate data to save
    toy_data = _generate_toy_image()
    _describe_array(toy_data)

    #setup file to save the data as
    f1 = os.path.join("./", "test1.png")
    f2 = os.path.join("./", "test2.png")

    #save the data
    _save_to_file(data=toy_data, fname=f1)

    #load the data
    toy_data_load = _open_file(f1)
    _describe_array(toy_data_load)

    print("Loaded and save arrays are:")
    if np.array_equal(toy_data, toy_data_load):
        print("Identical")
    else:
        print("Different")

    #save the data
    _save_to_file(data=toy_data_load, fname=f2)

def _test_save_and_load_with_camera():
    data1 = _aquire_image()
    _describe_array(data1)

    f1 = os.path.join("./", "test1.png")
    f2 = os.path.join("./", "test2.png")

    _save_to_file(data=data1, f=f1)
    data2 = _open_file(f1)
    _describe_array(data2)

    _save_to_file(data=data2, f=f2)
    data3 = _open_file(f2)
    _describe_array(data3)

    if np.array_equal(data1, data2) and np.array_equal(data1, data3):
        print("Equal")

def _np_load_save_benchmark():
    f = os.path.join("./", "test.npy")
    data = _aquire_image()

    @timeit
    def save():
        np.save(f, data, allow_pickle=False)

    @timeit
    def load():
        return(np.load(f))

    save()
    out = load()

    assert np.array_equal(data, out), "arrays are not the same"

if __name__=="__main__":
    #_test_save_and_load()
    #_test_save_and_load_with_camera()
    #_np_load_save_benchmark()
    aquire_image_and_log()
