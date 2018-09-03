import numpy as np
import nolds
from scipy import interpolate
from scipy import signal
from astropy.stats import LombScargle

# ----------------- ClEAN OUTlIER / ECTOPIC BEATS ----------------- #

# TO DO ...


def clean_outlier_v1(rrintervals, method="Malik", custom_rule=None):
    """
    RR intervals differing by more than the removing_rule from the one
    proceeding it are removed.

    Arguments
    ---------
    rrintervals - list of Rr Intervals
    method - method to use to clean outlier. Malik, Kamath, Karlsson or Custom
    custom_rule - percentage criteria of difference with previous Rr
    Interval at which we consider that it is abnormal

    Returns
    ---------
    nnintervals - list of NN Interval

    """

    rrintervals = np.array(rrintervals)
    # rrintervals = np.where(rrinterval > 2000, np.nan, rrinterval) # rri 2000 --> bpm 30
    # rrintervals = np.where(rrinterval <  300, np.nan, rrinterval) # rri 300 --> bpm 200

    # set first element in list
    nnintervals = [rrintervals[0]]
    outlier_count = 0
    previous_outlier = False

    """
        if method == "Karlsson":
            if i == len(rrintervals)-2:
                break
            mean_prev_next_rri = (rrinterval + rrintervals[i + 2]) / 2
            if abs(mean_prev_next_rri - rrintervals[i+1]) < 0.2 * mean_prev_next_rri:
                nnintervals.append(rrintervals[i+1])
            else:
                nnintervals.append(np.nan)
                outlier_count += 1
                previous_outlier = True
        else:
    """

    if method == "mean_last9":
        nnintervals = []
        for i, rrinterval in enumerate(rrintervals):

            if i < 9:
                nnintervals.append(rrinterval)
                continue

            mean_last_9_elt = np.nanmean(nnintervals[-9:])
            if abs(mean_last_9_elt - rrinterval) < 0.2 * mean_last_9_elt:
                nnintervals.append(rrinterval)
            else:
                print(rrinterval)
                nnintervals.append(np.nan)
                outlier_count += 1
                # previous_outlier = True
    else:
        for i, rrinterval in enumerate(rrintervals[:-1]):

            if previous_outlier:
                nnintervals.append(rrintervals[i + 1])
                previous_outlier = False
                continue

            # TO DO pour v2 ... Check si plusieurs outliers consécutifs. Quelle règle appliquer ?
            # while previous_outlier:
            #   j += 1
            #  if is_outlier(rrinterval, rrintervals[i+1+j]):
            #     nnintervals.append(np.nan)
            #    continue
            # else:
            #    previous_outlier = False

            if is_outlier(rrinterval, rrintervals[i + 1], method=method, custom_rule=custom_rule):
                nnintervals.append(rrintervals[i + 1])
            else:
                # A débattre, Comment remplacer les outliers ?
                nnintervals.append(np.nan)
                outlier_count += 1
                previous_outlier = True

    print("Il y a {} outliers supprimés".format(outlier_count))

    return nnintervals


def is_outlier(rrinterval, next_rrinterval, method="Malik", custom_rule=None):
    if method == "Malik":
        return abs(rrinterval - next_rrinterval) <= 0.2 * rrinterval
    elif method == "Kamath":
        return 0 <= (next_rrinterval - rrinterval) <= 0.325 * rrinterval or 0 <= (
                    rrinterval - next_rrinterval) <= 0.245 * rrinterval
    elif method == "custom":
        return abs(rrinterval - next_rrinterval) <= custom_rule * rrinterval
    else:
        raise ValueError("Not a valid method. Please choose Malik or Kamath")


def test_sample(nnintervals, outlier_count):
    if outlier_count / len(nnintervals) > 0.2:
        print("Too much outlier for analyses !")
    if len(nnintervals) < 240:
        print("Not enough Heart beat for Nyquist criteria !")
    return None


# ----------------- TIME DOMAIN FEATURES ----------------- #


