#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:53:58 2024

@author: jderrick
"""

import peakclimber
import pandas as pd
sample=True
while sample:
    filename=input("Filename for desired fit: ")
    sample_name=input("Sample Name: ")
    hplc=[]
    try:
        hplc+=peakclimber.make_entry(filename,{"Name":sample_name})
        hplc_df=pd.DataFrame(hplc)
        start_time=int(input("Start Time for analysis (minutes): "))
        end_time=int(input("End Time for analysis (minutes): "))
        
        
        x=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time)& (hplc_df['Name']==sample_name)]['Time']
        y=hplc_df.loc[(hplc_df['Time']>=start_time) & (hplc_df['Time']<=end_time)& (hplc_df['Name']==sample_name)]['Value']
        z=peakclimber.remove_noise(y,2000,1e11,20)
        df = pd.DataFrame()
        df["Time"]=x
        df["Value"]=z
        peaks=peakclimber.find_peak_areas(df,start_time,end_time,graph=True,name=sample_name)
        output_list=[]
        for peak_n in range(0,len(peaks[0])):
            output_dic={"Retention Time":peaks[0][peak_n],"Peak Area":peaks[1][peak_n]}
            output_list.append(output_dic)
        df_for_export=pd.DataFrame(output_list)
        df_for_export.to_csv(sample_name+"_peak.csv")
        cont=input("More files?: ")
        if cont=="n" or cont=="no":
            sample=False
            break
    except OSError:
        print("invalid file name")
   

