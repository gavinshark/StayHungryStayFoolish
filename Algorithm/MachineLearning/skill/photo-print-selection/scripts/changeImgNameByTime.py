# -*- coding: utf-8 -*-
from PIL import Image
import os
import time
import cv2
import re
import uuid
import shutil
from datetime import date

try:
    from pillow_heif import open_heif, register_heif_opener
    register_heif_opener()
except ImportError:
    open_heif = None
    register_heif_opener = None

def formatTime(secs):
    str = time.strftime("%Y-%m-%d", time.localtime(secs))
    return str

def getExifTime(imagePath):
    if os.path.splitext(imagePath)[-1].lower() in ['.heic', '.heif']:
        if open_heif is None:
            raise RuntimeError('pillow-heif is required to read HEIC metadata')
        exifData = open_heif(imagePath).info.get('exif')
        if not exifData:
            return None
        exif = Image.Exif()
        exif.load(exifData)
        return exif.get(36867)

    imge = Image.open(imagePath)
    exifData = imge._getexif()
    imageDate = exifData[36867]
    return imageDate

def getImgTime(imgPath):
    imageDate = None
    isExif = True
    try:
        imageDate = getExifTime(imgPath)
    except Exception as e:
        print('%s failed to getExifTime, exception is %s' % (imgPath, str(e)))
        imageDate = None

    if imageDate == '' or imageDate is None:
        isExif = False
        try:
            imageDate = formatTime(os.stat(imgPath).st_mtime)
        except Exception as e:
            print('%s failed to st_mtime, exception is %s' % (imgPath, str(e)))
            imageDate = None

    if imageDate == '' or imageDate is None:
        try:
            imageDate = formatTime(os.path.getmtime(imgPath))
        except Exception as e:
            print('%s failed to getmtime, exception is %s' % (imgPath, str(e)))
            imageDate = None

    if imageDate == '' or imageDate is None:
        imageDate = None

    return imageDate, isExif

def getSizeParamofTag(shape):
    # font & size
    font = 2
    thickness = 6
    maxValue = shape[1] if shape[1] > shape[0] else shape[0]
    if maxValue > 8192: #width
        font = 8
        thickness = 24
    elif maxValue > 1024:
        font = int(maxValue/1024)
        thickness = int(maxValue/1024)*3
    else:
        None

    # margin
    left, bottom = 300, 500
    if 0.05 * shape[1] >  font*20:#width
        left = 0.05 * shape[1]
    else:
        left = font*20
        
    if 0.05 * shape[0] >  font*20:
        bottom = 0.95 * shape[0]
    else:
        bottom = shape[0]-200
    

    margin = (int(left), int(bottom))
    return margin, font, thickness

def getColorofTag(img, font, margin):
    color = (66,155,253)
    return color

def addTag(inputImagePath, outputImagePath, imageDate):
    img = cv2.imread(inputImagePath)
    #get photo size
    shape = img.shape
    margin, font, thickness = getSizeParamofTag(shape)
    #get photo color
    color = getColorofTag(img, shape, margin)
    #
    modifiedImage = cv2.putText(img, imageDate, margin, cv2.FONT_HERSHEY_SIMPLEX, font, color, thickness, cv2.LINE_AA)
    cv2.imwrite(outputImagePath, modifiedImage)
    print('%s - %s' % (inputImagePath, imageDate))

zhmodel = re.compile(u'[\u4e00-\u9fa5]')
def formatImageName(imgPath, imgName):
    rawpath = os.path.join(imgPath, imgName)
    if zhmodel.search(imgName) :
        suffix = os.path.splitext(imgName)[-1]
        imgName = str(uuid.uuid4()) + suffix
        newpath = os.path.join(imgPath, imgName)
        os.rename(rawpath, newpath)
        print('%s renamed to %s' % (rawpath, newpath))
    return imgName