def get_time_domain_features(nnintervals):
    """
    Function returning a dictionnary containing time domain features for 
    hrV analyses.

    Mostly used on long term recordings (24h) but some studies use this 
    features on short term recordings, from 2 to 5 minutes window.
    
    Arguments
    ----------
    nnintervals - list of Normal to Normal Interval
    
    Returns
    ----------
    time_domain_features - dictionnary containing time domain features for 
    hrV analyses. Thera are details about each features below.
    
    Notes
    ----------
    Details about feature engineering...
    
    - **mean_nni**: The the mean RR interval
    
    - **sdnn**: The standard deviation of the time interval between successive normal heart 
    beats (*i.e.*, the RR intervals)
    
    - **sdsd**: Standard deviation of differences between adjacent NN intervals
    
    - **rmssd**: The square root of the mean of the sum of the squares of differences between
    adjacent NN intervals. Reflects high frequency (fast or parasympathetic) influences on hrV 
    (*i.e.*, those influencing larger changes from one beat to the next).
    
    - **median_nni**: Median Absolute values of the successive Differences between the RR intervals.

    - **nni50**: Number of interval differences of successive RR intervals greater than 50 ms.

    - **pnni50**: The proportion derived by dividing nni50 (The number of interval differences of 
    successive RR intervals greater than 50 ms) by the total number of RR intervals.

    - **nni20**: Number of interval differences of successive RR intervals greater than 20 ms.

    - **pnni20**: The proportion derived by dividing nni20 (The number of interval differences of 
    successive RR intervals greater than 20 ms) by the total number of RR intervals.

    - **CVSD**: The coefficient of variation of successive differences (van Dellen et al., 1985), 
    the rmssd divided by mean_nni.
    
    - **range_nni**: différence between the maximum and minimum nninterval.
    
    
    References
    ----------
    TO DO
    
    """
    
    diff_nni = np.diff(nnintervals)
    length_int = len(nnintervals)
    
    mean_nni = np.mean(nnintervals)
    sdnn = np.std(nnintervals, ddof=1)  # ddof = 1 : estimateur non biaisé => divise std par n-1
    sdsd = np.std(diff_nni)
    rmssd = np.sqrt(np.mean(diff_nni ** 2))
    median_nni = np.median(nnintervals)
    
    nni50 = sum(abs(diff_nni) > 50)
    pnni50 = 100 * nni50 / length_int
    nni20 = sum(abs(diff_nni) > 20)
    pnni20 = 100 * nni20 / length_int
    
    range_nni = max(nnintervals) - min(nnintervals)
    
    # Feature(s) trouvée(s) sur les codes github et non dans la doc
    # CVSD = RMMSD / mean_nni
    
    # Features non calculables pour short term recordings
    # sdnn équivaut à SDANN sur 24h et non sur une fenêtre temporelle
    # cvNN = sdnn / mean_nni # Necissite cycle 24h
    
    time_domain_features = {
        'mean_nni': mean_nni, 
        'sdnn': sdnn, 
        'sdsd': sdsd, 
        'nni50': nni50,
        'pnni50': pnni50,
        'nni20': nni20,
        'pnni20': pnni20,
        'rmssd': rmssd,
        'median_nni': median_nni,
        'range_nni': range_nni
        # ,'CVSD': CVSD,
        # 'sdnn': sdnn,
        # 'cvNN': cvNN
        
    }
    
    return time_domain_features


# TO DO -> GEOMETRICAl FEATURES

# ----------------- FREQUENCY DOMAIN FEATURES ----------------- #

def get_frequency_domain_features(nnintervals, method="Welch", sampling_frequency=7,
                                  interpolation_method="linear", vlf_band=(0.0033, 0.04),
                                  lf_band=(0.04, 0.15), hf_band=(0.15, 0.40), plot=0):
    
    """
    Function returning a dictionnary containing frequency domain features 
    for hrV analyses.
    Must use this function on short term recordings, from 2 to 5 minutes 
    window.
    
    Arguments
    ---------
    nnintervals - list of Normal to Normal Interval
    method - Method used to calculate the psd. Choice are Welch's, lomb and Fourier's method.
    sampling_frequency - frequence at which the signal is sampled. Common value range from 
    1 Hz to 10 Hz, by default set to 7 Hz. No need to specify if lomb method is used.
    interpolation_method - kind of interpolation as a string, by default "linear". No need to 
    specify if lomb method is used
    vlf_band - Very low frequency band for features extraction from power spectral density
    lf_band - low frequency band for features extraction from power spectral density
    hf_band - High frequency band for features extraction from power spectral density
    
    Returns
    ---------
    freqency_domain_features - dictionnary containing frequency domain features 
    for hrV analyses. Thera are details about each features are given in 
    "get_features_from_psd" function.
    
    References
    ----------
    TO DO
    """
    
    timestamps = create_time_info(nnintervals)

    # ---------- Interpolation du signal ---------- #
    if method == "Welch":
        funct = interpolate.interp1d(x=timestamps, y=nnintervals, kind=interpolation_method)

        timestamps_interpolation = create_interpolation_time(nnintervals, sampling_frequency)
        nni_interpolation = funct(timestamps_interpolation)
        
        # ---------- Remove DC Component ---------- #
        nni_normalized = nni_interpolation - np.mean(nni_interpolation)
    
    #  ----------  Calcul psd  ---------- #
    # Describes the distribution of power into frequency components composing that signal.
        freq, psd = signal.welch(x=nni_normalized, fs=sampling_frequency, window='hann')
    
    elif method == "lomb":
        freq, psd = LombScargle(timestamps, nnintervals, normalization='psd').autopower(minimum_frequency=vlf_band[0], 
                                                                                        maximum_frequency=hf_band[1])
    elif method == "Fourier":
        freq, psd = fourier_periodogram(timestamps, nnintervals)
    else:
        raise ValueError("Not a valid method. Choose between 'lomb' and 'Welch'")
        
    # ----------  Calcul des features  ---------- #
    freqency_domain_features = get_features_from_psd(freq=freq, psd=psd,
                                                     vlf_band=vlf_band,
                                                     lf_band=lf_band,
                                                     hf_band=hf_band)
    
    # TO DO 
    # Plotting options
    if plot == 1:
        pass
    
    return freqency_domain_features


