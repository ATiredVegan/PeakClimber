#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:53:58 2024

@author: jderrick
"""

import peakclimber
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib
from idlelib.tooltip import Hovertip
from sys import exit
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.backends.backend_tkagg as tkagg
#from matplotlib.figure import Figure
from tkinter import filedialog
file_path=''
start_time=0
end_time=40


class ScrollTree(ttk.Treeview):
    def __init__(self, master, *args, **kwargs):
        ttk.Treeview.__init__(self, master, *args, **kwargs)

        sb = tk.Scrollbar(master, orient='vertical', command=self.yview) # Create a scrollbar
        sb.grid(row=0, column=1, sticky='ns')
        self.config(yscrollcommand=sb.set)

sample_name=''
def import_file(sample_name,window):
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:

        hplc=[]
        if sample_name=='':
            last_index=str(file_path).rfind('/')
            sample_name=str(file_path)[last_index+1:]
        hplc+=peakclimber.make_entry(file_path,{"Name":sample_name})
        hplc_df=pd.DataFrame(hplc)
        x=hplc_df.loc[(hplc_df['Name']==sample_name)]['Time']
        y=hplc_df.loc[(hplc_df['Name']==sample_name)]['Value']
        figure = plt.Figure(figsize=(15,5), dpi=100)
        canvas = FigureCanvasTkAgg(figure, window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column=0) #fill='both', expand=True)

        toolbar=tkagg.NavigationToolbar2Tk(canvas, window,pack_toolbar=False)
        toolbar.grid(row=1,column=0)



             
        ax=figure.add_subplot(111)
        ax.clear()
        ax.plot(x,y)
        ax.set_title(sample_name+ " Chromatograph")
        new_entry = tk.Frame(master=window)
        new_entry.grid(row=2, column=0, padx=10)
        start_timer= tk.Entry(master=new_entry,width=10)
        

        lbl_start = tk.Label(master=new_entry, text="Start time:")

        lbl_start.grid(row=0, column=0, sticky="w")
        start_timer.grid(row=0, column=1, sticky="w")
        end_timer= tk.Entry(master=new_entry,width=10)
        

        lbl_end = tk.Label(master=new_entry, text="End time:")

        lbl_end.grid(row=0, column=2, sticky="w")
        end_timer.grid(row=0, column=3, sticky="w")
        update_button = tk.Button(master=new_entry, text="Update", command=lambda:[update_graph(start_timer.get(),end_timer.get(),hplc_df,sample_name,ax,canvas,window),clear(new_entry)])
        update_button.grid(row=0,column=4)
        
    else:
        close(window)

def update_graph(start,end,hplc_df,sample_name,ax,canvas,window): 
    start_time=float(start)
    end_time=float(end)

    
    
    x=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time)& (hplc_df['Name']==sample_name)]['Time']
    y=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time)& (hplc_df['Name']==sample_name)]['Value']

    z=peakclimber.remove_noise(y,2000,1e10,20)
    df = pd.DataFrame()
    df["Time"]=x
    df["Value"]=z


    
    
    ax.clear()
    
    ax.plot(x,y)
    ax.set_title(sample_name+ " Chromatograph")

    canvas.draw()
    prominenceheight = tk.Frame(master=window)
    prominenceheight.grid(row=2, column=0, padx=10)
    prom= tk.Entry(master=prominenceheight,width=10)
    prom.insert(0, '0.05')

    lbl_prom = tk.Label(master=prominenceheight, text="Prominence (default 0.05):")
    Hovertip(lbl_prom,"Prominence  measures the height of a mountain or hill's summit relative to the lowest contour line \n encircling it but containing no higher summit within it. The measure here is as of a percentage of the largest peak. \n Peaks that do not meet the prominence requirement are excluded from the analysis")

    lbl_prom.grid(row=0, column=0, sticky="w")
    prom.grid(row=0, column=1, sticky="w")
    hei= tk.Entry(master=prominenceheight,width=10)
    hei.insert(0, '1')
    

    lbl_hei = tk.Label(master=prominenceheight, text="Height (default 1):")
    Hovertip(lbl_hei,"Minimum height for a peak to be included in the analysis")

    lbl_hei.grid(row=0, column=2, sticky="w")
    hei.grid(row=0, column=3, sticky="w")
    peaks = tk.Button(master=prominenceheight, text="Identify Peaks", command=lambda:[find_peaks(x,z,start,end,hplc_df,hei.get(),prom.get(),ax,canvas,window),clear(prominenceheight)])
    peaks.grid(row=0,column=4)
    print(window.grid_slaves())

    
def find_peaks(x,z,start,end,hplc_df,height,prominence,ax,canvas,window):
    height=float(height)
    prominence=float(prominence)

    ax.clear()
    time,heights=peakclimber.find_locations_peaks(x, z, prominence, height,graph=True,ax=ax)
    canvas.draw()

    onward= tk.Frame(master=window)
    prominenceheight = tk.Frame(master=window)
    settings =tk.Frame(master=window)
    prominenceheight.grid(row=2, column=0, padx=10)
    onward.grid(row=3,column=0, padx=10)
    settings.grid(row=4,column=0,padx=10)
    prom= tk.Entry(master=prominenceheight,width=10)
    prom.insert(0, '0.05')
    

    lbl_prom = tk.Label(master=prominenceheight, text="Prominence (default 0.05):")
    Hovertip(lbl_prom,"Prominence  measures the height of a mountain or hill's summit relative to the lowest contour line \n encircling it but containing no higher summit within it. The measure here is as of a percentage of the largest peak. \n Peaks that do not meet the prominence requirement are excluded from the analysis")


    lbl_prom.grid(row=0, column=0, sticky="w")
    prom.grid(row=0, column=1, sticky="w")
    hei= tk.Entry(master=prominenceheight,width=10)
    hei.insert(0, '1')
    

    lbl_hei = tk.Label(master=prominenceheight, text="Height (default 1):")
    Hovertip(lbl_hei,"Minimum height for a peak to be included in the analysis")
    lbl_hei.grid(row=0, column=2, sticky="w")
    hei.grid(row=0, column=3, sticky="w")
    
    lbl_variation=tk.Label(master=settings, text="Center variation")
    Hovertip(lbl_variation,"How much peak center is allowed to vary from the identified value")
    variation=tk.Entry(master=settings,width=10)
    variation.insert(0,'0.1')
    variation.grid(row=0,column=1)
    lbl_variation.grid(row=0,column=0)
    
    lbl_gmin=tk.Label(master=settings, text="Gamma Min")
    Hovertip(lbl_gmin,"Minimum value of skew term (default 0.1)")
    gmin=tk.Entry(master=settings,width=10)
    gmin.insert(0,'0.1')
    gmin.grid(row=0,column=3)
    lbl_gmin.grid(row=0,column=2)
    
    lbl_gmax=tk.Label(master=settings, text="Gamma Max")
    Hovertip(lbl_gmax,"Maximum value of skew term (default 5)")
    gmax=tk.Entry(master=settings,width=10)
    gmax.insert(0,'5')
    gmax.grid(row=1,column=3)
    lbl_gmax.grid(row=1,column=2)
    
    lbl_gcen=tk.Label(master=settings, text="Gamma default")
    Hovertip(lbl_gmax,"Initial gamma value for fit optimization (overrides default)")
    gcen=tk.Entry(master=settings,width=10)
    gcen.insert(0,'1')
    gcen.grid(row=2,column=3)
    lbl_gcen.grid(row=2,column=2)
    
    
    lbl_smin=tk.Label(master=settings, text="Sigma Min")
    Hovertip(lbl_smin,"Minimum value of peak width (defualt 0.01 min)")
    smin=tk.Entry(master=settings,width=10)
    smin.insert(0,'0.01')
    smin.grid(row=0,column=5)
    lbl_smin.grid(row=0,column=4)
    
    lbl_smax=tk.Label(master=settings, text="Sigma Max")
    Hovertip(lbl_smax,"Maximum value of peak width (default 1)")
    smax=tk.Entry(master=settings,width=10)
    smax.insert(0,'1')
    smax.grid(row=1,column=5)
    lbl_smax.grid(row=1,column=4)
    
    lbl_scen=tk.Label(master=settings, text="Sigma Center")
    Hovertip(lbl_smax,"Initial sigma value for fit optimization (overrides default)")
    scen=tk.Entry(master=settings,width=10)
    scen.insert(0,'0.1')
    scen.grid(row=2,column=5)
    lbl_scen.grid(row=2,column=4)
    
    peaks = tk.Button(master=prominenceheight, text="Reidentify Peaks", command=lambda:[find_peaks(x,z,start,end,hplc_df,hei.get(),prom.get(),ax,canvas,window),clear(prominenceheight)])
    peaks.grid(row=0,column=4)
    var1=tk.IntVar()
    var2=tk.IntVar()
    check=tk.Checkbutton(master=onward,variable=var1, text="Graph text",onvalue=1,offvalue=0)
    Hovertip(check,"To include peak centers on graph or not")
    front=tk.Checkbutton(master=onward,variable=var2, text="Fronted Peaks?",onvalue=-1,offvalue=1)
    front.deselect()
    Hovertip(front,"fronted peaks. Makes all gamma values negative")
    fit=tk.Button(master=onward,text="Fit Peaks",command=lambda:[clear(prominenceheight),fit_peaks(x,z,start,end,time,heights,hplc_df,sample_name,ax,canvas,window,var1.get(),variation.get(),gmin.get(),gmax.get(),gcen.get(),smin.get(),smax.get(),scen.get(),var2.get()),clear(onward),clear(settings)])
    check.grid(row=0,column=0)
    front.grid(row=0,column=1)
    fit.grid(row=0,column=2)

    
def fit_peaks(x,y,start,end,time,heights,hplc_df,sample_name,ax,canvas,window,text,variation,gmin,gmax,gcen,smin,smax,scen,fronted):
    variation=float(variation)
    areas=[]
    #find peak windows to improve runtime 
    windows=peakclimber.find_peak_windows(x,y,time,heights,float(start),float(end))
    df=pd.DataFrame()
    df['Time']=hplc_df.loc[(hplc_df['Time']>=float(start)) & (hplc_df['Time']<=float(end))]['Time']
    df['y']=hplc_df.loc[(hplc_df['Time']>=float(start)) & (hplc_df['Time']<=float(end))]['Value']
    df['denoised_y']=peakclimber.remove_noise(y, band_limit=2000,lamba=1e10,smoothing=20, sampling_rate=500)



    #goes through each window and finds area for each 
    for widow in windows:

        locs=widow[0]
        heights=widow[1]
        bounds=widow[2]
        sub_x=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['Time']
        sub_y=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['denoised_y']
        area=peakclimber.model_n_expgaus(sub_x,sub_y,len(locs),locs,heights,peak_variation=variation,gamma_min=float(gmin)*fronted,gamma_max=float(gmax)*fronted,gamma_center=fronted*float(gcen),sigma_min=float(smin),sigma_max=float(smax),sigma_center=float(scen))
        areas+=area
    


    
    ax.clear()
    peakclimber.graph_n_expgaus(x,y,len(areas),areas,sample_name,ax=ax,add_text=text)
    
    canvas.draw()
    locs=[]
    f_areas=[]
    for peak in areas:
        locs.append(peak[0])
        f_areas.append(peak[4])
    
    saver=tk.Frame(master=window)
    saver.grid(row=2,column=0)
    save_button = tk.Button(master=saver, text="Save Fit", command=lambda:[clear(saver),save(locs,f_areas),clear(tree_frame)])
    save_button.grid(row=0,column=0)
    
    tree_frame = tk.Frame(window)
    tree_frame.grid(row=3,column=0)

    columns = ['Retention Time','Area'] # List of column names for all the columns of the data
    tree = ScrollTree(tree_frame, columns=columns, show='headings')
    tree.grid(row=0, column=0)

    for col in columns:
        tree.heading(col, text=col, anchor='center') # Add a heading in the given `col` as ID
        tree.column(col, anchor='center') # Properties for the column with `col` as ID

    for i in range(0,len(locs)):
        tree.insert('','end',values=(str(round(locs[i],3))+' '+str(round(f_areas[i],3))))


    

def save(locs,f_areas):
    
    output_list=[]
    for peak_n in range(0,len(locs)):
        output_dic={"Retention Time":locs[peak_n],"Peak Area":f_areas[peak_n]}
        output_list.append(output_dic)
    df_for_export=pd.DataFrame(output_list)
    SAVING_PATH = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    df_for_export.to_csv(SAVING_PATH)
    
    filer=tk.Frame(master=window)
    filer.grid(row=2,column=0)
    
    new_file=tk.Button(master=filer,text="New File?",command=lambda:[clear(window),import_file('',window)])
    exiter=tk.Button(master=filer,text="Exit?",command=lambda:[close(window)])
    new_file.grid(row=0,column=0)
    exiter.grid(row=0,column=1)
    
    
    
def clear(level):

    liste = level.grid_slaves()
    for l in liste:
        l.destroy()      
 
def close(window):
    window.destroy()   
    exit()

window = tk.Tk()
window.title("PeakClimber")
window.geometry("1500x1000")
s=ttk.Style()
s.theme_use('clam')
frm_entry = tk.Frame(master=window)
frm_entry.grid(row=0, column=0, padx=10)
sample_namer= tk.Entry(master=frm_entry,width=10)

lbl_name = tk.Label(master=frm_entry, text="Sample name:")

lbl_name.grid(row=0, column=0, sticky="w")
sample_namer.grid(row=0, column=1, sticky="w")
import_button = tk.Button(master=frm_entry, text="Import File", command=lambda:[import_file(sample_namer.get(),window),clear(frm_entry)])
import_button.grid(row=4,column=0)

window.mainloop()


   