def convertHeicToJpg(imagePath):
    """Convert a HEIC file after its source name has been normalized."""
    if open_heif is None:
        raise RuntimeError('pillow-heif is required to convert HEIC files')

    jpgPath = os.path.splitext(imagePath)[0] + '.jpg'
    heifImage = open_heif(imagePath)
    # pillow-heif 1.x exposes the decoded pixel buffer as a memoryview;
    # bytes() keeps this compatible with the Pillow version used by the project.
    image = Image.frombytes(
        heifImage.mode,
        heifImage.size,
        bytes(heifImage.data),
        'raw',
        heifImage.mode,
        heifImage.stride,
    ).convert('RGB')
    image.save(jpgPath, 'JPEG', quality=95)
    image.close()
    print('%s converted to %s' % (imagePath, jpgPath))
    return jpgPath

def isValidImgFilePath(filePath):
    validSuffixList = ['.jpg', '.bmp', '.jpeg', '.tiff', '.png', '.gif', '.raw', '.eps', '.svg', '.heic', '.heif']
    suffix = os.path.splitext(filePath)[-1]
    ret = False
    if suffix.lower() in validSuffixList:
        ret = True
    return ret

def changeNameAndCopyFiles(srcPath, dstPath):
    if not os.path.isdir(srcPath):
        print('source path: %s does not exist' % srcPath)
        return 0,[]
    if not os.path.isdir(dstPath):
        print('dst path:%s does not exist, create it' % dstPath)
        os.mkdir(dstPath)
    total = 0
    abnormalImgs = []
    for imgName in os.listdir(srcPath):
        originalPath = os.path.join(srcPath, imgName)
        if os.path.isdir(originalPath):
            abnormalImgs.append(originalPath)
            continue
        if not isValidImgFilePath(imgName):
            abnormalImgs.append(originalPath)
            continue

        isHeic = os.path.splitext(imgName)[-1].lower() in ['.heic', '.heif']
        rawpath = originalPath
        generatedJpgPath = None
        try:
            # HEIC metadata must be read before the file is renamed and converted.
            if isHeic:
                imgTime, isExif = getImgTime(rawpath)
                imgName = formatImageName(srcPath, imgName)
                rawpath = os.path.join(srcPath, imgName)
                copyPath = convertHeicToJpg(rawpath)
                generatedJpgPath = copyPath
                copyName = os.path.basename(copyPath)
            else:
                imgName = formatImageName(srcPath, imgName)
                rawpath = os.path.join(srcPath, imgName)
                imgTime, isExif = getImgTime(rawpath)
                copyPath = rawpath
                copyName = imgName

            total += 1
            result = re.sub(r':', '-', imgTime, flags=re.IGNORECASE)
            print(result)
            tagpath = os.path.join(dstPath, result + copyName)
            #if not isExif:
            #    abnormalImgs.append(tagpath)
            #addTag(copyPath, tagpath, imgTime)
            shutil.copyfile(copyPath, tagpath)

        except Exception as e:
            print('failed to add tag for %s, exception is %s, but we still copy the files' % (imgName, str(e)))
            abnormalImgs.append(rawpath)
        finally:
            if generatedJpgPath is not None and os.path.exists(generatedJpgPath):
                try:
                    os.remove(generatedJpgPath)
                    print('%s removed after copying' % generatedJpgPath)
                except OSError as e:
                    print('failed to remove generated JPG %s, exception is %s' % (generatedJpgPath, str(e)))
    return total, abnormalImgs

if __name__ == '__main__':
    srcPath = '.'
    dstPath = 'dst_copied_name_with_date'
    print('start to add tags from %s to %s:\n' % (srcPath, dstPath))
    total, abnormalImgs = changeNameAndCopyFiles(srcPath, dstPath)
    print('\n\nend with %d images adding tags, %d is abnormal' % (total, len(abnormalImgs)))
    if len(abnormalImgs) >0 :
        for img in abnormalImgs:
            print(img)
