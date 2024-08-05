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

I have attached two python files to this email: peakclimber.py and main.py. You do not need to touch peakclimber.py at all. These two files need to stay in the same folder 

1.	In a terminal window, using cd, navigate to the location of peakclimber and your data using the cd command. 
2.	Once in the correct folder type python main.py. This will initiate the peakclimber program 
3.	Peakclimber will then ask you for a filename, sample name, and start and end points for analysis. Once provided, the program will generate two graphs. You need to close these windows in order for the program to proceed. 
4.	Once finished you should see two output files in the same folder: a graph showing the fit and a csv file with the fit statistics of each peak (center and area). 
5.	The program will then ask you if you want to run another file. To proceed type y or yes. The command n or no will exit the program. 

I’ve attached a text file that works on my machine. Please reach out if you have any issues. 
