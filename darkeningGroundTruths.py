# -*- coding: utf-8 -*-
"""
Created on Tue December 21 10:01:37 2020

@author: Deniz Kenan Kılıç
"""
import os
import numpy as np
from skimage import io
import json

''' This code darkens the areas (parking lot, etc.) where the vehicles are
standing in all frames and erases the GTs in these regions. '''

def parse_rec(filename, im_height, im_width):
    with open(filename, 'r') as f:
        lines = f.readlines()
    annotations = [x.strip() for x in lines]

    objects = []

    for annot in annotations:
        annot_struct = {}
        splitted_annot = annot.split()
        bbox_width = float(splitted_annot[3]) * im_width
        bbox_height = float(splitted_annot[4]) * im_height
        x_min = float(splitted_annot[1]) * im_width - (bbox_width-1) / 2
        x_max = float(splitted_annot[1]) * im_width + (bbox_width-1) / 2
        y_min = float(splitted_annot[2]) * im_height - (bbox_height-1) / 2
        y_max = float(splitted_annot[2]) * im_height + (bbox_height-1) / 2

        annot_struct['bbox'] = [x_min, y_min, x_max, y_max]
        annot_struct['difficult'] = 0
        annot_struct['class'] = 0
        objects.append(annot_struct)

    return objects

def gt_remove(imagePath, gtPath, roiPath, blackedOutThr, outputPath, gtType):
    """
    imagePath: Directory for .bmp images.
    gtPath: Directory for .txt or json ground truth files wrt .bmp images.
    roiPath: Directory for mask that is utilized to darken selected ROI's and
    to delete ground truths belonging in ROI's.
    blackedOutThr = Threshold ratio for the roi-object intersection to delete GT object.
    outputPath: Directory for saving darkened images and updated ground truths.
    gtType: Flag for ground truth file type, if it is "txt" then .txt files are
    operated and vice versa.
    """

    blackedoutRoi = io.imread(roiPath)
    blackedoutRoi = np.divide(blackedoutRoi, 255)
    blackedoutRoi = blackedoutRoi.astype('uint8')

    imagenamesBmp = os.listdir(imagePath)
    imagenamesBmp = [os.path.join(imagePath, bmp_file) for bmp_file in imagenamesBmp]

    outputImagePath = outputPath + r'\Updated_Images'
    if not os.path.exists(outputImagePath):
        os.makedirs(outputImagePath)

    outputGtPath = outputPath + r'\Updated_GTs'
    if not os.path.exists(outputGtPath):
        os.makedirs(outputGtPath)

    tobedeletedGTidx = {}
    imagenamesGt = os.listdir(gtPath)
    imagenamesGt = [os.path.join(gtPath, json_file) for json_file in imagenamesGt]

    if gtType == "txt" or gtType == "json":

         for i in range(len(imagenamesBmp)):
             image = io.imread(imagenamesBmp[i])
             gtImageName = os.path.split(imagenamesGt[i])

             if gtType == "txt":
                 im_height, im_width = image.shape
                 recs = parse_rec(imagenamesGt[i], im_height, im_width)

             elif gtType == "json":
                 with open(imagenamesGt[i]) as f:
                     gtData = json.load(f)
                     recs = gtData['samples']

             tobedeletedGTidx[gtImageName]= []

             for d in range(len(recs)):

                 if gtType == "txt":
                     BBGT = recs[d]['bbox']
                     BBGT = [round(z) for z in BBGT]

                 elif gtType == "json":
                     BBGT = [round(float(recs[d]['x'])),
                             round(float(recs[d]['y'])),
                             round(float(recs[d]['x'])+float(recs[d]['width']))-1,
                             round(float(recs[d]['y'])+float(recs[d]['height']))-1]

                 if np.sum(blackedoutRoi[BBGT[1]:BBGT[3], BBGT[0]:BBGT[2]] == 1) > blackedOutThr * (BBGT[3]-BBGT[1]+1) * (BBGT[2]-BBGT[0]+1):
                     tobedeletedGTidx[gtImageName].append(d)

             image = np.multiply(image, 1 - blackedoutRoi)

             bmpImageName = os.path.split(imagenamesBmp[i])
             io.imsave(outputImagePath + '\\' + bmpImageName[1] , image)

             # delete bboxes that belong to blackedoutRoi
             tobedeletedGTidx[gtImageName] = sorted(tobedeletedGTidx[gtImageName], reverse=True)

             if gtType == "txt":
                 with open(imagenamesGt[i], 'r') as f:
                     rows = f.readlines()

                 for j in range(len(tobedeletedGTidx[gtImageName])):
                     del rows[tobedeletedGTidx[gtImageName][j]]

                 with open(outputGtPath + '\\' +  gtImageName[1], 'w') as f:
                     for item in rows:
                         f.write("%s" % item)

             elif gtType == "json":
                 for j in range(len(tobedeletedGTidx[gtImageName])):
                     del gtData['samples'][tobedeletedGTidx[gtImageName][j]]

                 with open(outputGtPath + '\\' + gtImageName[1], 'w') as f:
                     json.dump(gtData, f, sort_keys=True,
                               indent=4, separators=(',', ': '))
    else:
         print("Unsupported Gt file format, supported formats are txt and json.")
    return tobedeletedGTidx

# Image paths
image_path = r'\darken_roi\BmpFiles'
# json or txt type ground truth files path
gt_path = r'\darken_roi\JsonGts'
# mask image path
roi_path = r'\darken_roi\roi_mask\mask_02.bmp'

blackedOutThr = 0.3
# path for saving results
save_path = r'\darken_roi\darkened_results\AOI_02_json' # edit this part for the new data
# flag for ground truth file type, "json" or "txt"
gt_type = "json"

tobedeletedGTidx = gt_remove(image_path, gt_path,
                             roi_path, blackedOutThr,
                             save_path, gt_type)
