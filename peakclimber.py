import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd 
import seaborn as sns 
import pybaselines
import math
from scipy.signal import find_peaks, savgol_filter
from scipy import special	
from scipy.signal import get_window
from lmfit.models import ExponentialGaussianModel
import lmfit

plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams["font.family"] = "Arial"
sns.set(font_scale=2)
sns.set_style("white")



def make_entry(filename, metadata): 
    """
    Imports a chromatograph into a pandas dataframe 
    Inputs: 
        filename: text 
        path to file directory containing chromatographic trace 
        meatadata: Dictionary 
        Relevant variable names and values about sample (genotype, background, replicate sample name)
    
    
    Outputs: 
        An list of dictionaries 
        Each line is a step in the hplc trace 
    """
    csv=pd.read_csv(filename,skiprows=range(0, 42),sep="\t")
    hplc=[]
    #iterates through the rows of the CSV and adds a dictionary entry for that time point 
    for row in csv.itertuples():
        val=''
        if isinstance(row[3],str):
            val=float(row[3].replace(',',''))
            
        else: 
            val=row[3]
        trace_dict={"Time":row[1],"Value":val}
        for key in metadata: 
            trace_dict[key]=metadata[key]
        hplc.append(trace_dict)
    return hplc 

def low_pass_filter(data, band_limit, sampling_rate) -> np.ndarray:
    
    """
    Applies a low pass FFT filter to a numpy array 
    Inputs: 
        data: numpy array 
        chromatographic data 
        band_limit: int 
        Frequency limit at which data is cutoff  
        sampling rate: int 
        Number of data points a minute 
    Outputs: 
        np array that has been FFTed 
    """
    #cutoff_index = int(band_limit * data.size / sampling_rate)
    F = np.fft.rfft(data*np.kaiser(data.size,0))
    #F[cutoff_index + 1:] = 0
   
    return np.fft.irfft(F, n=data.size).real
def remove_noise(data, band_limit=2000,lamba=1e10,smoothing=20, sampling_rate=500):
    """
    Denoises chromatographic trace with high-pass (pybaselines) and low-pass (low_pass_filter FFT) filters 
    Inputs: 
        Data: numpy array with signal 
        Band-limit (int): Frequency cutoff for FFT
        Sampling-rate (int): Max Frequency that's measured (500/s for our machine)
        lamba (int): smoothing function for whitaker 
    
    Outputs:
        z numpy array with transformed signal 
    """
    k=pybaselines.whittaker.psalsa(data,lam=lamba)[0]
    data=data-k
    z=low_pass_filter(data,band_limit,sampling_rate)
    z=np.convolve(z, np.ones(smoothing)/smoothing, mode='same')
    return z
def bemg(x,amplitude,center,sigma,gamma):
    return np.exp(sigma*sigma/(2*gamma**2)+(center-x)/(gamma))*special.erfc((-1*math.copysign(1, gamma)*(x-center)/sigma-sigma/(gamma))/math.sqrt(2))*math.copysign(1, gamma)*amplitude/(2*gamma)

