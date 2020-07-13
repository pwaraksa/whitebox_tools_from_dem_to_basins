#Script by john Lindsey, William Lidberg, Kim Lindgren and Anneli Ågren
from __future__ import print_function
import threading
import time
import os
import sys

sys.path.insert(1, r'D:\\WAMBAF\\WhiteboxTools_win_amd64\WBT') #This is where whitebox tools is located on my computer

from whitebox_tools import WhiteboxTools

#wb_dir = os.path.dirname('V:/JohannesLarson/WhiteboxTools_win_amd64/WBT/') #This is where whitebox tools is located on my computer
wb_dir = os.path.dirname('D:\\WAMBAF\\WhiteboxTools_win_amd64\WBT\\')

wbt = WhiteboxTools()
wbt.set_whitebox_dir(wb_dir)

#input folders
#DEM = 'Z:/RIP_WAM/TLW/newProcessing/BreachedDEM/'

#data1
DEM = 'G:/wambaf_06_2020/FeatureExtraction/Breached/'

#RASTERSTREAMS_4ha = 'Z:/RIP_WAM/TLW/newProcessing/RasterStreams/4ha/'

RASTERSTREAMS_4ha = 'G:/wambaf_06_2020/FeatureExtraction/rasterstreams/5ha'

#Output folders



#SLOPE = 'Z:/RIP_WAM/TLW/newProcessing/DTW/SLOPE/' #Gallant, J. C., and J. P. Wilson, 2000, Primary topographic attributes, in Terrain Analysis: Principles and Applications, edited by J. P. Wilson and J. C. Gallant pp. 51-86, John Wiley, Hoboken, N.J.
#SLOPERADIAN = 'Z:/RIP_WAM/TLW/newProcessing/DTW/SLOPERADIAN/'
#SLOPETAN = 'Z:/RIP_WAM/TLW/newProcessing/DTW/SLOPETAN/'

#DTW4ha = 'Z:/RIP_WAM/TLW/newProcessing/DTW/DTW4ha/'
#BACKLINK4 = 'Z:/RIP_WAM/TLW/newProcessing/DTW/BACKLINK/4ha/' #this is will not be used.

# path_output = 'F:/WAMBAF_19.06.2020/data/skrypt10'

path_output = 'F:/WAMBAF_19.06.2020/data/skrypt10_test'


SLOPE = path_output + '/DTW/SLOPE/' #Gallant, J. C., and J. P. Wilson, 2000, Primary topographic attributes, in Terrain Analysis: Principles and Applications, edited by J. P. Wilson and J. C. Gallant pp. 51-86, John Wiley, Hoboken, N.J.
SLOPERADIAN = path_output + '/DTW/SLOPERADIAN/'
SLOPETAN = path_output + '/DTW/SLOPETAN/'

DTW4ha = path_output + '/DTW/DTW4ha/'
BACKLINK4 = path_output + '/DTW/BACKLINK/4ha/' #this is will not be used.


maxThreads = 1 #Most of these operations are already parallized within whitebox tools. Starting multiple processes here will only slow down the processing time.

activeThreads = 0 #Don't change this.
def callback(out_str):
    ''' Create a custom callback to process the text coming out of the tool.
    If a callback is not provided, it will simply print the output stream.
    A custom callback allows for processing of the output stream.
    '''
    try:
        if not hasattr(callback, 'prev_line_progress'):
            callback.prev_line_progress = False
        if "%" in out_str:
            str_array = out_str.split(" ")
            label = out_str.replace(str_array[len(str_array) - 1], "").strip()
            progress = int(
                str_array[len(str_array) - 1].replace("%", "").strip())
            if callback.prev_line_progress:
                print('{0} {1}%'.format(label, progress), end="\r")
            else:
                callback.prev_line_progress = True
                print(out_str)
        elif "error" in out_str.lower():
            print("ERROR: {}".format(out_str))
            callback.prev_line_progress = False
        elif "elapsed time (excluding i/o):" in out_str.lower():
            elapsed_time = ''.join(
                ele for ele in out_str if ele.isdigit() or ele == '.')
            units = out_str.lower().replace("elapsed time (excluding i/o):",
                                            "").replace(elapsed_time, "").strip()
            print("Elapsed time: {0}{1}".format(elapsed_time, units))
            callback.prev_line_progress = False
        else:
            if callback.prev_line_progress:
                print('\n{0}'.format(out_str))
                callback.prev_line_progress = False
            else:
                print(out_str)

    except:
        print(out_str)

class workerThread(threading.Thread):
    def __init__(self, indata):
        threading.Thread.__init__(self)
        self.file = indata

    def run(self):
        global activeThreads
        activeThreads += 1

        #################################
        ##### Start here #####
        #################################

        global DEM
        global RASTERSTREAMS_4ha
        global DTW4ha
        global SLOPE
        global SLOPERADIAN
        global SLOPETAN
        global BACKLINK4

        wbt = WhiteboxTools()
        wbt.set_whitebox_dir(wb_dir)

        #Slope Degree
        inputdem = DEM + self.file
        slopedegrees = SLOPE + self.file
        args1 = ['--dem=' + inputdem, '--output=' + slopedegrees]

        #DTW uses a cost distance function with the stream as a source and slope as cost. the slope needs to be the mathematical slope and not slope in degrees.
        radians = SLOPERADIAN + self.file
        args2 = ['--input=' + slopedegrees, '--output=' + radians]
        slopetangens = SLOPETAN + self.file
        args3 = ['--input=' + radians, '--output=' + slopetangens]

        #DTW4ha
        streams = RASTERSTREAMS_4ha + self.file
        dtw4ha = DTW4ha + self.file.replace('.dep', '.tif') #if you have .dep as input and want .tif as output you can use self.file.replace('.dep', '.tif')
        backlink4ha = BACKLINK4 + self.file
        args4 = ['--source=' + streams, '--cost=' + slopetangens, '--out_accum=' + dtw4ha, '--out_backlink=' + backlink4ha]

        try:

            wbt.run_tool('Slope', args1, callback)
            wbt.run_tool('ToRadians', args2, callback)
            wbt.run_tool('tan', args3, callback)

            #Cost distance is the final step of DTW
            wbt.run_tool('CostDistance', args4, callback) #DTW 4ha

        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise
        #################################
        ##### end here #####
        #################################

        activeThreads -= 1

for inputfile in os.listdir(DEM):
    if inputfile.endswith('.dep'): #change this to .dep if you have .dep files.
        worker = workerThread(inputfile).start()

    while activeThreads >= maxThreads:
        pass

input('Script complete enter to close')
