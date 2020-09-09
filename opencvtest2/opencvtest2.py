import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io

import glob
import os
from pathlib import Path

#STEP1 - Read image and define pixel size
#img = cv2.imread("image/grains1.jpg", -1)

clusterlist = []

img_dir = "images" # Enter Directory of all images  
data_path = os.path.join(img_dir,'*g') 
files = glob.glob(data_path) 
images = [] 
for file in files: 
    image = cv2.imread(file) 
    images.append(image)

for img in images:
    pixels_to_um = 0.5 # (1 px = 500 nm)

    cv2.imshow('thing', img)
    cv2.waitKey()

    HSVimage = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    #cv2.imshow("H chanel", HSVimage [:,:,0])
    #cv2.waitKey()

    #cv2.imshow("S chanel", HSVimage [:,:,1])
    #cv2.waitKey()

    #cv2.imshow("V chanel", HSVimage [:,:,2])
    #cv2.waitKey()

    #Segment the red shade
    blue = cv2.inRange(HSVimage,(30,0,0),(120,255,255))
    #cv2.imshow("Blue Shade",blue)
    #cv2.waitKey()

    blue = cv2.bitwise_not(blue)
    #cv2.imshow("Blue",blue)
    #cv2.waitKey()

    kernel = np.ones((3,3),np.uint8)
    dilated = cv2.dilate(blue,kernel,iterations = 2)

    #cv2.imshow("dilated",dilated)
    #cv2.waitKey()

    eroded = cv2.erode(dilated,kernel,iterations = 2)

    #cv2.imshow("eroded",eroded)
    #cv2.waitKey()

    mask = eroded == 255


    s = [[1,1,1],[1,1,1],[1,1,1]]
    #label_im, nb_labels = ndimage.label(mask)
    labeled_mask, num_labels = ndimage.label(mask, structure=s)

    #The function outputs a new image that contains a different integer label 
    #for each object, and also the number of objects found.

    img2 = color.label2rgb(labeled_mask, bg_label=0)

    cv2.imshow('Colored Grains', img2)
    cv2.waitKey()

    #View just by making mask=threshold and also mask = dilation (after morph operations)
    #Some grains are well separated after morph operations

    #Now each object had a unique number in the image. 
    #Total number of labels found are...
    #print(num_labels) 

    #Step 5: Measure the properties of each grain (object)

    # regionprops function in skimage measure module calculates useful parameters for each object.

    clusterlist.append(measure.regionprops(labeled_mask, eroded))

propList = ['Area',
            'equivalent_diameter', #Added... verify if it works
            'orientation', #Added, verify if it works. Angle btwn x-axis and major axis.
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    

output_file = open('image_measurements.csv', 'w')
output_file.write("Image" + "Grain" + ",".join(propList) + '\n') #join strings in array by commas, leave first cell blank
#First cell blank to leave room for header (column names)

imageNumber = 0

for clusters in clusterlist:
    imageNumber += 1
    for cluster_props in clusters:
        #output cluster properties to the excel file
        output_file.write(str(imageNumber) + ",")
        output_file.write(str(cluster_props['Label']))
        for i,prop in enumerate(propList):
            if(prop == 'Area'): 
                to_print = cluster_props[prop]*pixels_to_um**2   #Convert pixel square to um square
            elif(prop == 'orientation'): 
                to_print = cluster_props[prop]*57.2958  #Convert to degrees from radians
            elif(prop.find('Intensity') < 0):          # Any prop without Intensity in its name
                to_print = cluster_props[prop]*pixels_to_um
            else: 
                to_print = cluster_props[prop]     #Reamining props, basically the ones with Intensity in its name
            output_file.write(',' + str(to_print))
        output_file.write('\n')
    output_file.write('\n')
output_file.close()   #Closes the file, otherwise it would be read only. 