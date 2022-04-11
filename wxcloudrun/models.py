from datetime import datetime

# import self
from django.db import models

import os

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

from PIL import Image
import cv2 as cv
import numpy as np
from cnocr import CnOcr

import pandas as pd

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKIDPeePvDG4dwznMgk9PQCiz0mIZbNuBDzV'
secret_key = 'KPEn6B0ZsvjHZbNuBCyUkkUzVmnY3JJ3'
region = 'ap-guangzhou'

token = None
scheme = 'https'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)

k = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)

list_frame = [[0 for pos in range(2)] for num in range(20)]
list_text = [[0 for pos in range(2)] for num in range(20)]
list_string = []

# Create your models here.
class Counters(models.Model):
    id = models.AutoField
    count = models.IntegerField(max_length=11, default=0)
    createdAt = models.DateTimeField(default=datetime.now(),)
    updatedAt = models.DateTimeField(default=datetime.now(),)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Counters'  # 数据库表名


class OCR():

    def gray(self, img):
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 25, 5)
        return img

    def frame(self, line_img, image):
        global list_frame
        height = line_img.shape[0]
        width = line_img.shape[1]

        height_b = int(height * 0.1)
        height_w = int(height * 0.03)

        width_b = int(width * 0.01)
        width_w = int(width * 0.02)

        line_img = cv.cvtColor(line_img, cv.COLOR_BGR2GRAY)
        ret, thr = cv.threshold(line_img, 150, 255, cv.THRESH_BINARY_INV)

        horizontal = [0] * height
        vertical = [0] * width

        hfg = [[0 for col in range(2)] for row in range(height)]
        lfg = [[0 for col in range(2)] for row in range(width)]

        black = 0
        for y in range(0, height):
            for x in range(0, width):
                if thr[y, x] == 0:
                    black += 1
                else:
                    continue
            horizontal[y] = black
            black = 0

        inline = 1
        time = 0
        start = 0
        j = 0
        for i in range(0, height):
            if inline == 1 and horizontal[i] <= height_b:
                start = i
                inline = 0
                # print(i)
            if (i - start > height_w) and horizontal[i] > height_b and inline == 0:
                inline = 1
                hfg[j][0] = start - 2
                hfg[j][1] = i + 2
                j = j + 1
                # print(i)

        black = 0
        for p in range(3, 4):
            for x in range(0, width):
                for y in range(hfg[p][0], hfg[p][1]):
                    if thr[y, x] == 0:
                        black += 1
                    else:
                        continue
                vertical[x] = black
                black = 0
            # print width

            incol = 1
            time = 0
            start = 0
            j = 0
            b1 = hfg[p][0]
            b2 = hfg[p][1]
            for i in range(0, width):
                if incol == 1 and vertical[i] < width_b:
                    start = i
                    incol = 0
                    # print(i)
                if (i - start > width_w) and vertical[i] >= width_b and incol == 0:
                    incol = 1
                    lfg[j][0] = start - 2
                    lfg[j][1] = i + 2
                    a1 = start - 2
                    a2 = i + 2
                    # print(i)
                    if (time > 0):
                        cv.rectangle(image, (a1, b1), (a2, b2), (255, 0, 0), 2)
                        list_frame[j * 2 - 2][0] = a1
                        list_frame[j * 2 - 2][1] = b1
                        list_frame[j * 2 - 1][0] = a2
                        list_frame[j * 2 - 1][1] = b2
                    time += 1
                    j += 1

        # cv.namedWindow("result", 0)
        # cv.imshow('result', image)

    def line_detective(self, img, gray_img):
        line_img = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

        gray_img = cv.Canny(gray_img, 50, 150)

        lines = cv.HoughLinesP(gray_img, 1, np.pi / 180, 20, minLineLength=40, maxLineGap=2)

        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv.line(line_img, (x1, y1), (x2, y2), (255, 255, 255), 2)

        self.frame(line_img, img)

    def text_detective(self, img):
        global list_text
        height = img.shape[0]
        width = img.shape[1]

        limit = int(height * 0.05)
        low = int(height * 0.01)

        horizontal = [0] * height

        black = 0
        for y in range(0, height):
            for x in range(0, width):
                if img[y, x] == 0:
                    black += 1
                else:
                    continue
            horizontal[y] = black
            black = 0

        inline = 1
        time = 0
        start = 0
        j = 0
        for i in range(low, height):
            if inline == 1 and horizontal[i] > 20:
                start = i
                inline = 0
                # print(i)
            if (i - start > limit) and horizontal[i] < 20 and inline == 0:
                inline = 1
                list_text[j][0] = start - 2
                list_text[j][1] = i + 2
                j = j + 1
                # print(i)

        # cv.imshow("g", img)
        return j

    def cut(self, img, gray):
        global list_string
        ocr = CnOcr()
        name = "cut.png"
        for i in range(8):
            # print(i)
            cuti = img[list_frame[i * 2][1]: list_frame[i * 2 + 1][1], list_frame[i * 2][0]: list_frame[i * 2 + 1][0]]

            if (i == 0):
                cutg = gray[list_frame[i * 2][1]: list_frame[i * 2 + 1][1],
                       list_frame[i * 2][0]: list_frame[i * 2 + 1][0]]
                lines = self.text_detective(cutg)
                list_string = [[0 for pos in range(8)] for num in range(lines - 2)]

            for j in range(1, lines):
                arr = cuti[list_text[j][0]: list_text[j][1], :]
                cv.imwrite(name, arr)
                res, cnt = ocr.ocr_for_single_line(name)
                string = ''
                for each in res:
                    string = string + each
                # print(string)
                if (j < lines - 1):
                    list_string[j - 1][i] = string

            i += 1

    def start(self, key):
        response = client.get_object(
            Bucket='test-1304530197',
            Key=key,
        )

        response['Body'].get_stream_to_file('output.txt')

        src = cv.imread('output.txt')
        # cv.imshow("", src)

        img = src

        gray_img = self.gray(src)

        self.line_detective(img, gray_img)

        self.cut(img, gray_img)

        data = pd.DataFrame(list_string)

        writer = pd.ExcelWriter('return.xlsx')
        data.to_excel(writer, 'page_1', float_format='%.5f')
        writer.save()

        writer.close()

        with open('return.xlsx', 'rb') as fp:
            response = client.put_object(
                Bucket='test-1304530197',
                Body=fp,
                Key='return.xlsx',
                StorageClass='STANDARD',
                EnableMD5=False
            )

        return 'return.xlsx'

