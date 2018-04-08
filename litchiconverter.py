"""
Convert DJI Litchi log files to a specific CSV format
to be used with FMV
"""
from math import *
from shutil import copyfile
from datetime import datetime
import os

template_file = 'template.csv'

dir = "/home/samuel/Documents/"


def converter(log_file_name, out_file_name, sensor_h_fov, sensor_v_fov,
              amsl):
    # Variable for tracking if log has video and gets converted
    log_has_video = 0

    # Indexes
    # CHECKSUM is index 0 and must be the first column
    # CHECKSUm can be populated with zeros or empty, but must
    # be present as a column
    CHECKSUM = 0
    TIMESTAMP = 1
    MISSION_ID = 2
    PLATFORM_TAIL_NUM = 3
    PLAT_HEADING_ANG = 4
    PLAT_PITCH_ANG = 5
    PLAT_ROLL_ANG = 6
    PLAT_DESIG = 7
    IMG_SOURCE_SENSOR = 8
    IMG_COORD = 9
    SENSOR_LAT = 10
    SENSOR_LON = 11
    SENSOR_TRUE_ALT = 12
    SENSOR_H_FOV = 13
    SENSOR_V_FOV = 14
    SENSOR_REL_AZ_ANG = 15
    SENSOR_REL_EL_ANG = 16
    SENSOR_REL_ROLL_ANG = 17

    # MISB List Length, change this value if more columns are added
    MISB_LEN = 18

    # Only twenty values in the "green" subset
    # ArcGIS calculates the other necessary values from this subset
    misb_list = [0]*MISB_LEN

    name_map = {'timestamp': 'UNIX Time Stamp',
                'latitude': 'Sensor Latitude',
                'longitude': 'Sensor Longitude',
                'altitudeRaw': 'AGL Altitude',
                'pitchRaw': 'Platform Pitch Angle',
                'rollRaw': 'Platform Roll Angle',
                'yawRaw': 'Platform Heading Angle',
                'gimbalYawRaw': 'Sensor Azimuth Angle',
                'gimbalPitchRaw': 'Sensor Elevation Angle',
                'gimbalRollRaw': 'Sensor Roll Angle',
                'isTakingVideo': 'Record Status'}

    misb_positions = {}

    # # Get log file names
    # log_file_name = input("Enter the full name of the DJI Log file: ")
    # template_file = input("Enter the full name of the template to use: ")
    # out_file_name = input("Enter name of the output file: ")

    log_file = open(log_file_name, 'r')
    copyfile(template_file, out_file_name)
    out_file = open(out_file_name, 'r+')

    # Create list of Litchi header names
    header_list = log_file.readline().split(',')

    # Look through header list for headers in our name map dictionary
    for header in header_list:
        # If the header is in our map, get it's column position
        # and add a key value pair to the misb_positions dictionary
        # misb_value : column position
        if header in name_map:
            misb_value = name_map[header]
            header_index = header_list.index(header)
            misb_positions[misb_value] = header_index

    # Skip header line for output file
    next(out_file)

    # Iterate through Litchi log file
    for line in log_file:
        # Split line by commas
        line_list = line.split(',')

        # Get isTakingVideo value
        record = int(line_list[misb_positions['Record Status']])

        # Get DJI local datetime and convert to UNIX timestamp
        unix_timestamp = int(line_list[misb_positions['UNIX Time Stamp']])
        misb_timestamp = unix_timestamp * 1000

        # Aircraft values
        sensor_lat = float(line_list[misb_positions['Sensor Latitude']])
        sensor_lon = float(line_list[misb_positions['Sensor Longitude']])
        sensor_true_alt = float(line_list[misb_positions[
                            'AGL Altitude']])/10 + float(amsl)
        plat_pitch_ang = float(line_list[misb_positions[
                            'Platform Pitch Angle']])/10
        plat_roll_ang = float(line_list[misb_positions[
                            'Platform Roll Angle']])/10
        plat_heading_ang = float(line_list[misb_positions[
                            'Platform Heading Angle']])/10
        # Convert from (-180,180) to (0,360)
        if plat_heading_ang < 0:
            plat_heading_ang += 360

        # Gimbal values, divide by 10 to convert from raw values to degrees
        sensor_pitch_ang = float(line_list[misb_positions[
                            'Sensor Elevation Angle']])/10
        sensor_roll_ang = float(line_list[misb_positions[
                                'Sensor Roll Angle']])/10
        sensor_heading = float(line_list[misb_positions[
                                'Sensor Azimuth Angle']])/10
        # Convert from (-180,180) to (0,360)
        if sensor_heading < 0:
            sensor_heading += 360

        sensor_rel_az_ang = sensor_heading - plat_heading_ang
        # sensor_rel_az_ang = plat_heading_ang - sensor_heading
        sensor_rel_roll_ang = plat_roll_ang - sensor_roll_ang
        sensor_rel_el_ang = sensor_pitch_ang - plat_pitch_ang

        if sensor_rel_az_ang < 0:
            sensor_rel_az_ang += 360

        # Use defined tag indexes and create a list of MISB tags
        # Values of zero will not be written
        misb_list[CHECKSUM] = None
        misb_list[TIMESTAMP] = misb_timestamp
        misb_list[MISSION_ID] = None
        misb_list[PLATFORM_TAIL_NUM] = None
        misb_list[PLAT_HEADING_ANG] = plat_heading_ang
        misb_list[PLAT_PITCH_ANG] = plat_pitch_ang
        misb_list[PLAT_ROLL_ANG] = plat_roll_ang
        misb_list[PLAT_DESIG] = None
        misb_list[IMG_SOURCE_SENSOR] = None
        misb_list[IMG_COORD] = None
        misb_list[SENSOR_LAT] = sensor_lat
        misb_list[SENSOR_LON] = sensor_lon
        misb_list[SENSOR_TRUE_ALT] = sensor_true_alt
        misb_list[SENSOR_H_FOV] = sensor_h_fov
        misb_list[SENSOR_V_FOV] = sensor_v_fov
        misb_list[SENSOR_REL_AZ_ANG] = sensor_rel_az_ang
        misb_list[SENSOR_REL_EL_ANG] = sensor_rel_el_ang
        misb_list[SENSOR_REL_ROLL_ANG] = sensor_rel_roll_ang

        # If video is active write output to file
        # We only want to record logs for active video to avoid synching issues
        # if(record):
        #     for i in range(0, MISB_LEN):
        #         if i == 0:
        #             out_file.write(',')
        #         else:
        #             out_file.write(str(misb_list[i]) + ',')
        #     out_file.write('\n')
        #     log_has_video = 1
        if(record):
            for value in misb_list:
                if value is None:
                    out_file.write(',')
                else:
                    out_file.write(str(value) + ',')

            out_file.write('\n')
            log_has_video = 1

    log_file.close()
    out_file.close()

    if(log_has_video):
        return 1
    if(not log_has_video):
        return 0

if __name__ == '__main__':
    log_file_name = eval(input("Log file: "))
    out_file_name = eval(input("Name of output file: "))
    fov_h = input("Horizontal field of view: ")
    fov_v = input("Vertical field of view: ")
    amsl = input("Enter average amsl: ")

    log_file_path = os.path.normpath(log_file_name)
    out_file_path = os.path.normpath(out_file_name)
    converter(log_file_name, out_file_name, fov_h, fov_v, amsl)