def model_n_expgaus(x,y,number_peaks,peak_locations,peak_heights,gamma_min=0.1,gamma_max=2,gamma_center=1,peak_variation=0.1,
                    sigma_min=0.005,sigma_max=1,sigma_center=0.1,height_scale=0.01,height_scale_high=0.8):
    """
    Fits n expoential gaussians to chromatographic data and returns list of parameters and the area of each peak 
    Inputs:
        x: Time axis, list 
        y: CAD, FLD axis, list

        number_peaks: Number of peaks, int 
        peak_locations: locations of peaks along x axis, float 
        peak_heights: Value on y axis of each peak, float 
        
        gamma_min: float: 
            mimimum value of gamma for exponential gaussian fit (see lmfit documentation)
        gamma_max: float: 
            maximum value of gamma for exponential gaussian fit (see lmfit documentation)
        gamma_center: float: 
            initial guess of value of gamma for exponential gaussian fit (see lmfit documentation)
        peak_variation: float 
            max variation of center for exponential gaussian fits 
        sigma_min: float 
            min sigma for exponential gaussian fits 
        sigma_max: float 
            max sigma for exponential gaussian fits 
        sigma_center: float 
            guess for sigma for exponential gaussian fits 
        height_scale: float 
            minimum amplitude for exponential gaussian fits 
        height_scale_high: float 
            maximum amplitude for exponential gaussian fits
    Outputs: Array of tuples (parameters, area). Tuples are define each peak, and each row in the array is an individual peak 
    
    
    Prints(optional): 
        Summary graphs 
        1. Peak identification 
        2. Intial Fit 
        3. Final Fit+ individual chromatographs 
    """
  
    #goes from max to min number of peaks, finds bic, removes smallest peak, repeat 
    model=''
    for n in range(0,number_peaks):
        gaus=lmfit.Model(bemg,prefix='p'+str(n)+"_")
        #addition of first model for first peak
        if model=='':
            model=gaus
            pars=gaus.make_params(prefix='p'+str(n)+"_")
            #peak locations can vary by 1 min 
            pars['p'+str(n)+'_center'].set(value=peak_locations[n],min=peak_locations[n]-peak_variation,max=peak_locations[n]+peak_variation)
            #sigma can only be so large and small 
            pars['p'+str(n)+'_sigma'].set(value=sigma_center, min=sigma_min,max=sigma_max)
            #amplitude can only be so small to be a real peak. Height correction from Amplitude to height is roughly /gamma~2  
            pars['p'+str(n)+'_amplitude'].set(value=peak_heights[n]*0.5, min=height_scale*peak_heights[n],max=peak_heights[n]*height_scale_high)
            pars['p'+str(n)+'_gamma'].set(value=gamma_center,max=gamma_max,min=gamma_min)
        #all subsequent peaks    
        else:
            model+=gaus
            pars.update(gaus.make_params(prefix='p'+str(n)+"_"))
            pars['p'+str(n)+'_center'].set(value=peak_locations[n],min=peak_locations[n]-peak_variation,max=peak_locations[n]+peak_variation)
            #sigma can only be so large and small 
            pars['p'+str(n)+'_sigma'].set(value=sigma_center, min=sigma_min,max=sigma_max)
            #amplitude can only be so small to be a real peak Height correction from Amplitude to height is roughly /gamma~2  
            pars['p'+str(n)+'_amplitude'].set(value=peak_heights[n]*0.5, min=height_scale*peak_heights[n],max=peak_heights[n]*height_scale_high)
            pars['p'+str(n)+'_gamma'].set(value=gamma_center,max=gamma_max,min=gamma_min)
    #Uses gradient descent to best fit model 
    try:
        out = model.fit(y, pars, x=x,nan_policy='omit')
        print(out.fit_report())
    except AttributeError:
        return None


    



    comps=out.eval_components(x=x) 
    
    #plots each peak 
    areas=[]
    for n in range(0,number_peaks):
        area=sum(comps['p'+str(n)+"_"])*0.01
        center=out.params['p'+str(n)+"_center"].value
        sigma=out.params['p'+str(n)+"_sigma"].value
        amplitude=out.params['p'+str(n)+"_amplitude"].value
        gamma=out.params['p'+str(n)+"_gamma"].value

        areas.append([center,sigma,amplitude, gamma,area/6])
    
    return(areas)


