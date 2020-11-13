"""General purpose tools"""

import csv
import pickle
import xarray
import os
import sys
import numpy as np
import cv2

def save_dict_to_txt(dic, fname):
    with open(fname, "w") as f:
        w = csv.writer(f)
        for key, val in dic.items():
            w.writerow([key, val])


def add_vars_to_dic(var_name_list: list, all_vars: dict) -> dict:
    """Takes a list of varible name strings and puts these
    varibales and their values into a dictionary"""
    values = [all_vars[var] for var in var_name_list]
    return dict(zip(var_name_list, values))


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


def _testbench_save_dict_to_txt():

    a = 4
    b = "hellow me"
    c = 40

    var_list = ["b", "a"]

    dic = add_vars_to_dic(var_list, locals())
    fname = 'test.out'
    save_dict_to_txt(dic, fname)


def ensure_no_overwrite(filename):
    #check if the file exists
    if (os.path.exists(filename)):
        overwrite = query_yes_no("Filename {} already exists. Do you want to overwrite?".format(filename))
        if overwrite:
            pass
        else:
            sys.exit(1)

def make_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)

##def save_as_png(xr_data: xarray, path):
##    make_dir(path)
##    print("SAving files to hard drive")
##
##    for i, z in enumerate(xr_data.coords['zs'].data):
##        data = xr_data.isel(zs=i).data
##        rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)
##        print(np.sum(np.sum(rescaled)))
##        im = Image.fromarray(rescaled)
##        #print("{0:05f}".format(0.1989899989))
##        filename = os.path.join(path, "z_{0:03f}mm.png".format(np.round(z, 3)))
##        im.save(filename)
##
##    print("Finished saving files to hard drive")

def save_xarray_as_16bit_tiff(xr_data:xarray, path, prefix="", no_overwrite=False):
    make_dir(path)
    for i, z in enumerate(xr_data.coords['zs'].data):
        data = xr_data.isel(zs=i).data
        filename = os.path.join(path, "{0}z_{1:.3f}mm".format(prefix, np.round(z, 3)))
        save_as_16bit_tiff(data, filename, no_overwrite)

def save_as_16bit_tiff(data: np.array, filename, no_overwrite=False):
    assert data.dtype == np.uint16, "Data type should be unsigned 16 bit"
    data = np.left_shift(data, 4)
    save_as_tiff(data, filename, no_overwrite)

def save_as_8bit_tiff(data: np.array, filename, no_overwrite=False):
    assert data.dtype == np.uint8, "Data type should be unsigned 16 bit"
    save_as_tiff(data, filename, no_overwrite)


def save_as_tiff(data: np.array, filename, no_overwrite=False):
    complete_filename = filename + ".tiff"
    if no_overwrite:
        ensure_no_overwrite(complete_filename)
    cv2.imwrite(complete_filename, data)

def save_data(xr_data, filename):
   print("\nSaving the data to the hard drive. Filename: {}".format(filename))
   pickle.dump(xr_data, open(filename, "wb" )) #save the data
   print("Finished saving!")

def load_data(filename):
   print("Loading files from the hard drive: Filename: {}".format(filename))
   xr_data = pickle.load(open(filename, "rb" ))
   print("Finished loading!!!")
   return xr_data

def is_image(f):
    image_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tif', 'tiff',\
                        'JPG', 'JPEG', 'PNG', 'BMP', 'TIF', 'TIFF']
    return any([f.endswith("." + extension) for extension in image_extensions])

def get_image_files(path):
    image_files = [os.path.join(path, f) for f in os.listdir(path) if is_image(f)]
    return image_files

def mkdir_no_overwrite(pathname_out):
    ensure_no_overwrite(pathname_out)
    try:
        os.mkdir(pathname_out)
    except OSError:
        print ("Creation of the directory %s failed" % pathname_out)
    else:
        print ("Successfully created the directory %s " % pathname_out)

# def save_single_for_ndarray(data, file):
#    print("SAving files to hard drive")
#    im = Image.fromarray(data)
#    im.save(file)

def generate_toy_image() -> np.ndarray:
    """Generates a random color image"""
    shape = (1216, 1936, 3)
    #shape = (4, 5, 3)
    data = np.random.randint(low=0, high=2**16, size=np.prod(shape), dtype=np.uint16).reshape(shape)

    #make data 12 bit
    data = np.right_shift(data, 4)
    return data


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


if __name__=='__main__':
    _testbench_save_dict_to_txt()
