import cv2
import pyocr
import pyocr.builders

class HouchiAutoIkusei:
    _preStatusxy = [
        [380, 405,        #y1, y2
        130, 193],        #x1, x2
        [405, 435,
        130, 193],
        [435, 465,
        130, 193],
        [465, 495,
        130, 193]
    ] 
    _statusxy = [
        [380, 405,        #y1, y2
        348, 416],        #x1, x2
        [405, 435,
        348, 416],
        [435, 465,
        348, 416],
        [465, 495,
        348, 416]
    ]

    _tapxy=[
        [200, 700],     #c級/cancel
        [380, 680]      #b級/accept
    ]
    nox_dir = r"F:\\Nox\bin"
    ss_dir = r"%s\tmp" %(os.getcwd())
    pre_ss = r"%s\pre_status" %(ss_dir)
    ss = r"%s\status" %(ss_dir)
    tessract_dir = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

    def __init__(self):
        pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        tool = pyocr.get_available_tools()[0]
        builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
        builder.tesseract_configs.append("digits")

    @property
    def nox_dir(self):
        return self._nox_dir
        