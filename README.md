# How to use *PeakClimber* to analyze HPLC traces

* Written for someone with no experience with bash script or python

# Goal:
To provide step-by-step command line instructions for the average user to analyze HPLC chromatographs

# Materials:

1.	After the HPLC run, appropriately name each trace. Move your data to a proper storage location (Data backup, server, Cloud service, etc.)
2.	Copy your data folder to your Desktop to work locally from now on.
a.	Making an additional copy of the HPLC traces folder on the Desktop can make navigating to the data via terminal more efficient
3.	Download gui_main.py, peakclimber.py, requirements.txt, and setup.sh from https://github.com/ATiredVegan/PeakClimber
4.	After download, place gui_main.py, peakclimber.py, requirements.txt, and setup.sh in the same Desktop folder as your HPLC traces
a.	For this example, I am analyzing 4 samples (labeled 1, 2, 5, and 6)


<img width="416" alt="image" src="https://github.com/user-attachments/assets/9a716257-932c-4059-80a6-aa6111bdb4de" />
  
Figure 1: Screenshot of HPLC traces folder on local Desktop containing Python scripts and data

# Methods:

1.	Open terminal from Applications > Terminal 
a.	Terminal is the window in which you enter commands into the computer to process
b.	ctrl + alt + “t” will also open the terminal application quickly on a PC; command + “t” will open a new Terminal window on a Mac

<img width="484" alt="image" src="https://github.com/user-attachments/assets/2ea36c60-5b05-4fda-8a7d-874091da5fcd" />

Figure 2: Screenshot of the Terminal application window upon opening.

