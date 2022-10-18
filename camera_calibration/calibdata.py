import numpy as np

path=r'C:\Users\lahir\fstack_data\calibration\kinect_calib.csv'
#read a matrix from a csv file. Each row should be in a seperate line
#n=number of items per each line
#e.g to read a 3x3 calibration matrix, n=3
def read_mtx_from_csv(path,n):
    mtx=np.empty([0,n])
    with open(path, "r") as filestream:
            for line in filestream:
                line=line.replace(" ","")
                line=line.replace("\n","")
                currentline = line.split(",")
                currentline=np.array([[float(item) for item in currentline]])
                mtx=np.concatenate((mtx,currentline),axis=0)
    return mtx

#get a 3x4 intrinsic matrix from a 3x3 matrix
#i.e. append a zeros column to the end
def get_3x4intr(mtx):
    return np.concatenate((mtx,np.zeros((3,1))),axis=1)

#get homogenous vectors from a array of vectors of points (n-dimentional)
#i.e. append a column of ones at the end
def get_homo(mtx):
    return np.concatenate((mtx,np.ones((mtx.shape[0],1))),axis=1)

R=np.random.rand(3,3)
T=np.random.rand(3,1)
#concatenate the R and T matrices to form the 3x4 trans matrix
#R should be 3x3, T should be 3x1
def get_transmtx_from_RT(R,T):
    RT=np.concatenate((R,T),axis=1)
    trans=np.concatenate((RT,np.array([[0,0,0,1]])),axis=0)
    return trans
