from math import *


def fov(flen, senw, senh):
    flen = float(flen)
    senw = float(senw)
    senh = float(senh)
    fov_w = degrees(2*atan(senw/(2*flen)))
    fov_h = degrees(2*atan(senh/(2*flen)))
    fov_d = degrees(2*atan(sqrt(senw**2+senh**2)/(2*flen)))

    return fov_w, fov_h, fov_d

if __name__ == '__main__':

    flen = input("Enter camera focal length: ")
    senw = input("Enter sensor width in mm: ")
    senh = input("Enter sensor height in mm: ")

    print(fov(flen, senw, senh))
