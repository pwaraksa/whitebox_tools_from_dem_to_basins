import os

#This is where all the clipped raster files are saved.
FolderWithDEMs = 'F:\data2'
#clipped Streams.
FolderWithStreams = 'F:\data2\SplittedFeature\SplitRivers'
#Clipped Roads.
FolderWithRoads = 'F:\data2\SplittedFeature\SplitRoads'
#This is the output folder where the burned DEMs will be saved.
OutputFolder = 'F:\data2\SplittedFeature\BurnStreamsAtRoads'
#Maximum breach distance
MaximumBreachDistance = '50'
#This loop will find all files that ends with .dep and join them to their path
#First make a empty list
ListOfArguments = []

#Then look for .dep files in the folderwithfiles 
for root, dirs, files in os.walk(os.path.abspath(FolderWithDEMs)):
    for file in files:
        if file.endswith('.dep'):
            ListOfArguments.append(os.path.join(FolderWithDEMs, file + ', '+
            os.path.join(FolderWithStreams, file.replace('.dep', '.shp')+ ', ' +
            os.path.join(FolderWithRoads, file.replace('.dep', '.shp') + ', ' +
            os.path.join(OutputFolder, file + ', ' + MaximumBreachDistance)))))

#Save list to text file that whitebox GAt can read.            
with open('Arguments_BurnStreamsAtRoads2.txt','w')as output:
    output.write('\n'.join(ListOfArguments))

