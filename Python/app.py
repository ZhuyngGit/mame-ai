from enum import Enum
import pyautogui
import mss
import numpy
import cv2
import imagehash
from PIL import Image
import ctypes
import sendkeys
import time, sys

class States(Enum):
    WaitingForMameShellStartup = 1
    WaitingForGameShellStartup = 2
    WaitingForGameToStart = 3


def InsertCoin():
    pyautogui.moveTo(3000, 500)
    pyautogui.click()
    sendkeys.SendScanCodeInput(0x06)

def StartGame():
    pyautogui.moveTo(3000, 500)
    pyautogui.click()
    sendkeys.SendScanCodeInput(0x02)

def SendKey(key):
    ctypes.windll.user32

def SampleScreen():
    with mss.mss() as sct:
        monitor_number = 1
        mon = sct.monitors[monitor_number]
        monitor = {
            "top": mon["top"]+33,
            "left": mon["left"] + 604,
            "width": 732,
            "height": 1180,
            "mon": monitor_number,
        }
        img = numpy.array(sct.grab(monitor))
        return img


def TransformScreenCapture():
    # gray scale?
    return 0


def GetScore(frame):
    DIGIT_WIDTH = 27
    DIGIT_TOP = 30
    DIGIT_BOTTOM = 54
    ONES_RIGHT = 169

    hashes = {
        "1c2663636363341c": 0,
        "1c2663636363361c": 0,
        "0c1c0c0c0c0c1e3f": 1,
        "0c1c0c0c0c0c3e3f": 1,
        "3e63071e3c38707f": 2,
        "3f060c1e0703673e": 3,
        "3f060c1e0303633e": 3,
        "0e1e36667f7f0606": 4,
        "7e607e060303663e": 5,
        "7e607e030303633e": 5,
        "1e30607c6663663e": 6,
        "1e30607e6663663e": 6,
        "1e30607e6763623e": 6,
        "ffe7060c18181818": 7,
        "7f67060c18181818": 7,
        "7f63060c18181818": 7,
        "3c6272384ecf463e": 8,
        "3c62723c4e4f463e": 8,
        "3c62723c0e4f463e": 8,
        "3c62723c4e4f423e": 8,
        "3e63637f07060c3c": 9,
        "0000000000000000": 0
    }
    value = 0

    multiplier = 1
    for digit in range(4):
        digitframe = frame[DIGIT_TOP:DIGIT_BOTTOM, ONES_RIGHT -
                           (DIGIT_WIDTH * (digit+1)):ONES_RIGHT-(DIGIT_WIDTH*digit)]
        digithash = str(imagehash.average_hash(Image.fromarray(digitframe)))

        if digithash == "0000000000000000":
            break

        if digithash in hashes:
            value += multiplier * hashes[digithash]
        else:
            # cv2.imshow('ones', digitframe)
            print("unexpected hash for digit: " + str(digit) + " = " + digithash)

        multiplier = multiplier * 10

    return value

def IsGameEnded(frame):
    # look for word 'credit' at bottom of screen
    creditframe = frame[969:997, 35:198]
    # cv2.imshow('creditarea', creditframe)
    credithash = str(imagehash.average_hash(Image.fromarray(creditframe)))
    if credithash == '12ffa8307860fe10':
        return True

    # look for word 'game' in middle of screen
    # look for word 'over' in middle of screen
    return False

def HasCredit(frame):
    # look for anything but zero in the first position
    creditcountframe = frame[969:997, 251:277]
    # cv2.imshow('creditcountarea', creditcountframe)
    credithash = str(imagehash.average_hash(Image.fromarray(creditcountframe)))
    if credithash == '0000000000000000':
        return False

    if credithash == '383c46c7c7e63c18':
        return False
    
    return True

def WaitingForStartup(frame):
    startupframe = frame[550:585, 278:440]
    # cv2.imshow('startupframe', startupframe)
    credithash = str(imagehash.average_hash(Image.fromarray(startupframe)))
    if credithash == '00ffdffebcf82000':
        return True
    
    return False


# ******************* main loop *******************
a = 1
while True:
    frame = SampleScreen()

    scores = GetScore(frame)
    print('Score = ' + str(scores))
    if IsGameEnded(frame):
        print('game ended')
        InsertCoin()
        if HasCredit(frame):
            StartGame()
    else:
        if not WaitingForStartup(frame):
            if a == 1:
                a = 0
                sendkeys.SendScanCodeInput(0xCB)
            else:
                a = 1
                sendkeys.SendScanCodeInput(0xCD)

