import threading
from pathlib import Path
from uuid import uuid4
from base64 import b64encode
from traceback import print_exc
from subprocess import call
import os, shutil
import imageio
import cv2
import numpy as np

#####################
# Generic Functions #
#####################
from shared_utils import folder_utils


def base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        return b64encode(image_file.read()).decode()

def make_image_data(image_path):
    return 'data:image/png;base64,' + base64_encoded_image(image_path)

def check_source_format(source_image):
    # available format - 181
    available_formats = ['.1sc', '.2', '.2fl', '.3', '.4', '.acff', '.afi', '.afm', '.aim', '.al3d', '.ali', '.am',
                         '.amiramesh', '.apl', '.arf', '.avi', '.bif', '.bin', '.bip', '.bmp', '.btf', '.c01',
                         '.cfg', '.ch5', '.cif', '.cr2', '.crw', '.csv', '.cxd', '.czi', '.dat', '.dcm', '.dib',
                         '.dicom', '.dm2', '.dm3', '.dm4', '.dti', '.dv', '.eps', '.epsi', '.exp', '.fdf', '.fff',
                         '.ffr', '.fits', '.flex', '.fli', '.frm', '.gel', '.gif', '.grey', '.h5', '.hdf', '.hdr',
                         '.hed', '.his', '.htd', '.html', '.hx', '.i2i', '.ics', '.ids', '.im3', '.img', '.ims',
                         '.inr', '.ipl', '.ipm', '.ipw', '.j2k', '.jp2', '.jpf', '.jpg', '.jpk', '.jpx', '.klb',
                         '.l2d', '.labels', '.lei', '.lif', '.liff', '.lim', '.lms', '.lsm', '.map', '.mdb',
                         '.mea', '.mnc', '.mng', '.mod', '.mov', '.mrc', '.mrcs', '.mrw', '.msr', '.mtb', '.mvd2',
                         '.naf', '.nd', '.nd2', '.ndpi', '.ndpis', '.nef', '.nhdr', '.nii', '.nii.gz', '.nrrd',
                         '.obf', '.obsep', '.oib', '.oif', '.oir', '.ome', '.ome.btf', '.ome.tf2', '.ome.tf8',
                         '.ome.tif', '.ome.tiff', '.ome.xml', '.par', '.pbm', '.pcoraw', '.pcx', '.pds', '.pgm',
                         '.pic', '.pict', '.png', '.pnl', '.ppm', '.pr3', '.ps', '.psd', '.qptiff', '.r3d', '.raw',
                         '.rcpnl', '.rec', '.res', '.scn', '.sdt', '.seq', '.sif', '.sld', '.sm2', '.sm3', '.spc',
                         '.spe', '.spi', '.st', '.stk', '.stp', '.svs', '.sxm', '.tf2', '.tf8', '.tfr', '.tga', '.tif',
                         '.tiff', '.tnb', '.top', '.txt', '.v', '.vff', '.vms', '.vsi', '.vws', '.wat', '.wlz', '.wpi',
                         '.xdce', '.xml', '.xqd', '.xqf', '.xv', '.xys', '.zfp', '.zfr', '.zvi']
    _, file_extension = os.path.splitext(source_image.name)

    try:
        available_formats.index(file_extension.lower())
        return True
    except Exception:
        print_exc()
        return False

# Save the uploaded file to a cache dir.
def save_source_image(source_image):
    dest_dir = folder_utils.get_cache_directory()

    _, file_extension = os.path.splitext(source_image.name)
    file_path = str(dest_dir.joinpath(uuid4().hex + file_extension))

    with open(file_path, mode='wb') as destination:
        for chunk in source_image.chunks():
            destination.write(chunk)
    
    return file_path

def convert_to_tiff(source_file):
    dest_dir = folder_utils.get_cache_directory('converted')
    file_name, _ = os.path.splitext(os.path.basename(source_file))
    dest_file = str(dest_dir.joinpath(file_name + '.tiff'))

    shell_script = f'gm convert {source_file} {dest_file}'
    call(shell_script, shell=True)

    return dest_file

def save_processing_file(raw_data):
    dest_dir = folder_utils.get_cache_directory('raw_data')
    file_path = str(dest_dir.joinpath(uuid4().hex + '.png'))

    with open(file_path, mode='wb') as destination:
        destination.write(raw_data)
    
    return file_path

