This is a pipeline to visualize and analyze the results of CellProfiler on RNAscope experiments.

1. Take images in the SP8. Individual or tiled, doesn't matter. Do a z-stack and in Fiji make a maximum projection.
2. Split the channels and save them individually, with their default Fiji-titles (But removing spaces in the name!), in the folder where to do the quantification.
3. Copy the Cell-profiler project file in the CellProfilerProtocols folder into the same directory.
4. Modify the project to work with your images, and change the two output saving paths.
5. Run it. It should produce a .csv file with the statistics, and an overlay image summarizing the results.
6. Run jupyter notebook ==== in RNAscope-CellProfiler in github (CHANGE THE NAME!).

