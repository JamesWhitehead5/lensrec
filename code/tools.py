import csv
import xarray
import os
import sys
from PIL import Image
import numpy as np
import cv2
from camera_bitdepth_tests import _describe_array
import matplotlib.pyplot as plt

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

def save_as_png(xr_data: xarray, path):
    make_dir(path)
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

def save_xarray_as_16bit_tiff(xr_data:xarray, path):
    make_dir(path)
    for i, z in enumerate(xr_data.coords['zs'].data):
        data = xr_data.isel(zs=i).data
        filename = os.path.join(path, "z_{0:.3f}mm.png".format(np.round(z, 3)))
        save_as_16bit_tiff(data, filename)
        
def save_as_16bit_tiff(data: np.array, filename):
    assert data.dtype == np.uint16, "Data type should be unsigned 16 bit"
    data = np.left_shift(data, 4)
    #_describe_array(data)
    #plt.imshow(data/np.max(data))
    plt.show()
    cv2.imwrite(filename + ".tiff", data)
    

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
    image_extensions = ['jpg', 'jpeg', 'png', 'bmp']
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

def save_single_for_ndarray(data, file):
    print("SAving files to hard drive")
    im = Image.fromarray(data)
    im.save(file)


if __name__=='__main__':
    _testbench_save_dict_to_txt()
