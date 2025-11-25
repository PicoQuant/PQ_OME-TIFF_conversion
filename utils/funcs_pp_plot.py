
import numpy as np
#import matplotlib
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
#import matplotlib.gridspec as gridspec
#import matplotlib.patches as patches
import matplotlib.font_manager as fm

from PIL import Image, ImageDraw, ImageFont
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors

plt.style.use('default')

#%%


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def clamp_bright_pxs(im, sat=0.02):
    thres = 1 - sat / 100
    
    a = np.histogram(im.ravel(),1000)
    a1 = np.cumsum(np.histogram(im.ravel(),1000)[0])/im.shape[0]/im.shape[1]
    a2 = a[1][np.max(np.argwhere(a1<thres))]
    im2 = im.copy()
    im2[im2>a2] = a2
    
    return im2

def FLIM_im(int_im, lt_im, gamma=1.0, title_txt='tbd',
            tau_min=0, tau_max=5, use_cmap='PQ0',
            trunc_l=0, trunc_u=1.0, show_fig=False,
            save_to=(True,'test.png'), draw_cbar_tick_lines=False, 
            draw_scalebar=(False, 1, 0.05, 'µm', 40, 40)):

    # ------------------------
    # Process intensity
    # ------------------------
    int_im_plot_vals = int_im.copy()
    int_im = int_im ** gamma
    int_im = int_im / np.max(int_im)

    # ------------------------
    # Colormap
    # ------------------------
    cmaps_PQ = []
    cmaps_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_0_Red-Green-Blue.txt')[:,1:]/255)
    cmaps_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_1_Blue-Green-Yellow.txt')[:,1:]/255)
    cmaps_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_2_Cyan-Green-Magenta.txt')[:,1:]/255)
    cmaps_PQ.append(np.genfromtxt('ColorSchemes/ColorScheme_3_Cyan-Magenta-Yellow.txt')[:,1:]/255)

    if use_cmap.startswith('PQ'):
        idx = int(use_cmap[2])
        cmap = LinearSegmentedColormap.from_list('PQ', cmaps_PQ[idx], N=100)
        new_cmap = truncate_colormap(cmap, trunc_l, trunc_u)
    elif use_cmap == 'hsv_r':
        cmap = plt.get_cmap('hsv').reversed()
        new_cmap = truncate_colormap(cmap, trunc_l, trunc_u)
    elif use_cmap == 'jet':
        cmap = plt.get_cmap('jet')
        new_cmap = truncate_colormap(cmap, trunc_l, trunc_u)
    elif use_cmap == 'inferno':
        cmap = plt.get_cmap('inferno')
        new_cmap = truncate_colormap(cmap, trunc_l, trunc_u)    
    else:
        new_cmap = plt.get_cmap('viridis')

    # ------------------------
    # Image normalization
    # ------------------------
    H, W = lt_im.shape
    lt_im_norm = (lt_im - tau_min) / (tau_max - tau_min)
    lt_im_norm = np.clip(lt_im_norm, 0, 1)
    
    # ------------------------
    # Upscale small images
    # ------------------------
    upscale_factor = 1
    # if H < 750 or W < 750:
    #     upscale_factor = 2
    #     lt_im = np.repeat(np.repeat(lt_im, 2, axis=0), 2, axis=1)
    #     lt_im_norm = np.repeat(np.repeat(lt_im_norm, 2, axis=0), 2, axis=1)
    #     int_im = np.repeat(np.repeat(int_im, 2, axis=0), 2, axis=1)
    #     int_im_plot_vals = np.repeat(np.repeat(int_im_plot_vals, 2, axis=0), 2, axis=1)
    #     H, W = lt_im_norm.shape
    if 1024/H > 1 or 1024/W > 1:
        upscale_factor = np.floor(np.max([1024/H,1024/W])).astype(np.int16)
        lt_im = np.repeat(np.repeat(lt_im, upscale_factor, axis=0), upscale_factor, axis=1)
        lt_im_norm = np.repeat(np.repeat(lt_im_norm, upscale_factor, axis=0), upscale_factor, axis=1)
        int_im = np.repeat(np.repeat(int_im, upscale_factor, axis=0), upscale_factor, axis=1)
        int_im_plot_vals = np.repeat(np.repeat(int_im_plot_vals, upscale_factor, axis=0), upscale_factor, axis=1)
        H, W = lt_im_norm.shape

    # ------------------------
    # Scaling
    # ------------------------
    scale = H / 1400   # reference
    pad = int(40 * scale)
    title_pad = int(80 * scale)
    cbar_width = int(40 * scale)

    # ------------------------
    # Font
    # ------------------------
    font_path = fm.findfont("DejaVu Sans Bold")  # portable
    title_font = ImageFont.truetype(font_path, int(48 * scale))
    tick_font = ImageFont.truetype(font_path, int(32 * scale))
    label_font = ImageFont.truetype(font_path, int(36 * scale))


    # ------------------------
    # Apply colormap
    # ------------------------
    rgba = new_cmap(lt_im_norm)
    rgba[..., 3] = int_im
    rgba_uint8 = (rgba * 255).astype(np.uint8)
    image_rgba = Image.fromarray(rgba_uint8, "RGBA")

    # ------------------------
    # Colorbar
    # ------------------------
    def render_colorbar(cmap, vmin, vmax, height, width=cbar_width):
        y = np.linspace(vmax, vmin, height)
        y_norm = (y - vmin) / (vmax - vmin)
        rgb = (cmap(y_norm)[..., :3] * 255).astype(np.uint8)
        bar = np.repeat(rgb[:, None, :], width, axis=1)
        return Image.fromarray(bar, "RGB")

    colorbar_img = render_colorbar(new_cmap, tau_min, tau_max, H)

    # ------------------------
    # Canvas
    # ------------------------
    total_w = image_rgba.width + colorbar_img.width + pad * 3 * 2
    total_h = image_rgba.height + pad * 3 + title_pad
    canvas = Image.new("RGB", (total_w, total_h), (0, 0, 0))
    canvas.paste(image_rgba, (pad, pad + title_pad), image_rgba)
    cbar_x = pad * 2 + image_rgba.width
    cbar_y = pad + title_pad
    canvas.paste(colorbar_img, (cbar_x, cbar_y))

    draw = ImageDraw.Draw(canvas)

    # ------------------------
    # Draw title
    # ------------------------
    bbox = draw.textbbox((0, 0), title_txt, font=title_font)
    title_x = (canvas.width - (bbox[2] - bbox[0])) // 2
    title_y = pad
    draw.text((title_x, title_y), title_txt, fill=(255, 255, 255), font=title_font)

    # ------------------------
    # Draw colorbar ticks
    # ------------------------
    ticks = np.linspace(tau_min, tau_max, 5)
    tick_positions = pad + title_pad + (1 - (ticks - tau_min) / (tau_max - tau_min)) * H

    for t, y in zip(ticks, tick_positions):
        label = f"{t:.2f}"
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = cbar_x + colorbar_img.width + 10
        ty = int(y - th / 2)
        draw.text((tx, ty), label, fill=(255, 255, 255), font=tick_font)

        if draw_cbar_tick_lines:
            y_int = int(y)
            draw.line((cbar_x, y_int, cbar_x + colorbar_img.width -1, y_int), fill=(255, 255, 255), width=max(1, int(6 * scale)))


    # ------------------------
    # Draw colorbar label (fixed spacing)
    # ------------------------
    cb_label = "Lifetime [ns]"
    # measure label size
    tmp_canvas = Image.new("RGBA", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp_canvas)
    bbox = tmp_draw.textbbox((0, 0), cb_label, font=label_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad_label = int(10 * scale)
    label_img = Image.new("RGBA", (text_w + 2*pad_label, text_h + 2*pad_label), (0,0,0,0))
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((pad_label, pad_label), cb_label, font=label_font, fill=(255,255,255,255))
    label_img_rot = label_img.rotate(90, expand=True)
    
    # compute max tick label width
    tick_label_max_w = max(draw.textbbox((0,0), f"{t:.2f}", font=tick_font)[2] for t in ticks)
    
    # place label right of colorbar + tick labels + extra padding
    label_x = cbar_x + cbar_width + tick_label_max_w + int(20*scale)
    label_y = pad + title_pad + (H // 2) - (label_img_rot.height // 2)
    canvas.paste(label_img_rot, (label_x, int(label_y)), label_img_rot)


    # ------------------------
    # Draw scalebar
    # ------------------------
    if draw_scalebar[0]:
        sb_length = draw_scalebar[1]  # physical units
        pixel_size = 1/upscale_factor * draw_scalebar[2] # physical units/pixel
        unit_text = draw_scalebar[3] if len(draw_scalebar) > 3 else "units"
        offset_x = draw_scalebar[4] if len(draw_scalebar) > 4 else 10  # px from left
        offset_y = draw_scalebar[5] if len(draw_scalebar) > 5 else 10  # px from bottom
    
        bar_width = int(sb_length / pixel_size)
        bar_height = max(3, int(6*scale))  # proportional to scale
        sb_x = pad + offset_x
        sb_y = pad + title_pad + image_rgba.height - bar_height - offset_y
        draw.rectangle([sb_x, sb_y, sb_x + bar_width, sb_y + bar_height], fill=(255,255,255))
        
        # Draw label above the bar with a gap based on font height
        sb_label = f"{sb_length:.1f} {unit_text}"
        bbox = draw.textbbox((0,0), sb_label, font=tick_font)
        label_w = bbox[2]-bbox[0]
        label_h = bbox[3]-bbox[1]
        
        vertical_gap = label_h // 2 + 2  # half font height + small extra gap
        draw.text((sb_x + bar_width//2 - label_w//2, sb_y - label_h - vertical_gap),
                  sb_label, fill=(255,255,255), font=tick_font)


    # ------------------------
    # Show figure
    # ------------------------
    if show_fig:
        fig = plt.figure(figsize=(10, 10), facecolor='black')
        ax = fig.add_subplot(111)
        ax.set_facecolor('black')
        ax.imshow(np.asarray(canvas), interpolation='nearest')
        ax.axis('off')

        origin_x = pad
        origin_y = pad + title_pad

        def format_coord(x, y):
            x_raw = int(x - origin_x)
            y_raw = int(y - origin_y)
            if 0 <= x_raw < W and 0 <= y_raw < H:
                return (f"pixel repetition={upscale_factor}, "
                        f"x={x_raw}, y={y_raw}   "
                        f"lt={lt_im[y_raw, x_raw]:.2f}   "
                        f"int={int_im_plot_vals[y_raw, x_raw]:.1f}")
            return ""

        ax.format_coord = format_coord
        plt.tight_layout()
        plt.show()

    if save_to[0]:
        canvas.save(save_to[1])
