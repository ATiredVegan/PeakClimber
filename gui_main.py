#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:53:58 2024

@author: jderrick
"""

import peakclimber
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib
from idlelib.tooltip import Hovertip
from sys import exit
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.backends.backend_tkagg as tkagg
from tkinter import filedialog
file_path=''
start_time=0
end_time=40


class ScrollTree(ttk.Treeview):
    def __init__(self, master, *args, **kwargs):
        ttk.Treeview.__init__(self, master, *args, **kwargs)
        sb = tk.Scrollbar(master, orient='vertical', command=self.yview)
        sb.grid(row=0, column=1, sticky='ns')
        self.config(yscrollcommand=sb.set)


sample_name=''
def import_file(sample_name, window):
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
        canvas.get_tk_widget().grid(row=0, column=0)

        toolbar=tkagg.NavigationToolbar2Tk(canvas, window, pack_toolbar=False)
        toolbar.grid(row=1, column=0)

        ax=figure.add_subplot(111)
        ax.clear()
        ax.plot(x, y)
        ax.set_title(sample_name + " Chromatograph")
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Signal")
        canvas.figure.tight_layout()
        canvas.draw()

        new_entry = tk.Frame(master=window)
        new_entry.grid(row=2, column=0, padx=10)
        start_timer = tk.Entry(master=new_entry, width=10)
        start_timer.insert(0, str(round(float(x.min()), 2)))

        lbl_start = tk.Label(master=new_entry, text="Start time:")
        lbl_start.grid(row=0, column=0, sticky="w")
        start_timer.grid(row=0, column=1, sticky="w")
        end_timer = tk.Entry(master=new_entry, width=10)
        end_timer.insert(0, str(round(float(x.max()), 2)))

        lbl_end = tk.Label(master=new_entry, text="End time:")
        lbl_end.grid(row=0, column=2, sticky="w")
        end_timer.grid(row=0, column=3, sticky="w")
        update_button = tk.Button(master=new_entry, text="Update", command=lambda:[update_graph(start_timer.get(),end_timer.get(),hplc_df,sample_name,ax,canvas,window),clear(new_entry)])
        update_button.grid(row=0, column=4)

    else:
        close(window)


def update_graph(start, end, hplc_df, sample_name, ax, canvas, window):
    try:
        start_time=float(start)
        end_time=float(end)
    except ValueError:
        messagebox.showerror("Invalid input", "Start and end times must be numbers.")
        return

    x=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time) & (hplc_df['Name']==sample_name)]['Time']
    y=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time) & (hplc_df['Name']==sample_name)]['Value']
    z=peakclimber.remove_noise(y, 2000, 1e10, 20)

    ax.clear()
    ax.plot(x, y)
    ax.set_title(sample_name + " Chromatograph")
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Signal")
    canvas.figure.tight_layout()
    canvas.draw()

    prominenceheight = tk.Frame(master=window)
    prominenceheight.grid(row=2, column=0, padx=10)
    prom = tk.Entry(master=prominenceheight, width=10)
    prom.insert(0, str(max(y)*0.01))

    lbl_prom = tk.Label(master=prominenceheight, text="Prominence (default 1% max height):")
    Hovertip(lbl_prom,"Prominence measures the height of a mountain or hill's summit relative to the lowest contour line \n encircling it but containing no higher summit within it. The measure here is as of a percentage of the largest peak. \n Peaks that do not meet the prominence requirement are excluded from the analysis")

    lbl_prom.grid(row=0, column=0, sticky="w")
    prom.grid(row=0, column=1, sticky="w")
    hei = tk.Entry(master=prominenceheight, width=10)
    hei.insert(0, str(max(y)*0.1))

    lbl_hei = tk.Label(master=prominenceheight, text="Height (default 1/10 max height):")
    Hovertip(lbl_hei,"Minimum height for a peak to be included in the analysis")

    lbl_hei.grid(row=0, column=2, sticky="w")
    hei.grid(row=0, column=3, sticky="w")
    peaks = tk.Button(master=prominenceheight, text="Identify Peaks", command=lambda:find_peaks(x,z,start,end,hplc_df,hei.get(),prom.get(),ax,canvas,window,prominenceheight))
    peaks.grid(row=0, column=4)


def find_peaks(x, z, start, end, hplc_df, height, prominence, ax, canvas, window, prominenceheight_frame=None):
    #checks to see if prominence and height are valid inputs 
    try:
        height=float(height)
        prominence=float(prominence)
    except ValueError:
        messagebox.showerror("Invalid input", "Height and prominence must be numbers.")
        return

    ax.clear()
    time,heights=peakclimber.find_locations_peaks(x, z, prominence, height, graph=True, ax=ax)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Signal")
    canvas.figure.tight_layout()
    canvas.draw()

    #if no peaks were found, return an error 
    if len(heights) == 0:
        messagebox.showwarning("No peaks found", "No peaks were identified with the current prominence and height settings. Try lowering the thresholds.")
        return

    # Only clear the calling frame now that we know peaks were found
    if prominenceheight_frame is not None:
        clear(prominenceheight_frame)

    onward = tk.Frame(master=window)
    prominenceheight = tk.Frame(master=window)
    settings = tk.Frame(master=window)
    prominenceheight.grid(row=2, column=0, padx=10)
    onward.grid(row=3, column=0, padx=10)
    settings.grid(row=4, column=0, padx=10)
    prom = tk.Entry(master=prominenceheight, width=10)
    prom.insert(0, str(prominence))

    lbl_prom = tk.Label(master=prominenceheight, text="Prominence (1% of max default height):")
    Hovertip(lbl_prom,"Prominence measures the height of a mountain or hill's summit relative to the lowest contour line \n encircling it but containing no higher summit within it. The measure here is as of a percentage of the largest peak. \n Peaks that do not meet the prominence requirement are excluded from the analysis")

    lbl_prom.grid(row=0, column=0, sticky="w")
    prom.grid(row=0, column=1, sticky="w")
    hei = tk.Entry(master=prominenceheight, width=10)
    hei.insert(0, str(height))

    lbl_hei = tk.Label(master=prominenceheight, text="Height (default 1):")
    Hovertip(lbl_hei,"Minimum height for a peak to be included in the analysis")
    lbl_hei.grid(row=0, column=2, sticky="w")
    hei.grid(row=0, column=3, sticky="w")

    lbl_variation=tk.Label(master=settings, text="Center variation")
    Hovertip(lbl_variation,"How much peak center is allowed to vary from the identified value")
    variation=tk.Entry(master=settings, width=10)
    variation.insert(0,'0.1')
    variation.grid(row=0, column=1)
    lbl_variation.grid(row=0, column=0)

    lbl_gmin=tk.Label(master=settings, text="Gamma Min")
    Hovertip(lbl_gmin,"Minimum value of skew term (default 0.1)")
    gmin=tk.Entry(master=settings, width=10)
    gmin.insert(0,'0.1')
    gmin.grid(row=0, column=3)
    lbl_gmin.grid(row=0, column=2)

    lbl_gmax=tk.Label(master=settings, text="Gamma Max")
    Hovertip(lbl_gmax,"Maximum value of skew term (default 5)")
    gmax=tk.Entry(master=settings, width=10)
    gmax.insert(0,'5')
    gmax.grid(row=1, column=3)
    lbl_gmax.grid(row=1, column=2)

    lbl_gcen=tk.Label(master=settings, text="Gamma default")
    Hovertip(lbl_gmax,"Initial gamma value for fit optimization (overrides default)")
    gcen=tk.Entry(master=settings, width=10)
    gcen.insert(0,'1')
    gcen.grid(row=2, column=3)
    lbl_gcen.grid(row=2, column=2)

    lbl_smin=tk.Label(master=settings, text="Sigma Min")
    Hovertip(lbl_smin,"Minimum value of peak width (default 0.01 min)")
    smin=tk.Entry(master=settings, width=10)
    smin.insert(0,'0.01')
    smin.grid(row=0, column=5)
    lbl_smin.grid(row=0, column=4)

    lbl_smax=tk.Label(master=settings, text="Sigma Max")
    Hovertip(lbl_smax,"Maximum value of peak width (default 1)")
    smax=tk.Entry(master=settings, width=10)
    smax.insert(0,'1')
    smax.grid(row=1, column=5)
    lbl_smax.grid(row=1, column=4)

    lbl_scen=tk.Label(master=settings, text="Sigma default")
    Hovertip(lbl_smax,"Initial sigma value for fit optimization (overrides default)")
    scen=tk.Entry(master=settings, width=10)
    scen.insert(0,'0.1')
    scen.grid(row=2, column=5)
    lbl_scen.grid(row=2, column=4)

    peaks = tk.Button(master=prominenceheight, text="Reidentify peaks", command=lambda:find_peaks(x,z,start,end,hplc_df,hei.get(),prom.get(),ax,canvas,window,prominenceheight))
    peaks.grid(row=0, column=4)
    var1=tk.IntVar()
    var2=tk.IntVar()
    check=tk.Checkbutton(master=onward, variable=var1, text="Graph text", onvalue=1, offvalue=0)
    Hovertip(check,"To include peak centers on graph or not")
    front=tk.Checkbutton(master=onward, variable=var2, text="Fronted peaks?", onvalue=-1, offvalue=1)
    front.deselect()
    Hovertip(front,"Fronted peaks. Makes all gamma values negative")

    # Capture all entry values before clearing frames to avoid TclError from destroyed widgets
    def on_fit():
        h=hei.get(); p=prom.get(); v=variation.get()
        g1=gmin.get(); g2=gmax.get(); gc=gcen.get()
        s1=smin.get(); s2=smax.get(); sc=scen.get()
        t=var1.get(); f=var2.get()
        clear(prominenceheight); clear(onward); clear(settings)
        fit_peaks(x,z,start,end,time,heights,hplc_df,sample_name,h,p,ax,canvas,window,t,v,g1,g2,gc,s1,s2,sc,f)

    fit=tk.Button(master=onward, text="Fit peaks", command=on_fit)
    check.grid(row=0, column=0)
    front.grid(row=0, column=1)
    fit.grid(row=0, column=2)



def fit_peaks(x,y,start,end,time,heights,hplc_df,sample_name,height,prominence,ax,canvas,window,text,variation,gmin,gmax,gcen,smin,smax,scen,fronted):
    variation=float(variation)
    areas=[]

    #show a "please wait" label while fitting runs
    wait_frame = tk.Frame(master=window)
    wait_frame.grid(row=2, column=0, padx=10)
    wait_label = tk.Label(master=wait_frame, text="Fitting peaks, please wait...", fg="grey")
    wait_label.grid(row=0, column=0)
    window.update()

    #find peak windows to improve runtime
    windows=peakclimber.find_peak_windows(x,y,time,heights,float(start),float(end))
    df=pd.DataFrame()
    df['Time']=hplc_df.loc[(hplc_df['Time']>=float(start)) & (hplc_df['Time']<=float(end))]['Time']
    df['y']=hplc_df.loc[(hplc_df['Time']>=float(start)) & (hplc_df['Time']<=float(end))]['Value']
    df['denoised_y']=peakclimber.remove_noise(y, band_limit=2000, lamba=1e10, smoothing=20, sampling_rate=500)

    #goes through each window and finds area for each
    for screen_window in windows:
        locs=screen_window[0]
        heights=screen_window[1]
        bounds=screen_window[2]
        sub_x=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['Time']
        sub_y=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['denoised_y']
        area=peakclimber.model_n_expgaus(sub_x,sub_y,len(locs),locs,heights,peak_variation=variation,gamma_min=float(gmin)*fronted,gamma_max=float(gmax)*fronted,gamma_center=fronted*float(gcen),sigma_min=float(smin),sigma_max=float(smax),sigma_center=float(scen))
        areas+=area

    # Remove the wait label now that fitting is done
    clear(wait_frame)

    ax.clear()
    peakclimber.graph_n_expgaus(x,y,len(areas),areas,sample_name,ax=ax,add_text=text)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Signal")
    canvas.figure.tight_layout()
    canvas.draw()

    locs=[]
    f_areas=[]
    for peak in areas:
        locs.append(peak[0])
        f_areas.append(peak[4])

    total_area = sum(f_areas) if sum(f_areas) != 0 else 1
    pct_areas = [a / total_area * 100 for a in f_areas]

    saver=tk.Frame(master=window)
    saver.grid(row=2, column=0)
    save_button = tk.Button(master=saver, text="Save Fit", command=lambda:[clear(saver),save(locs,f_areas,pct_areas,window),clear(tree_frame)])
    save_button.grid(row=0, column=0)

    # new file button to restart analysis with new chromatograph
    new_file_button = tk.Button(master=saver, text="New File", command=lambda:[clear(window), import_file('', window)])
    new_file_button.grid(row=0, column=2)

    # Back button: clear all lingering widgets at rows 2-3 before rebuilding find_peaks screen
    def on_back():
        for widget in window.grid_slaves():
            if 2 <= int(widget.grid_info()['row']) <= 3:
                widget.destroy()
        find_peaks(x,y,start,end,hplc_df,height,prominence,ax,canvas,window)
        
    back = tk.Button(master=saver, text="Back", command=on_back)
    back.grid(row=0, column=1)

    tree_frame = tk.Frame(window)
    tree_frame.grid(row=3, column=0)

    columns = ['Retention Time', 'Area', '% Area']
    tree = ScrollTree(tree_frame, columns=columns, show='headings',height=6)
    tree.grid(row=0, column=0)

    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, anchor='center')

    for i in range(0, len(locs)):
        tree.insert('', 'end', values=(round(locs[i], 3), round(f_areas[i], 3), round(pct_areas[i], 2)))


def save(locs, f_areas, pct_areas, window):
    output_list=[]
    for peak_n in range(0, len(locs)):
        output_dic={"Retention Time": locs[peak_n], "Peak Area": f_areas[peak_n], "% Area": pct_areas[peak_n]}
        output_list.append(output_dic)
    df_for_export=pd.DataFrame(output_list)
    SAVING_PATH = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
    if SAVING_PATH:
        df_for_export.to_csv(SAVING_PATH)

    filer=tk.Frame(master=window)
    filer.grid(row=2, column=0)

    new_file=tk.Button(master=filer, text="New File?", command=lambda:[clear(window),import_file('',window)])
    exiter=tk.Button(master=filer, text="Exit?", command=lambda:[close(window)])
    new_file.grid(row=0, column=0)
    exiter.grid(row=0, column=1)


def clear(level):
    liste = level.grid_slaves()
    for l in liste:
        l.destroy()


def close(window):
    window.destroy()
    exit()


window = tk.Tk()
window.title("PeakClimber")
window.geometry("1000x800")
s=ttk.Style()
s.theme_use('clam')
frm_entry = tk.Frame(master=window)
frm_entry.grid(row=0, column=0, padx=10)
sample_namer= tk.Entry(master=frm_entry, width=10)

lbl_name = tk.Label(master=frm_entry, text="Sample name:")

lbl_name.grid(row=0, column=0, sticky="w")
sample_namer.grid(row=0, column=1, sticky="w")
import_button = tk.Button(master=frm_entry, text="Import File", command=lambda:[import_file(sample_namer.get(),window),clear(frm_entry)])
import_button.grid(row=4, column=0)

# Persistent exit button fixed at row 4
exit_frame = tk.Frame(master=window)
exit_frame.grid(row=4, column=0, pady=5, sticky="se", padx=10)
window.grid_rowconfigure(5, weight=1)
window.grid_columnconfigure(0, weight=1)
exit_button = tk.Button(master=exit_frame, text="Exit", command=lambda: close(window))
exit_button.grid(row=0, column=0)

window.mainloop()