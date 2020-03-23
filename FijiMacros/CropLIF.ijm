// Hernando Martinez
// October 2019

// This macro scans a directory, select .lif files, and open the contents one by one so the user
// can crop the images and it saves them automatically, splitting the channels into rabies and cfos


run("Close All");
// choose directory
inputdir = getDirectory("Choose a Directory");

// Find .lif files
files = getFileList(inputdir);
liffiles = newArray();
for (j=0; j < files.length; j++){
	if (endsWith(files[j],".lif")){
		liffiles = Array.concat(liffiles,files[j]);
	}
}

// If files are found create output directory if it does not exist
File.makeDirectory(inputdir+"DataForAnalysis");
outdir = inputdir+"DataForAnalysis/PulledCroppedImages/";
File.makeDirectory(outdir);
// get the list of images processed already
previously_processed = getFileList(outdir);

for (j = 0; j < liffiles.length; j++) {
	print(liffiles[j]);
	liffilepath = inputdir + liffiles[j];
	//open files
	FILE_PATH = liffilepath;
	run("Bio-Formats Macro Extensions");
	Ext.setId(FILE_PATH);
	Ext.getSeriesCount(SERIES_COUNT);
	SERIES_NAMES=newArray(SERIES_COUNT);
	print("Number of images: "+SERIES_COUNT);
	    
	// Loop on all series in the file
	for (i=0; i<SERIES_COUNT; i++) {       
	    // Get serie name and channels count
	    Ext.setSeries(i);
	    Ext.getEffectiveSizeC(CHANNEL_COUNT);
	    SERIES_NAMES[i]="";
	    Ext.getSeriesName(SERIES_NAMES[i]);
	    //TEMP_NAME=toLowerCase(SERIES_NAMES[i]);
	    rawtit = SERIES_NAMES[i];
	    // do nothing if this image has been processed already
	    if(checkIfProcessed(rawtit+"_rabies.tif", previously_processed)){
	    	print(rawtit + " processed already");
	    }
	    else{        
		    run("Bio-Formats Importer", "open=["+ FILE_PATH + "] " + "view=[Hyperstack]" + " stack_order=Default series_" + i+1);
		    rename(rawtit);
		    // make composite
		    Stack.setDisplayMode("composite");
		    run("Enhance Contrast", "saturated=0.35");
		    // draw a rectangle and wait for the user so the image gets cropped
		    makeRectangle(5, 5, getWidth-10, getHeight-10);
		    title = "WaitForUser";
	  		msg = "select area to crop the image";
	  		waitForUser(title, msg);
		    run("Crop");
		    // split channels and save
		    run("Split Channels");
		    selectWindow("C1-"+rawtit);
		    run("Grays");
		    ImageName = rawtit+"_rabies.tif";
			saveAs("Tiff", outdir +"/"+ ImageName);
			close(ImageName);
			
			selectWindow("C2-"+rawtit);
		    run("Grays");
		    ImageName = rawtit+"_cFos.tif";
			saveAs("Tiff", outdir +"/"+ ImageName);
			close(ImageName);
	    }
	}
}

function checkIfProcessed(string,array){
	val = 0;
	for (i = 0; i < array.length; i++) {
		if (array[i] == string){
			val = 1;
		}
	}
	return(val);
}