def graph_n_expgaus(x,y,number_peaks,parameters,name,ax=None,add_text=1):
    """
    Combines multiple exponential gaussian fits together to create graph output 
    Inputs: 
        x, y: array
        time and variable series respectively 
        number_peaks: int 
        number of peaks in the sample 
        parameters: list of lists containing the parameters for each exponential gaussian 
        name: name of the image file for graphical output

    Prints: 
        Summary graphs Final Fit+ individual chromatographs 
    Returns: 
        Nothing
    """

 

    model=''
    for n in range(0,number_peaks):
        gaus=lmfit.Model(bemg,prefix='p'+str(n)+"_")
        #addition of first model for first peak
        if model=='':
            model=gaus
            pars=gaus.make_params(prefix='p'+str(n)+"_")
            #peak locations can vary by 1 min 
            pars['p'+str(n)+'_center'].set(value=parameters[n][0],vary=False)
            #sigma can only be so large and small 
            pars['p'+str(n)+'_sigma'].set(value=parameters[n][1],vary=False)
            #amplitude can only be so small to be a real peak 
            pars['p'+str(n)+'_amplitude'].set(value=parameters[n][2],vary=False)
            pars['p'+str(n)+'_gamma'].set(value=parameters[n][3],vary=False)
       
        #all subsequent peaks    
        else:
            model+=gaus
            pars.update(gaus.make_params(prefix='p'+str(n)+"_"))
            pars['p'+str(n)+'_center'].set(value=parameters[n][0],vary=False)
            pars['p'+str(n)+'_sigma'].set(value=parameters[n][1],vary=False)
            pars['p'+str(n)+'_amplitude'].set(value=parameters[n][2],vary=False)
            pars['p'+str(n)+'_gamma'].set(value=parameters[n][3],vary=False)
        
            #intial fit 

    #to get best fit 
    out = model.fit(y, pars, x=x)


 







    comps=out.eval_components(x=x) 
   
    if ax is None:
        print('here')
        fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    
    else:
        ax=ax
    #plots underlying data
    #axes[0].plot(x, y)
    #plots initial fit in orange with dashed line 
    #axes[0].plot(x, init, '--', label='initial fit')
    #plots best fit in green with solid line 
    #axes[0].plot(x, out.best_fit, '-', label='best fit')
    ax.plot(x, out.best_fit, '-', label='best fit')
    #axes[0].legend()

    #find the components of the best fit curve 
    #plots underlying data 
    ax.plot(x, y)

    #plots each peak 
    for n in range(0,number_peaks):
        ax.plot(x, comps['p'+str(n)+"_"], '--', label='Gaussian component '+str(n))
        ax.fill_between(x, comps['p'+str(n)+"_"].min(), comps['p'+str(n)+"_"], alpha=0.5) 
        #adds peak location on the actual output graph 
        if add_text==1:
            ax.text(out.params['p'+str(n)+"_center"].value, out.params['p'+str(n)+"_amplitude"].value+1, str(out.params['p'+str(n)+"_center"].value)[0:5], fontsize=8,horizontalalignment='center')
    
    plt.show()
    plt.savefig(name+".png")
    #return areas
