# computerVision-darkening-gt
Darkening a Certain Area in Images and Deleting Unwanted Ground Truths

The Python script darkens the areas (parking lots, etc.) where the vehicles are standing in all frames and erases the GTs (example contains bounding box type ground truths) in these regions. A mask is utilized to darken selected ROIs and to delete ground truths belonging in ROIs.