2. Make sure you have Python and pip installed to run this package. You will want to install python by downloading version 3.12.7 from this link (https://www.python.org/downloads/release/python-3127/). Once you have python installed, run the following command to install pip

> python -m pip install --upgrade pip


3.	In terminal, navigate to your data using cd commands:
			
>cd ~/Desktop
>
>cd Ludington_Lab/PeakClimber/src/package_1



<img width="222" alt="image" src="https://github.com/user-attachments/assets/23a0fc90-18eb-43d1-8cbe-780eb5e3b819" />

Figure 3: Screenshot of Terminal to navigate to HPLC data folder and listing out the contents of the folder. 

4. Install all dependencies. Run the bash script setup.sh by typing. You only need to do this once.

> bash setup.sh 



5. Now that you’re in your data folder, you can run PeakClimber!

>python gui_main.py

<img width="472" alt="image" src="https://github.com/user-attachments/assets/5071ab0b-acbe-4d7b-ab16-eb624c149e03" />


Figure 4: Screenshot of Terminal to run PeakClimber.

5.	Once you hit “enter”, a new window should pop up that looks like this:

<img width="355" alt="image" src="https://github.com/user-attachments/assets/563edc50-37eb-4581-90f5-cc0fae49104b" />
 
Figure 5: Screenshot of PeakClimber user interface to upload data.

a.	It is not necessary to enter anything into the sample name box. If you do, future saved files (spreadsheets/graphs) will start with this name. If you do not wish to name your files now, simply click “import file” to upload your first HPLC sample.

b.	How do I know which file to choose from? If you’re interested in the fluorescent signal, you’ll open Emission.txt files. If you’re interested in total lipids (non-fluorescent), you’ll import the CAD file for that sample.

6.	Once you import your first data file, PeakClimber will load the trace in this window (Figure 6):

<img width="488" alt="image" src="https://github.com/user-attachments/assets/6ae0a0f6-94ea-4e73-b89b-77616b1667dc" />
 
Figure 6: Screenshot of the first data trace loaded into PeakClimber

7.	Select the time range of the trace that you would like to analyze.
   
a.	For this trace, I’m most interested in quantifying peaks between 5 min and 50 min

b.	Watch how the x-axis changes in the window below to focus on the specified time window/peaks of interest (Figure 7). 

<img width="502" alt="image" src="https://github.com/user-attachments/assets/47b87d24-c722-4216-ab38-390f132e1659" />
 
Figure 7: Screenshot of HPLC trace cropped to the region of 5 min to 50 min as specified by the user. 

8.	Now, identify peaks by changing the default prominence and height values.
   
a.	In Figure 8, I used the default values for prominence and height and then I ran “identify peaks.”

b.	Prominence is the minimum distance between a peak and the nearest valley. Height is the minimum peak height that will be counted. These values can be changed as many times as you like until you are satisfied with the identified peaks. 

<img width="510" alt="image" src="https://github.com/user-attachments/assets/715ace42-9e5e-4290-a583-2aeffce4c07e" />
 
Figure 8: Screenshot of HPLC trace cropped to the selected time region. Peak centers are identified by blue dots in the graph legend. 

<img width="344" alt="image" src="https://github.com/user-attachments/assets/970ab0de-f09c-478d-bb1f-9fd14c464732" />
 
Figure 8.1: Screenshot of blank window labeled Figure 1 that may pop up. Close just this window to continue identifying peaks on your trace. This is a known bug!

9.	On the next screen you will have a list of parameters options as shown in Figure 9. The only two options you should worry about initially are the Graph text and Fronted peaks. The former controls if you have text on your graphs (peak retention times), the later controls if your tail for ALL PEAKS is before or after the peak center. Unfortunately, there is an undefined region of the BEMG function around 0, so PeakClimber currently can only fit fronted or tailed peaks, but not a mixture. The other parameters control your fit: you should leave these as the default unless you are not satisfied with the quality of the fit (more in the FAQ below). 
  
<img width="540" alt="image" src="https://github.com/user-attachments/assets/aea31c73-db17-451b-bc86-1a0315216002" />

Figure 9: Parameter options for your fit. The checkboxes control if you see text on your graphs, or if you fit to a fronted peak rather than a traditionally tailed peak. The other options control the parameters that you will use for your fit.


10.	When each peak is identified with a peak center, and you are happy with the parameter options, choose “Fit peaks.”
 
<img width="451" alt="image" src="https://github.com/user-attachments/assets/b2a6e335-fe27-45e4-b57c-8f23c24d5884" />

Figure 10: Screenshot of the fit peaks of the HPLC trace displaying the fit: the underlying trace is present in orange, the overall fit in blue, and the subcomponents are the shaded regions. The areas and runtimes of each peak are shown in a table below the trace image. 

11.	Choose “save fit” to save the data to a csv file.
    
a.	PeakClimber will prompt you to name this .csv file and you can save it in the same folder as you the original HPLC traces.

b.	Only the data table is saved, not an image of the trace. The data exported is retention time and peak height.

c.	You can save the current view of the trace by hitting the save symbol in the toolbar below the graph. 

d.	Do not rely on copying the raw data table from this window. When analyzing multiple HPLC traces, avoid aggregating lots of csv files by copying and pasting each data table into one Excel spreadsheet. It is possible to highlight all the values in the table by clicking on the first row, then, while holding down the “shift” key (for Mac or for PC) scroll to click on the last value. However, command + “c” will not copy these values to your clipboard. 


12.	To analyze the next trace, choose “New File?” which will take you back to the import file interface in Figure 5. 
<img width="312" alt="image" src="https://github.com/user-attachments/assets/c806b48a-6de8-47c8-95b1-0780d73b6bfb" />
 
Figure 11: Screenshot of the interface to load your next trace or exit PeakClimber. 

12.	Once you have fit the peaks for each of the HPLC traces and properly saved the data, your HPLC data folder should now contain .csv files for each sample.

<img width="409" alt="image" src="https://github.com/user-attachments/assets/cfb92016-dcbd-47e8-bccb-5a9c40655877" />
 
Figure 12: Screenshot of Terminal listing contents of HPLC_Intestines working directory. Here, I saved .csv files for peaks quantified from the Emission signal and from the CAD signal. 
 


# FAQ: 

1.	**PeakClimber is Identifying too many/too few peaks. How do I fix this?**
     
>The easiest thing to do is adjust the height and prominence cutoffs until you are satisfied with the identified peaks. If you are unable to correctly identify peaks across the whole graph, try subdividing the graph into regions where you can home in on specific height/prominence cutoffs 

2.	**I’m not happy with the fits. What do I do?**
   
> The fit depends a lot on the parameter space as well as the initial parameters used. Although there should be one optimal solution, the non-linear optimization will often stop before it has arrived at the “optimal solution”, leaving the user with a suboptimal fit. To combat this, I would recommend changing the parameters in the following ways depending on the issues that you are having: 

> a.	**Peaks are generally too wide**: decrease sigma max and sigma default. 

> b.	**Peaks are generally too narrow**: decrease sigma max and sigma default. 

> c.	**Tail is too long**: increase gamma min and gamma default.

> d.	**Large regions of the graph are not covered by the fit**: you may be missing peaks (decrease your prominence and height cutoffs). Another solution could be to increase the default tail size by decreasing gamma default and decreasing gamma min. 

4.	**I want to find the peak areas of a trace with both fronted and tailed peaks**

> If the fronted/tailed peaks are independent of one another, you can fit different regions of the trace using different options for the fronted peaks checkbox (on for fronted regions, off for tailed regions). Unfortunately, PeakClimber does not currently support fits of regions with both fronted and tailed peaks due to constraints in the optimization algorithm. 






Resources:

https://github.com/ATiredVegan/PeakClimber




