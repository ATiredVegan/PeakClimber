# PeakClimber
To use this piece of software you will need to have python 3 installed on your machine, as well as the following packages

matplotlib (version 3.7.1)
numpy (version 1.24.3)
pandas (version 1.5.3)
seaborn (version 0.12.2)
pybaselines (version 1.0.0)
scipy (version 1.9.3)
lmfit (version 1.0.3)

You can use pip or conda to install any of these packages. 

Usage: 

Setup: Your data should be in the form of txt files. These can be exported directly from chromeleon and other hplc/mass spec software. It will be convenient to have these files in the same folder, or within a subfolder, as the two python files. 

There are three python files and a bash script in this repository: peakclimber.py, gui_main2.py, and main.py. You do not need to touch peakclimber.py at all, and main.py is a command line version of PeakClimber if you feel like using it for some reason. These three files need to stay in the same folder 

1.	In a terminal window, using cd, navigate to the location of peakclimber using the cd command.
2.	Run the setup script by typing bash setup.sh. If you are following good coding practices you should create a new environment specifically for PeakClibmer, but if you don't know what I mean by this, it's not important. This script will install all the packages you need via pip 
3.	After you have installed the required packages sucessfully, you can run PeakClimber by typing python gui_main2.py
4.	Peakclimber will then open a new window and ask you for a sample name (defaults to filename if you put nothing in) and to import a file using the file browser
5.	The next screen will show you the raw chromatograph and then prompt you to select a region you would like to analyze.
6.	PeakClimber will next crop to the region you have selected, and prompt you for the parameters required for peak fitting. Height is the minimum peak height that will be counted as a peak, and prominence is the minimum distance between a peak and the nearest valley in order for the peak to be counted as real. You can change these on the next screen if you are unsatisifed with peak identification.
7.	The next screen shows the identified peaks as well as a denoised and detrended chromatograph. You can change the peak selection here if you are unsatisfied. Click fit peaks if you are satisfied 
8.	The final screen will display your fit: the underlying trace is present in orange, the overall fit in blue, and the subcomponents as the shaded regions. The areas and runtimes of each peak are shown below. You can save this chromatograph as text file or csv by hitting the save file button 
9.	The program will then ask you if you want to run another file or exit

I’ve attached two text files that works on my machine: one of three overlapping fatty acids, and another of a whole fly chromatograph. Please reach out if you have any issues. 