def create_time_info(nnintervals):
    """
    Function creating time interval of all nnintervals
    
    Arguments
    ---------
    nnintervals - list of Normal to Normal Interval
    
    Returns
    ---------
    nni_tmstp - time interval between first NN Interval and final NN Interval
    """
    # Convert in seconds
    nni_tmstp = np.cumsum(nnintervals) / 1000.0 
    
    # Force to start at 0
    return nni_tmstp - nni_tmstp[0]


def create_interpolation_time(nnintervals, sampling_frequency=7):
    """
    Function creating the interpolation time used for Fourier transform's method
    
    Arguments
    ---------
    nnintervals - list of Normal to Normal Interval
    sampling_frequency - frequence at which the signal is sampled
    
    Returns
    ---------
    nni_interpolation_tmstp - timestamp for interpolation
    """
    time_nni = create_time_info(nnintervals)
    # Create timestamp for interpolation
    nni_interpolation_tmstp = np.arange(0, time_nni[-1], 1 / float(sampling_frequency))
    return nni_interpolation_tmstp


def fourier_periodogram(t, y):
    """
    TO DO
    """
    n = len(t)
    # Return the Discrete Fourier Transform sample frequencies
    frequency = np.fft.fftfreq(n, t[1] - t[0])
    # Compute the one-dimensional discrete Fourier Transform
    y_fft = np.fft.fft(y)
    positive = (frequency > 0)
    return frequency[positive], (1. / n) * abs(y_fft[positive]) ** 2


