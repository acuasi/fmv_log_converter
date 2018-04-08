from math import *


def fov(flen, senw, senh):
    flen = float(flen)
    senw = float(senw)
    senh = float(senh)
    fov_horizontal = degrees(2*atan(senw/(2*flen)))
    fov_vertical = degrees(2*atan(senh/(2*flen)))
    fov_diagonal = degrees(2*atan(sqrt(senw**2+senh**2)/(2*flen)))

    return fov_horizontal, fov_vertical, fov_diagonal

if __name__ == '__main__':

    flen = input("Enter camera focal length: ")
    senw = input("Enter sensor width in mm: ")
    senh = input("Enter sensor height in mm: ")

    print(fov(flen, senw, senh))