def save_image(image_array, scale, channel):
    dest_dir = folder_utils.get_cache_directory('bioformats')
    saved_file = str(dest_dir.joinpath(uuid4().hex + '.png'))

    image_size = image_array.shape
    img = None

    if len(image_size) == 2 and channel is not None:
        r = channel['color']['r']
        g = channel['color']['g']
        b = channel['color']['b']
        if r + g + b > 0:
            x = np.array((r, g, b), dtype=np.uint8)
            _image_array = image_array / scale

            img = np.zeros(image_size + (3,))        
            img[..., 0] = _image_array * x[0]
            img[..., 1] = _image_array * x[1]
            img[..., 2] = _image_array * x[2]

            imageio.imwrite(saved_file, img)

    if img is None:
        imageio.imwrite(saved_file, image_array)

    return saved_file #, len(image_size) == 3 and image_size[2] == 3

def delete_file(file):
    t = threading.Thread(target=delete_file_thread, args=[file], daemon=True)
    t.start()

def delete_file_thread(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        print("The file does not exist")


####################
# OpenCV Functions #
####################

# def split_channels(image_file, channels):
#     origin_img = cv2.imread(image_file, 1)

#     if len(origin_img.shape) == 3:
#         height, width, _ = origin_img.shape[:3]
#     else:
#         height, width = origin_img.shape[:2]

#     zeros = np.zeros((height, width), origin_img.dtype)
#     # B, G, R
#     blue_ch, green_ch, red_ch = cv2.split(origin_img)
    
#     if channels == 'b':
#         img = cv2.merge((blue_ch, zeros, zeros))
#     elif channels == 'g':
#         img = cv2.merge((zeros, green_ch, zeros))
#     elif channels == 'r':
#         img = cv2.merge((zeros, zeros, red_ch))
#     elif channels == 'bg' or channels == 'gb':
#         img = cv2.merge((blue_ch, green_ch, zeros))
#     elif channels == 'br' or channels == 'rb':
#         img = cv2.merge((blue_ch, zeros, red_ch))
#     elif channels == 'gr' or channels == 'rg':
#         img = cv2.merge((zeros, green_ch, red_ch))
#     else:
#         img = cv2.merge((blue_ch, green_ch, red_ch))

#     dest_dir = get_cache_directory('channels')
#     new_image_file = str(dest_dir.joinpath(uuid4().hex + '.png'))
    
#     cv2.imwrite(new_image_file, img)

#     return new_image_file

def convert_to_gray(image_file, bits):
    origin_img = cv2.imread(image_file)

    img = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)

    if bits == '8':
        img = map_uint16_to_uint8(map_uint16_to_uint8(img))
    elif bits == '16':
        img = map_uint16_to_uint8(img)

    dest_dir = folder_utils.get_cache_directory('gray')
    new_image_file = str(dest_dir.joinpath(uuid4().hex + '.png'))
    
    cv2.imwrite(new_image_file, img)

    return new_image_file

def map_uint16_to_uint8(img, lower_bound=None, upper_bound=None):
    if lower_bound is not None and not(0 <= lower_bound < 2**16):
        raise ValueError(
            '"lower_bound" must be in the range [0, 65535]')
    if upper_bound is not None and not(0 <= upper_bound < 2**16):
        raise ValueError(
            '"upper_bound" must be in the range [0, 65535]')
    if lower_bound is None:
        lower_bound = np.min(img)
    if upper_bound is None:
        upper_bound = np.max(img)
    if lower_bound >= upper_bound:
        raise ValueError(
            '"lower_bound" must be smaller than "upper_bound"')

    lut = np.concatenate([
        np.zeros(lower_bound, dtype=np.uint16),
        np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
        np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
    ])
    return lut[img].astype(np.uint8)

def change_image_parameter(image_file, brightness, contrast, gamma):
    origin_img = cv2.imread(image_file)

    brightness = map(brightness, -255, 255, -255, 255)
    contrast = map(contrast, -127, 127, -127, 127)
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow)/255
        gamma_b = shadow
        buf = cv2.addWeighted(origin_img, alpha_b, origin_img, 0, gamma_b)
    else:
        buf = origin_img.copy()

    if contrast != 0:
        f = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127*(1-f)
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    dest_dir = folder_utils.get_cache_directory('temp')
    new_image_file = str(dest_dir.joinpath(uuid4().hex + '.png'))

    cv2.imwrite(new_image_file, buf)

    return new_image_file

def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

