# Inmuno_4channels_analysis.ipynb
 DEPRECATED: see readme file in Fiji Custom repo dev

This pipeline analyses PH3 data acquired with the Slide Scanner microscope, and outputs:
 - identification of cells of interest (PH3+) and whether they are D1 or D2
 - the position of cells of interest in the ARA
 The process uses multiple tools and is the following:
 1. Slice brains (A2A x Ai14) at 30um
 2. Stain for DARPP32 in green and PH3 in far red, and DAPI
 3. Image at 40x in the Slide Scanner the full slices
 4. Process them with They are CZI_SlideScanner_ROIsubdivider.py (in Fiji_Custom repo)
 5. Run Group_convert_and_enhance.py (in Fiji Custom repo)
 6. Downsample (3 times works ok) the DARPP32 channel. You can use ImageSequence_Downsampler.ijm in Fiji_Custom repo.
 7. Run cellpose (https://github.com/MouseLand/cellpose) on the downsampled images: 
`python -m cellpose --dir ~/Desktop/test/raw--downsized-3/ --save_tif --no_npy --diameter 28.5 --pretrained_model cyto --chan 0 --use_gpu`
 8. Run Inmuno_4channels_20210107.cpproj in CellProfiler_protocols
 9. Find the corresponding ARA slices (output of CZI_SlideScanner_ROIsubdivider.py) in MoBIE, save position and screenshot (see Histology_to_ARA repo)
 10. Register the slices using elastix (in repo Histology_to_ARA)
 11. Run the notebook Inmuno_4channels_analysis.ipynb for each mouse


# For RNAscope
This is a pipeline to visualize and analyze the results of CellProfiler on RNAscope experiments.

1. Take images in the SP8. Individual or tiled, doesn't matter. Do a z-stack and in Fiji make a maximum projection.
2. Split the channels and save them individually, with their default Fiji-titles (But removing spaces in the name!), in the folder where to do the quantification.
3. Copy the Cell-profiler project file in the CellProfilerProtocols folder into the same directory.
4. Modify the project to work with your images, and change the two output saving paths.
5. Run it. It should produce a .csv file with the statistics, and an overlay image summarizing the results.
6. Run jupyter notebook.

## steps for working with slide-scanner data
1a. Files are too big to be opened in Fiji, so they need to be cropped on import. To do this, open, using bio-formats, the low resolution version (.czi makes a piramid scheme), and draw an ROI over the region of interest and get the starting x, y, and width and height (in ROI manager More->List). Then calculate the binning (using the pixel number of the images), and correct for that during import.
1b. Alternatively, crop them directly in the zeiss software and save them.

2. Manually correct the intensity of the channels in Fiji, transform images to 8-bit, and save images following this format: AnimalID_Condition_Slide_Slice_Side(R/L).tif

3. Generate ROIs (if you use the full image above, still follow the split of the channels). Draw ROIs in the image, split the channels, and save them appending this information in the file name:
AnimalID_Condition_Slide_Slice_Side(R/L)_ROI_Channel.tif

### NEW IMPLEMENTATION:
All of the above is implemented through two scripts to automatize the process. 
These scripts can be found in repository Fiji_Custom.
They are CZI_SlideScanner_ROIsubdivider.py and Group_convert_and_enhance.py

# For Rabies-cFos quantification
This pipeline aims to quantify the relative (to the full image) c-Fos staining in each cell infected with rabies.
## step 1
Take confocal images (current specifications below) of your rabies channel and your c-Fos channel.
Resolution:  0.9240 pixels per micron
Pixel size: 1.0823x1.0823 micron^2
Objective used in SP8: 10x AIR
Bits per pixel: 8 (grayscale LUT)
## step 2
Run CropLIF.ijm in FijiMacros. This will:
-Crop your images (pair always the two channels) to the region of interest and save the channels separately using this format:
MouseID_StarterCells_cFosCondition_SlideSliceNumber_SideoftheBrain_channel.tif (channel being 'cFos' or 'rabies').
-Save them in a specific folder
## step 3
Run IlastikProjects/RabiesContentQuantification.ilp and load your ...rabies images. Check that it classifies it correctly and retrain if needed. Save the outputs in a separate folder (e.g. IlastikOutput/) following these guidelines: https://github.com/CellProfiler/CellProfiler/wiki/How-to-use-Pixel-Classification-in-CellProfiler
## step 4
Run FijiMacros/GroupPercentileThresholding.py in Fiji to threshold the cFos channel.
## step 5
Run CellProfilerProtocols/RabiesContentQuantification.cpproj to get the tables.
Here, drag the main folder to the Images field (first), and specify which percentile is low, med and high (NamesAndTypes)
Change the input and output folders to the main directory in 'View output settings'
## step 6
Activate conda environment imageanalysis [TODO: create requirements]
Run jupyter notebook
