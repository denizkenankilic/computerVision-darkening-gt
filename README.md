# computerVision-darkening-gt
Darkening a Certain Area in Images and Deleting Unwanted Ground Truths

The Python script darkens the areas (a parking lot, etc.) where the vehicles are standing in all frames and erases the GTs (example contains bounding box type ground truths) in these regions. A mask is utilized to darken selected ROI's and to delete ground truths belonging in ROI's.