def find_locations_peaks(x,y,peak_prominence_cutoff,height_cutoff,graph=False,shoulder=False, shoulder_cutoffs=None,ax=None):
    """
    

    Parameters
    ----------
    x : List of floats 
        Time axis 
    y : List of floats 
        Signal axis
    peak_prominence_cutoff : float
        Value at which to cut off prominence. Prominences below this value are not accepted as real peaks 
    height_cutoff : float 
        Value at which to cut off peak height. Heights below this value are not accepted as real peaks 
    graph : Bool, optional
        Whether to graph peak locations or not . The default is False.
    shoulder : Bool, optional
        Whether or not to include shoulders in the peak analysis. The default is False.
    shoulder_cutoffs : Float, optional
        Shoulder prominence cut off value (first derivative). Shoulders below this value are not included  The default is None.

    Returns
    -------
    time: list of floats 
    list of peak times 
    
    heights: list of floats 
    list of peak heights (index is the same as time )
    """
    
    #Finds time averaged derivative
    data=pd.DataFrame()
    data["Time"]=x
    data["Value"]=y
    #smooths the data with a savgol filter and taeks first dderivative 
    data.loc[:, 'Smoothed']=savgol_filter(y, window_length=101, polyorder=3, deriv=0)
    data.loc[:, 'Time Ave']=savgol_filter(y, window_length=101, polyorder=3, deriv=1)
    #data.loc[:, 'Time Ave']+=min(data.loc[:, 'Time Ave'])
    if graph:
        if ax is None:
            print('here')
            fig,ax=plt.subplots(1,1,figsize=(10,10))
        else:
            ax=ax
        #plots derivative 
        sns.lineplot(x=data['Time'], y=data['Smoothed'], label='Smoothed',ax=ax)
    data["Inverse Smoothed"]=data.loc[:,'Smoothed']*-1+max(data.loc[:, 'Smoothed'])
    data["Inverse Time Ave"]=data.loc[:,'Time Ave']*-1+max(data.loc[:, 'Time Ave'])
    data["Moved Time Ave"]=data.loc[:,'Time Ave']+abs(min(data.loc[:, 'Time Ave']))
    data["contrast"]=data.loc[:, 'Smoothed']- 50*data.loc[:, 'Time Ave']
    """
    if graph:
        sns.lineplot(x=data['Time'], y=data['contrast'], label='Time Averaged First Derivative',ax=ax[1])
    """
    #finds peaks from the time averaged derivative. These are really inflection points not actually peaks, but this
    #method will correctly identify shoulders
    #finds real peaks 

    peaks = find_peaks(data['Smoothed'],prominence=peak_prominence_cutoff,height=height_cutoff)[0]
    pre_shoulder_times=find_peaks(data['contrast'],prominence=peak_prominence_cutoff*5,height=height_cutoff)[0]
    shoulder_times=[]
    for time in pre_shoulder_times:
        add=True
        for peak in peaks:
            
            if abs(peak-time)<200:
                add=False
                break
        if add:
            shoulder_times.append(time)
    """
    for potential_shoulder in peaks2: 

        if data["Time Ave"].values[potential_shoulder]>=0:
            pass 
        else:
            shoulder_times.append(potential_shoulder)
    for potential_shoulder in valleys2: 

        if data["Time Ave"].values[potential_shoulder]<=0:
            pass 
        else:
            shoulder_times.append(potential_shoulder)
    """
    #plots IDed peaks on the underlying data 
    if graph:
        sns.scatterplot(x=data["Time"].values[peaks], y=data["Smoothed"].values[peaks], s = 55,
                 label = 'Peak Centers',ax=ax)
        """
        if shoulder:
            sns.scatterplot(x=data["Time"].values[shoulder_times], y=data["contrast"].values[shoulder_times], s = 55,
                     label = 'Peak Shoulders',ax=ax[1])
        """    
        plt.show()
    
    times=data["Time"].values[peaks]
    heights=data["Value"].values[peaks]
    if shoulder:

        for peak in shoulder_times:
            if peak not in peaks:
                peaks=np.append(peaks,peak)
        
   
    
    times=data["Time"].values[peaks]
    heights=data["Value"].values[peaks]
        
    
    

    #converts reference peaks into the time domain (rather than index )
    return times,heights
def find_peak_windows(x,y,reference_peak_list,heights,start,end):
    """
    

    Parameters
    ----------
    x : List of floats 
        TIME SERIES 
    y : List of floats 
        VALUE SERIES
    reference_peak_list : list of floats
        List of peak locations 
    heights : list of floats 
        List of peak heights 
    start : int or float
        Start time of series 
    end : int or float
       End time of series 

    Returns
    -------
    windows : list of three variables for each window
        Locations: all peaks in window 
        Heights: heights of all peaks in window
        Bounds: start and end location of window 

    """
    windows=[]
    indices=[start]
    #finds all zeroes in graph 
    for i,j in zip(y,x): 
        if i<=0:
            indices.append(j)
    current_window=[]
    current_height=[]
    current_loc=[]
    current_index=0
    #starts lower bound at current index 
    bounds=[indices[current_index]]
    #iterates through all peaks and heights 
    for loc,height in zip(reference_peak_list,heights):
        inwindow=False
        while inwindow==False:
            #add peak to current window
            if loc<indices[current_index]:
                current_loc.append(loc)
                current_height.append(height)
                inwindow=True
           #once you're beyond index end of the window, break window 
            else:
                current_index+=1
                if current_loc!=[]:
                    bounds.append(indices[current_index])
                    current_window=[current_loc,current_height,bounds]
                    windows.append(current_window)
                    current_window=[]
                    current_height=[]
                    current_loc=[]
                    bounds=[indices[current_index]]
    #end final window 
    bounds.append(end)
    current_window=[current_loc,current_height,bounds]
    windows.append(current_window)
    
        

    return windows 
