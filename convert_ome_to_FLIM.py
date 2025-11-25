import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from tkinter import filedialog, simpledialog, Tk
from tifffile import imread

# define PQ colormap
cmap_PQ = []
cmap_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_0_Red-Green-Blue.txt')[:,1:]/255)
cmap_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_1_Blue-Green-Yellow.txt')[:,1:]/255)
cmap_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_2_Cyan-Green-Magenta.txt')[:,1:]/255)
cmap_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_3_Cyan-Magenta-Yellow.txt')[:,1:]/255)

root = Tk()
root.withdraw()
fn = filedialog.askopenfilename(initialdir='Examples',initialfile='Example_Neurons_OME_TIF.tif')

root = Tk()
root.withdraw()
lt_min = simpledialog.askfloat('Min. LT (ns)', 'Enter the minimum LT value in ns:', initialvalue=0)
lt_max = simpledialog.askfloat('Max. LT (ns)', 'Enter the maximum LT value in ns:', initialvalue=6)

cmap_idx = simpledialog.askinteger('Colormap #', 'Choose Colormap:', initialvalue=0)
if cmap_idx > 3:
    cmap_idx = 3

PQ = LinearSegmentedColormap.from_list('PQ', cmap_PQ[cmap_idx], N=100) 

# Load the image
image = imread(fn)

intensity = image[0]
lt = image[1]*1e9

lt[lt < lt_min] = lt_min
lt[lt > lt_max] = lt_max
lt_norm = (lt - lt_min) / (lt_max - lt_min)

# define color based on lifetime
cmap = plt.get_cmap(PQ)
lt_colors = cmap(lt_norm)[:,:,:-1]

# define brightness based on intensity
int_norm = intensity/np.max(intensity)
img_flim = lt_colors*int_norm[:,:,None]

# save image
plt.imsave(fn[:-4]+'_FLIM.png',(255*img_flim).astype(np.uint8),format='PNG')
plt.imsave(fn[:-4]+'_FLIM.tif',img_flim,format='TIFF')

# plot result
plt.figure(figsize=(10,3))

ax1=plt.subplot(1,3,1)
plt.imshow(intensity)
plt.set_cmap('gray')
plt.title('Intensity')
plt.gca().set_xticks([])
plt.gca().set_yticks([])

ax2=plt.subplot(1,3,2,sharex=ax1,sharey=ax1)
plt.imshow(lt,cmap=PQ)
plt.title('Lifetime')
plt.gca().set_xticks([])
plt.gca().set_yticks([])
cb = plt.colorbar(orientation='vertical')
cb.set_label('$\\tau$ (ns)')
cb.ax.tick_params(labelsize=8)

l, b, w, h = ax2.get_position().bounds
ll, bb, ww, hh = ax1.get_position().bounds
ax2.set_position([l-0.035,bb,ww,hh])
l, b, w, h  = cb.ax.get_position().bounds
cb.ax.set_position([l+0.005,b,w,h])

plt.subplot(1,3,3,sharex=ax1,sharey=ax1)
plt.imshow(img_flim)
plt.title('FLIM')
plt.gca().set_xticks([])
plt.gca().set_yticks([])
plt.show()
