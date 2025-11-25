# PQ_OME-TIFF_conversion
Python script to convert OME-TIFFs recorded with the PicoQuant Luminosa microscope to intensity-weighted lifetime images.

Execute from command line by typing `python .\convert_ome_to_FLIM.py` and follow the instructions to define the minimum and maximum of the lifetime map and choose a color map.
The additional script `render_pixel_perfect_png.py` allows to render a non-interpolated png including scale and color bars.

# Example conversion:
![Example](https://raw.githubusercontent.com/AndersBarth/PQ_OME-TIFF_conversion/master/Examples/Example.png)


# Available colormaps:
![PQ Colormaps](https://raw.githubusercontent.com/AndersBarth/PQ_OME-TIFF_conversion/master/ColorSchemes/PQ_colormaps.png)