def get_features_from_psd(freq, psd, vlf_band=(0.003, 0.04), lf_band=(0.04, 0.15), hf_band=(0.15, 0.40)):
    """
    Function computing frequency domain features from the power spectral 
    decomposition.
    
    Arguments
    ---------
    freq - Array of sample frequencies
    psd - Power spectral density or power spectrum
    
    Returns
    ---------
    freqency_domain_features - dictionnary containing frequency domain features 
    for hrV analyses. Thera are details about each features are given below. 

    Notes
    ---------
    Details about feature engineering...
    
    - **total_power** : Total power density spectra
    
    - **vlf** : variance ( = power ) in hrV in the Very low Frequency (.003 to .04 Hz by
    default). Reflect an intrinsic rhythm produced by the heart which is modulated primarily by 
    sympathetic activity.
    
    - **lf** : variance ( = power ) in hrV in the low Frequency (.04 to .15 Hz). Reflects a 
    mixture of sympathetic and parasympathetic activity, but in long-term recordings like ours, 
    it reflects sympathetic activity and can be reduced by the beta-adrenergic antagonist propanolol
    
    - **hf**: variance ( = power ) in hrV in the High Frequency (.15 to .40 Hz by default). 
    Reflects fast changes in beat-to-beat variability due to parasympathetic (vagal) activity. 
    Sometimes called the respiratory band because it corresponds to hrV changes related to the 
    respiratory cycle and can be increased by slow, deep breathing (about 6 or 7 breaths per 
    minute) and decreased by anticholinergic drugs or vagal blockade.
    
    - **lf_hf_ratio** : lf/hf ratio is sometimes used by some investigators as a quantitative mirror 
    of the sympatho/vagal balance.
    
    - **lfnu** : normalized lf power
    
    - **hfnu** : normalized hf power
    
    References
    ---------
    TO DO
    
    """
    
    # Calcul des indices selon les bandes de fréquences souhaitées
    vlf_indexes = np.logical_and(freq >= vlf_band[0], freq < vlf_band[1])
    lf_indexes = np.logical_and(freq >= lf_band[0], freq < lf_band[1])
    hf_indexes = np.logical_and(freq >= hf_band[0], freq < hf_band[1])

    # STANDARDS

    # Integrate using the composite trapezoidal rule
    lf = np.trapz(y=psd[lf_indexes], x=freq[lf_indexes])
    hf = np.trapz(y=psd[hf_indexes], x=freq[hf_indexes])

    # total power & vlf : Feature utilisée plus souvent dans les analyses 
    # "long term recordings"
    vlf = np.trapz(y=psd[vlf_indexes], x=freq[vlf_indexes])
    total_power = vlf + lf + hf

    # Features non calculables pour "short term recordings"
    # ulf = np.trapz(y=psd[ulf_indexes], x=freq[ulf_indexes])
    
    lf_hr_ratio = lf / hf
    lfnu = (lf / (lf + hf)) * 100
    hfnu = (hf / (lf + hf)) * 100

    # Feature(s) trouvée(s) sur les codes github et non dans la doc
    # lf_P_ratio = lf / total_power
    # hf_P_ratio = hf/ total_power

    freqency_domain_features = {
        'lf': lf,
        'hf': hf,
        'lf_hr_ratio': lf_hr_ratio,
        'lfnu': lfnu,
        'hfnu': hfnu,
        'total_power': total_power,
        'vlf': vlf
        # 'ulf' : ulf,
        # 'lf_P_ratio' : lf_P_ratio,
        # 'hf_P_ratio' : hf_P_ratio
    }
    
    return freqency_domain_features

# ----------------- NON lINEAR DOMAIN FEATURES ----------------- #


def get_csi_cvi_features(nnintervals):
    """
    Function returning a dictionnary containing 3 features from non linear domain  
    for hrV analyses.
    Must use this function on short term recordings, for 30 , 50, 100 Rr Intervals 
    or seconds window.

    Arguments
    ---------
    nnintervals - list of Normal to Normal Interval

    Returns
    ---------
    csi_cvi_features - dictionnary containing non linear domain features 
    for hrV analyses. Thera are details about each features are given below. 
    
    Notes
    ---------
    - **csi** : 
    - **cvi** : 
    - **Modified_csi** : 
    
    References
    ----------
    TO DO    
    """
    
    # Measures the width and length of poincare cloud
    poincare_plot_features = get_poincare_plot_features(nnintervals)
    T = 4 * poincare_plot_features['sd1']
    L = 4 * poincare_plot_features['sd2']
    
    csi = L / T
    cvi = np.log10(L * T)
    modified_csi = L**2 / T
    
    csi_cvi_features = {
        'csi': csi,
        'cvi': cvi,
        'Modified_csi': modified_csi
    }
    
    return csi_cvi_features


def get_poincare_plot_features(nnintervals):
    """
    Function returning a dictionnary containing 3 features from non linear domain  
    for hrV analyses.
    Must use this function on short term recordings, from 5 minutes window.

    Arguments
    ---------
    nnintervals - list of Normal to Normal Interval

    Returns
    ---------
    poincare_plot_features - dictionnary containing non linear domain features 
    for hrV analyses. Thera are details about each features are given below. 
    
    Notes
    ---------
    - **sd1** : 
    - **sd2** : 
    - **ratio_sd1_sd2** : 
    
    References
    ----------
    TO DO   
    """
    diff_nnintervals = np.diff(nnintervals)
    # measures the width of poincare cloud
    sd1 = np.sqrt(np.std(diff_nnintervals, ddof=1) ** 2 * 0.5)
    # measures the length of the poincare cloud
    sd2 = np.sqrt(2 * np.std(nnintervals, ddof=1) ** 2 - 0.5 * np.std(diff_nnintervals, ddof=1) ** 2)
    ratio_sd1_sd2 = sd1 / sd2
    
    poincare_plot_features = {
        'sd1': sd1,
        'sd2': sd2,
        'ratio_sd1_sd2': ratio_sd1_sd2
    }

    return poincare_plot_features


def get_sampen(nnintervals):
    """
    Must use this function on short term recordings, from 1 minute window.
    TO DO
    """
    sampen = nolds.sampen(nnintervals, emb_dim=2)
    return {'sampen': sampen}