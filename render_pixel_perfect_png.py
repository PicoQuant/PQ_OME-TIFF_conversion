
import numpy as np
import matplotlib.pyplot as plt
import tifffile
import xml.etree.ElementTree as ET

from utils.funcs_pp_plot import FLIM_im, clamp_bright_pxs

plt.close('all')


# the python colorbars need some truncation to facilitate a color-mapping similar 
# to the colormaps traditionally used for FLIM
# good starting values for "jet" are trunc_l = 0.25, trunc_u = 0.75 
# good starting values for "hsv_r" are trunc_l = 0.4, trunc_u = 0.95 

gamma = 1       # make the intensity scale non-linear. Accentuate dim features with gamma<1
clamp = 0.1     # data-dependent: clamp the max. intensity to the value of the 1-clamp percentile value, i.e. reduce the influence of bright spots


tau_min = 2.5   
tau_max = 3.5

ome_file = 'Examples/Example_Neurons_OME_TIF.tif'
scalebar_length = 10

### load the example data and reading the pixelsize from the metadata
with tifffile.TiffFile(ome_file) as tif:
    image_array = tif.asarray()  # NumPy array
    metadata = tif.ome_metadata   # OME XML as string
    root = ET.fromstring(metadata)
    ns = {"ome": "http://www.openmicroscopy.org/Schemas/OME/2016-06"}
    
    for pixels in root.findall(".//ome:Pixels", ns):
        size_x = float(pixels.attrib.get("PhysicalSizeX"))
        unit_x = pixels.attrib.get("PhysicalSizeXUnit")
       

int_im = clamp_bright_pxs(image_array[0], clamp)
lt_im  = image_array[1] *1e9




### render a pixel-perfect png, including title, colorbar, scalebar as a png
title_txt = 'fast lifetime image - cmap is PQ0'
save_to = (True, 'Examples/lifetime_im_pixel_perfect.png')

FLIM_im(int_im, lt_im, gamma, title_txt, tau_min, tau_max, use_cmap = 'PQ0', trunc_l = 0.01, trunc_u = 1.0, show_fig = 1, save_to = save_to,
        draw_cbar_tick_lines = True, draw_scalebar=(True, scalebar_length, size_x, unit_x, 40, 40))



#%%##################################################################
# cropping and scaling examples
#####################################################################


# small images are upscaled to keep the visual appearence the same
# this is done by repeating the pixel in 2x2, 3x3, .. nxn block and hence no interpolation is present
title_txt = 'fast lifetime image - small square sub-image'
save_to = (False, 'Examples/lifetime_im_pixel_perfect.png')

FLIM_im(int_im[:333,:333], lt_im[:333,:333], gamma, title_txt, tau_min, tau_max, use_cmap = 'jet', trunc_l = 0.25, trunc_u = 0.75, show_fig = 1, save_to = save_to,
        draw_cbar_tick_lines = True, draw_scalebar=(True, 1/2*scalebar_length, size_x, unit_x, 40, 40))


                # if the image is not square the smallest axis determins the upscaling
title_txt = 'fast lifetime image - non-square sub-image'
save_to = (False, 'Examples/lifetime_im_pixel_perfect.png')

FLIM_im(int_im[:512,:153], lt_im[:512,:153], gamma, title_txt, tau_min, tau_max, use_cmap = 'jet', trunc_l = 0.25, trunc_u = 0.75, show_fig = 1, save_to = save_to,
        draw_cbar_tick_lines = True, draw_scalebar=(True, 1/2*scalebar_length, size_x, unit_x, 40, 40))


#%%##################################################################
# cropping and scaling examples
#####################################################################


# small images are upscaled to keep the visual appearence the same
# this is done by repeating the pixel in 2x2, 3x3, .. nxn block and hence no interpolation is present
title_txt = 'fast lifetime image - cmap is jet'
save_to = (False, 'Examples/lifetime_im_pixel_perfect.png')

FLIM_im(int_im, lt_im, gamma, title_txt, tau_min, tau_max, use_cmap = 'jet', trunc_l = 0.25, trunc_u = 0.75, show_fig = 1, save_to = save_to,
        draw_cbar_tick_lines = True, draw_scalebar=(True, scalebar_length, size_x, unit_x, 40, 40))


# if the image is not square the smallest axis determins the upscaling
title_txt = 'fast lifetime image - cmap is hsv_r'
save_to = (False, 'Examples/lifetime_im_pixel_perfect.png')

FLIM_im(int_im, lt_im, gamma, title_txt, tau_min, tau_max, use_cmap = 'hsv_r', trunc_l = 0.4, trunc_u = 0.95, show_fig = 1, save_to = save_to,
        draw_cbar_tick_lines = True, draw_scalebar=(True, scalebar_length, size_x, unit_x, 40, 40))