#!/usr/bin/python3

"""
A GUI front end for converting Phantom 3 log files to a format to be able to
be ingested by ArcMap's Video Multiplexing Tool for Full Motion Video
"""

import sys
import litchiconverter
import fov
from lxml import etree
from PyQt5.QtWidgets import (QWidget, QApplication, QAction,
                             QComboBox, QVBoxLayout, QLabel, QFileDialog,
                             QDesktopWidget, QMainWindow, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DEFAULT_LOG_DIR = ''

ABOUT_TEXT = """
             ArduCopter log converter program, v0.1 \
             Converts ArduCopter logs into an acceptable \
             format to be ingested by the ArcGIS Video \
             Multiplexing tool \n\r \
             Northern Embedded Solutions, 2016
             """

# Map xml elements to variables for code readability
NAME = 0
FLEN = 1
IMGH = 2
IMGW = 3
SENH = 4
SENW = 5

xml_map = {}

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 900


class ConvGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.camera_chosen = 0
        self.log_chosen = 0
        self.log_type_chosen = 0
        self.output_dir_chosen = 0

        centralWidget = QWidget()

        # ______Labels______

        # Label for camera drop down list
        cameraLabel = QLabel('Choose Camera')
        cameraLabel.setAlignment(Qt.AlignCenter)

        # Label for log type drown down list
        logTypeLabel = QLabel('Choose Type of Log')
        logTypeLabel.setAlignment(Qt.AlignCenter)

        # Label for log conversion buttons
        self.logLabel = QLabel('Log Conversion')
        self.logLabel.setAlignment(Qt.AlignCenter)

        # Labels for User Input values
        inputLabel = QLabel('User Values')
        inputLabel.setAlignment(Qt.AlignCenter)
        amslLabel = QLabel('Average AMSL (m)')
        amslLabel.setAlignment(Qt.AlignCenter)

        # Unnecessary labels
        #
        # missionIdLabel = QLabel('Name of Mission')
        # missionIdLabel.setAlignment(Qt.AlignCenter)
        # tailNumLabel = QLabel('Aircraft N or registration number')
        # tailNumLabel.setAlignment(Qt.AlignCenter)
        # platDesigLabel = QLabel('Aircraft Designation')
        # platDesigLabel.setAlignment(Qt.AlignCenter)
        # imageSensorLabel = QLabel('Image sensor name')
        # imageSensorLabel.setAlignment(Qt.AlignCenter)
        # coordSysLabel = QLabel('Coordinate system (e.g. WGS84)')
        # coordSysLabel.setAlignment(Qt.AlignCenter)

        # QLineEdits for getting user values
        self.amslInput = QLineEdit()
        # self.missionIdInput = QLineEdit()
        # self.tailNumInput = QLineEdit()
        # self.platDesigInput = QLineEdit()
        # self.imageSensorInput = QLineEdit()
        # self.coordSysInput = QLineEdit()

        # ______Buttons______

        # Create camera drop down list of supported cameras
        # from cameras.xml profile document
        # Use parser to ensure pretty print works, see:
        # http://lxml.de/FAQ.html#why-doesn-t-the-
        # pretty-print-option-reformat-my-xml-output
        parser = etree.XMLParser(remove_blank_text=True)
        self.xml_tree = etree.parse('cameras.xml', parser)
        self.xml_root = self.xml_tree.getroot()

        # Initialize QComboBox object with default text
        cameraType = QComboBox(self)
        cameraType.addItem('Select a Camera')

        # Loop through the children of the xml root
        # get the camera name and add to the drop down list
        index = 0
        for child in self.xml_root:

            self.camera = child[NAME].text
            cameraType.addItem(self.camera)
            # Populate the xml map list with the camera name and
            # it's index in the root list so we can refer to it's values
            # later
            xml_map[self.camera] = index
            index += 1

        cameraType.setEditable(True)
        cameraType.lineEdit().setReadOnly(True)
        cameraType.lineEdit().setAlignment(Qt.AlignCenter)

        # Align the dropdown options to be centered
        for i in range(0, cameraType.count()):
            cameraType.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

        cameraType.activated[str].connect(self.cameraChosen)

        # Create Log type drop down menu
        self.logType = QComboBox(self)
        self.logType.addItem('Select Log Type')
        # self.logType.addItem('DJI GO')
        self.logType.addItem('Litchi')

        for i in range(0, self.logType.count()):
            self.logType.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)

        self.logType.setEditable(True)
        self.logType.lineEdit().setReadOnly(True)
        self.logType.lineEdit().setAlignment(Qt.AlignCenter)

        self.logType.activated[str].connect(self.logTypeChosen)

        # Create push button for adding a new camera profile
        newCameraBtn = QPushButton('Add New Camera')
        newCameraBtn.clicked.connect(self.newCamera)

        # Create push button object that opens the log file
        # to be converted
        chooseLogBtn = QPushButton('Open log file...')
        chooseLogBtn.clicked.connect(self.openFile)

        # Push button to start log conversion
        convertBtn = QPushButton('Convert!')
        convertBtn.clicked.connect(self.convertLog)

        # Button for setting output file location
        saveLocBtn = QPushButton('Set output save location...')
        saveLocBtn.clicked.connect(self.saveLocation)

        # Quit button
        quitBtn = QPushButton('Exit Program')
        quitBtn.clicked.connect(self.close)

        # ______Layout______

        # Create vertical box layout
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(cameraLabel)
        vbox.addWidget(cameraType)
        vbox.addWidget(newCameraBtn)
        vbox.addStretch()
        vbox.addWidget(logTypeLabel)
        vbox.addWidget(self.logType)
        vbox.addStretch()
        vbox.addWidget(inputLabel)
        vbox.addWidget(amslLabel)
        vbox.addWidget(self.amslInput)
        # vbox.addWidget(missionIdLabel)
        # vbox.addWidget(self.missionIdInput)
        # vbox.addWidget(tailNumLabel)
        # vbox.addWidget(self.tailNumInput)
        # vbox.addWidget(platDesigLabel)
        # vbox.addWidget(self.platDesigInput)
        # vbox.addWidget(imageSensorLabel)
        # vbox.addWidget(self.imageSensorInput)
        # vbox.addWidget(coordSysLabel)
        # vbox.addWidget(self.coordSysInput)
        vbox.addStretch()
        vbox.addWidget(self.logLabel)
        vbox.addWidget(chooseLogBtn)
        vbox.addWidget(saveLocBtn)
        vbox.addWidget(convertBtn)
        vbox.addStretch()
        vbox.addWidget(quitBtn)

        centralWidget.setLayout(vbox)

        # Create quit action
        quit = QAction('Quit', self)
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip('Exit program')
        quit.triggered.connect(self.close)

        # Create about action
        about = QAction('About LogConverter', self)
        about.setShortcut('Ctrl+A')
        about.setStatusTip('About program')
        about.triggered.connect(self.aboutProgram)

        # Create menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(quit)
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(about)

        self.setCentralWidget(centralWidget)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center()

        self.setWindowTitle('Log Converter')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openFile(self):
        self.log_file = QFileDialog.getOpenFileName(
            self, 'Open file', None)[0]
        self.log_chosen = 1

    # QFileDialog:getSaveFileName will pass name even if it doesn't exist
    # unlike QFileDialog:getOpenFileName; Linux doesn't seem to care but
    # Windows definitely does
    def saveLocation(self):
        self.save_location = QFileDialog.getSaveFileName(
            self, 'Choose save location', None)[0]

    def cameraChosen(self, text):

        # Make sure an actual camera was chosen
        if text != 'Select a Camera':
            # When a camera is chosen change the value in our camera variable
            self.camera = text

            # We need the index for the particular camera chosen.
            # We obtain this from our xml_map dictionary:
            # xml_map[camera] maps to index number of that
            # particular camera's element in root
            # the constant e.g. FLEN then maps to the index of that subelement
            # So we get: xml_root[camera_index][parameter_index]
            # and .text gives us the actual text value of that element
            self.flen = self.xml_root[xml_map[self.camera]][FLEN].text
            self.imagew = self.xml_root[xml_map[self.camera]][IMGW].text
            self.imageh = self.xml_root[xml_map[self.camera]][IMGH].text
            self.sensorw = self.xml_root[xml_map[self.camera]][SENW].text
            self.sensorh = self.xml_root[xml_map[self.camera]][SENH].text

            self.camera_chosen = 1

    def logTypeChosen(self, text):

        if text != 'Select Log Type':
            self.log = text
            self.log_type_chosen = 1

    def newCamera(self):
        self.newCamera = QWidget()

        # Labels for popup window
        nameLbl = QLabel('Enter Descriptive Camera Name:')
        flenLbl = QLabel('Enter Camera Focal Length [mm]:')
        imghLbl = QLabel('Enter Image Height [pixels]:')
        imgwLbl = QLabel('Enter Image Width [pixels]:')
        senwLbl = QLabel('Enter Sensor Width [mm]:')
        senhLbl = QLabel('Enter Sensor Height [mm]:')
        notice = QLabel('New camera will be available upon restart of the GUI')

        notice.setAlignment(Qt.AlignCenter)

        # Set font size and color for notice
        notice_font = QFont()
        notice_font.setPointSize(8)
        notice_font.setBold(True)
        notice.setFont(notice_font)
        notice.setStyleSheet("QLabel { color : red;}")

        # QLineEdit objects for user values
        self.nameEdit = QLineEdit()
        self.flenEdit = QLineEdit()
        self.imghEdit = QLineEdit()
        self.imgwEdit = QLineEdit()
        self.senwEdit = QLineEdit()
        self.senhEdit = QLineEdit()

        # Button for submitting values
        submitBtn = QPushButton('Create Camera Profile')
        submitBtn.clicked.connect(self.writeXML)

        # Build a vertical layout
        vLayout = QVBoxLayout()
        vLayout.addStretch()
        vLayout.addWidget(nameLbl)
        vLayout.addWidget(self.nameEdit)
        vLayout.addWidget(flenLbl)
        vLayout.addWidget(self.flenEdit)
        vLayout.addWidget(imgwLbl)
        vLayout.addWidget(self.imgwEdit)
        vLayout.addWidget(imghLbl)
        vLayout.addWidget(self.imghEdit)
        vLayout.addWidget(senwLbl)
        vLayout.addWidget(self.senwEdit)
        vLayout.addWidget(senhLbl)
        vLayout.addWidget(self.senhEdit)
        vLayout.addStretch()
        vLayout.addWidget(submitBtn)
        vLayout.addStretch()
        vLayout.addWidget(notice)
        vLayout.addStretch()

        # Set up and show window
        self.newCamera.setLayout(vLayout)
        self.newCamera.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Center widget
        qr = self.newCamera.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.newCamera.move(qr.topLeft())

        # Set title, show and call exec function
        self.newCamera.setWindowTitle('Add New Camera')
        self.newCamera.show()
        # self.newCamera.exec_()

    def writeXML(self):
        # Get values from user
        name = self.nameEdit.text()
        flen = self.flenEdit.text()
        imgw = self.imgwEdit.text()
        imgh = self.imghEdit.text()
        senw = self.senwEdit.text()
        senh = self.senhEdit.text()

        # Create subelement "camera" and then sub elements to that:
        # name, flen, imgw, imagh, senw, senh
        Camera = etree.SubElement(self.xml_root, 'Camera')
        xml_name = etree.SubElement(Camera, 'name')
        xml_name.text = name
        xml_flen = etree.SubElement(Camera, 'flen')
        xml_flen.text = flen
        xml_imgw = etree.SubElement(Camera, 'imgw')
        xml_imgw.text = imgw
        xml_imgh = etree.SubElement(Camera, 'imgh')
        xml_imgh.text = imgh
        xml_senw = etree.SubElement(Camera, 'senw')
        xml_senw.text = senw
        xml_senh = etree.SubElement(Camera, 'senh')
        xml_senh.text = senh

        # Overwrite camera profile file
        self.xml_tree.write('cameras.xml', pretty_print=True)

        # Close widget to return user to main GUI window
        self.newCamera.close()

    def aboutProgram(self):
        QMessageBox.about(self, "About LogConverter", ABOUT_TEXT)

    def convertLog(self):

        if self.camera_chosen == 0:
            QMessageBox.information(self, 'Warning', 'Select a Camera!')

        elif self.log_type_chosen == 0:
            QMessageBox.information(self, 'Warning', 'Select Log Type!')

        elif self.log_chosen == 0:
            QMessageBox.information(self, 'Warning', 'Select Log File!')

        else:
            fov_values = fov.fov(self.flen, self.sensorw, self.sensorh)
            fov_horizontal = fov_values[0]
            fov_vertical = fov_values[1]

            amsl = self.amslInput.text()

            # if (self.log == 'DJI GO'):
            #     converter.converter(
            #         self.log_file, self.save_location,
            #         fov_h, fov_w, amsl)
            #     QMessageBox.information(self, 'Message', 'Log converted!')

            if (self.log == 'Litchi'):
                self.converted = litchiconverter.converter(
                    self.log_file, self.save_location, fov_horizontal,
                    fov_vertical, amsl)
                if(self.converted):
                    QMessageBox.information(self, 'Message', 'Log converted!')
                else:
                    QMessageBox.information(self, 'Message', 'No video in log file.')


if __name__ == '__main__':

    app = QApplication(sys.argv)
    # app.setStyle('Cleanlooks')
    gui = ConvGUI()
    sys.exit(app.exec_())
