from math import ceil, floor
import azurekinect.read_azure_img as imgread
from matplotlib import pyplot as plt
import camera_calibration.calibdata as calib
import numpy as np
from scipy import interpolate
import math

'''
We need to interpolate the depth image after coordinate frame transformation because the 
projections are not perfect due to floating point arithmatic, inperfections in projection matrix values etc. 
Therefore some values in the final depth image are missing. 
interpolate_missing_pixels is coppied from 
https://stackoverflow.com/questions/37662180/interpolate-missing-values-2d-python
post by Sam De Meyer and G M
'''
def interpolate_missing_pixels(
        image: np.ndarray,
        mask: np.ndarray,
        method: str = 'nearest',
        fill_value: int = 0
):

    h, w = image.shape[:2]
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))

    known_x = xx[~mask]
    known_y = yy[~mask]
    known_v = image[~mask]
    missing_x = xx[mask]
    missing_y = yy[mask]

    interp_values = interpolate.griddata(
        (known_x, known_y), known_v, (missing_x, missing_y),
        method=method, fill_value=fill_value
    )

    interp_image = image.copy()
    interp_image[missing_y, missing_x] = interp_values

    return interp_image


x,y,z=imgread.read_ptc(r'C:\Users\lahir\fstack_data\data\10_18_2022_16_20_44\000.ptc')

#read the calibration matrix of phone
phone_intri=calib.read_mtx_from_csv(r'C:\Users\lahir\fstack_data\calibration\phone_calib.csv',3)
phone_intri=calib.get_3x4intr(phone_intri)
#read the translation and rotation matrices kinect -> phone
R=calib.read_mtx_from_csv(r'C:\Users\lahir\fstack_data\calibration\azuretophone_R.csv',3)
T=calib.read_mtx_from_csv(r'C:\Users\lahir\fstack_data\calibration\azuretophone_T.csv',1)
RT=calib.get_transmtx_from_RT(R,T)

trans_pts=[]
for i in range(len(x)):
    pt=np.array([[list(x[i])[0],list(y[i])[0],list(z[i])[0]]])
    pt=calib.get_homo(pt).T
    #transform point to phone coordinate system
    pt_trans=np.matmul(RT,pt)
    pt_trans=pt_trans/pt_trans[-1]
    #get distance to the point from camera center
    dist=list(np.sqrt(pt_trans[0]*pt_trans[0] + pt_trans[1]*pt_trans[1] + pt_trans[2]*pt_trans[2]))[0]
    #transform this point to image coordinate system with phone's intrinsic matrix
    pt_trans=np.matmul(phone_intri,pt_trans)
    pt_trans=list(pt_trans[:,0])
    
    if(pt_trans[-1]==0):
        trans_pts.append([0.0,0.0,0.0])
    else:
        trans_pts.append([pt_trans[0]/pt_trans[-1],pt_trans[1]/pt_trans[-1],dist])

#taking round should be more accurate than using the floor and ceil method below (commented)
image=np.zeros(imgread.transformed_shape)
for pt in trans_pts:
    if(round(pt[0])>0 and round(pt[0])<imgread.transformed_shape[1] and round(pt[1])>0 and round(pt[1])<imgread.transformed_shape[0]):
        image[round(pt[1]),round(pt[0])]=pt[-1]
'''
image=np.zeros(imgread.transformed_shape)
for pt in trans_pts:
    if(round(pt[0])>0 and math.ceil(pt[0])<imgread.transformed_shape[1] and round(pt[1])>0 and math.ceil(pt[1])<imgread.transformed_shape[0]):
        image[math.ceil(pt[1]),math.ceil(pt[0])]=pt[-1]
        image[math.floor(pt[1]),math.floor(pt[0])]=pt[-1]
'''

#mask = what pixels are needed of interpolating ?
#criteria to select these pixels : if at least two pixles of the surrounding pixels are not zero
#because the artefact zero pixels are mostly single pixles. Pixels around them have proper values.
mask=np.zeros_like(image)
for h in range(1,image.shape[0]-1):
    for w in range(1,image.shape[1]-1):
        n_nonzero=0
        if(image[h,w]==0):
            #look around this pixel
            if(image[h-1,w]>0): n_nonzero+=1
            if(image[h+1,w]>0): n_nonzero+=1
            if(image[h,w-1]>0): n_nonzero+=1
            if(image[h,w+1]>0): n_nonzero+=1
            if(image[h-1,w-1]>0): n_nonzero+=1
            if(image[h-1,w+1]>0): n_nonzero+=1
            if(image[h+1,w-1]>0): n_nonzero+=1
            if(image[h+1,w+1]>0): n_nonzero+=1
            if(n_nonzero>=2):
                mask[h,w]=1
mask=mask==1

res=interpolate_missing_pixels(image,mask)
plt.imshow(res)
plt.show()

