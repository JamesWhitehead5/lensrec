import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpngw import write_png
import png
import time


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
    #write_png(fname, shifted_data, bitdepth=16)
    cv2.imwrite(fname, data,)

##@timeit
##def _save_to_file(data: np.ndarray, fname) -> None:
##    data = np.reshape(data, (-1, data.shape[2]))
##    png.from_array(data, 'RGB;16').save(fname)


##@timeit
##def _save_to_file(data: np.ndarray, fname) -> None:
##    z=data
##    print(data)
##    # Use pypng to write z as a color PNG.
##    with open(fname, 'wb') as f:
##        writer = png.Writer(width=z.shape[0], height=z.shape[1], bitdepth=16)
##        # Convert z to the Python list of lists expected by
##        # the png writer.
##        z2list = np.transpose(z, axes=((0, 2, 1)))
##        #z2list = z2list.reshape(-1, z.shape[0]).tolist()
##        z2list = z.tolist()
##        print(z2list)
##        writer.write(f, z2list)
        
@timeit
def _open_file(f) -> np.ndarray:
    #Tried Pillow/PIL, cv2, scipy, imageio
    """Loads an image file and returns the data as a 3d array"""
    #reader = png.Reader(f)
    #ny, nx, image_gen, *_ = reader.read()
    #data = np.array(list(map(np.uint16, image_gen)))
    #data = data.reshape(nx, ny, 3)
    
    data = cv2.imread(f, -1)
    
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
    shape = (1216, 1936, 3)
    #shape = (4, 5, 3)
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
    _test_save_and_load()
    #_np_load_save_benchmark()
    
    

    
