import cv2
import numpy as np

import camera
import framesprocessing


def mean(arr):
    return sum(arr)/len(arr)


def get_mean_colors(array):
    b = array[:, :, 0].mean()
    g = array[:, :, 1].mean()
    r = array[:, :, 2].mean()
    return b, g, r

def is_changed(arr1, arr2, perc):
    m1 = mean(arr1)
    m2 = mean(arr2)
    dif = abs(m1-m2)
    return max([m1, m2])/100*dif >= perc




if __name__ == "__main__":
    CLEAR = False
    cam = camera.Camera(800)
    last = None
    while True:
        frame = cam.get_frame(True)
        size, coords = framesprocessing.get_coords_split_image(frame, 16)
        nframe = cv2.resize(frame, (size[1], size[0]), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for c in coords:
            tmp_img = nframe[c[0]:c[1], c[2]:c[3]]
            b, g, r = get_mean_colors(tmp_img)
            nframe[c[0]:c[1], c[2]:c[3]] = [b, g, r]
            
            if last is not None and not CLEAR:
                bl, gl, rl = get_mean_colors(last[c[0]:c[1], c[2]:c[3]])
                
                if is_changed([b, g, r], [bl, gl, rl], 5):
                    nframe[c[0]:c[1], c[2]:c[3]] = [0, 100, 0]
            
            # text_coord = (c[2]+5, c[0]+15)
            # mean_img = round(gray[c[0]:c[1], c[2]:c[3]].mean())
            # text = f'{mean_img}'
            # cv2.putText(nframe, text, text_coord, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,250), 2)
            
            cv2.rectangle(nframe, (c[2], c[0]), (c[3], c[1]), (250, 50, 0))
        text_coord = (coords[-1][2]+5, coords[-1][0]+30)
        cv2.putText(nframe, f'{int(nframe.mean())}', text_coord, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 250, 0), 2)
        last = np.copy(nframe)
        CLEAR = not CLEAR
        if cam.is_key(27, 13):
            cam.close()
            break
        cv2.imshow('video', nframe)

