def find_peak_areas(single_rep,start,end,name="graph",canonical_peaks=None,graph=False,shoulder=True,prominence_cutoff=0.05,height_cutoff=1,gamma_min=1,gamma_max=5,gamma_center=2,peak_variation=0.1,
                    sigma_min=0.05,sigma_max=0.2,sigma_center=0.1,height_scale=0.2,height_scale_high=1,ax=None):
    """
    

    Parameters
    ----------
    single_rep : pandas dataframe
        dataframe containing only time/value information of the replicate of interest 
    start : int or float
        start time of the region of interest 
    end : int or float
        end time of the region of interest
    canonical_peaks : list of floats, optional
        List of canonical peaks (on the time axis). The default is None.
    graph : BOOL, optional
        Whether or not to graph outputs. The default is False.
    shoulder : Bool, optional
        Whether or not to include shoulders in graph. The default is False.
    prominence_cutoff: float 
        minimum prominence to define a single peak 
    height_cutoff: flaot 
        mimimum height to define a single peak 
    gamma_min: float: 
        mimimum value of gamma for exponential gaussian fit (see lmfit documentation)
    gamma_max: float: 
        maximum value of gamma for exponential gaussian fit (see lmfit documentation)
    gamma_center: float: 
        initial guess of value of gamma for exponential gaussian fit (see lmfit documentation)
    peak_variation: float 
        max variation of center for exponential gaussian fits 
    sigma_min: float 
        min sigma for exponential gaussian fits 
    sigma_max: float 
        max sigma for exponential gaussian fits 
    sigma_center: float 
        guess for sigma for exponential gaussian fits 
    height_scale: float 
        minimum amplitude for exponential gaussian fits 
    height_scale_high: float 
        maximum amplitude for exponential gaussian fits 
    name: string
        name of fileoutput for graph

    Returns
    -------
    locs : list of floats 
        Peak locations 
    f_areas : list of floats 
        Peak areas, matched to peak locations by index 

    """
    #makes time axis 
    x=single_rep.loc[(single_rep['Time']>=start) & (single_rep['Time']<=end)]['Time']
    #makes value axis 
    y=single_rep.loc[(single_rep['Time']>=start) & (single_rep['Time']<=end)]['Value']
    #denoises y-axis 
    #y=remove_noise(y)
    

    # if there are no input peaks, find peaks 
    if canonical_peaks is None:
        reference_peak_list,heights=find_locations_peaks(x,y,prominence_cutoff,height_cutoff,graph=graph,shoulder=shoulder)
    #else just use canonical peaks 
    else:
        reference_peak_list=canonical_peaks
   
    areas=[]
    #find peak windows to improve runtime 
    windows=find_peak_windows(x,y,reference_peak_list,heights,start,end)
    df=pd.DataFrame()
    df['Time']=single_rep.loc[(single_rep['Time']>=start) & (single_rep['Time']<=end)]['Time']
    df['y']=single_rep.loc[(single_rep['Time']>=start) & (single_rep['Time']<=end)]['Value']
    df['denoised_y']=remove_noise(y, band_limit=2000,lamba=1e10,smoothing=20, sampling_rate=500)

    #goes through each window and finds area for each 
    for window in windows:
        print(window)
        locs=window[0]
        heights=window[1]
        bounds=window[2]
        sub_x=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['Time']
        sub_y=df.loc[(df['Time']>=bounds[0]) & (df['Time']<bounds[1])]['y']
        area=model_n_expgaus(sub_x,sub_y,len(locs),locs,heights,gamma_min,gamma_max,gamma_center,peak_variation,sigma_min,sigma_max,sigma_center,height_scale,height_scale_high)
        areas+=area
    #graphs if required 
    if graph:
        graph_n_expgaus(x,y,len(areas),areas,name,ax=ax)
    locs=[]
    f_areas=[]
    for peak in areas:
        locs.append(peak[0])
        f_areas.append(peak[4])
    return locs,f_areas


