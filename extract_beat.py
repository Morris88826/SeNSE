import os
import tqdm
import argparse
import numpy as np
import pandas as pd
import neurokit2 as nk
from joblib import Parallel, delayed

def process_cgm_segment(cgm_df, _cgm_idx, fs=250):
    data = []
    glucose = cgm_df["glucose"].values.mean()
    Timestamp = cgm_df["Timestamp"].values[0]

    ecg = cgm_df["EcgWaveform"].values
    ecg_clean = nk.ecg_clean(ecg, sampling_rate=fs)
    try:
        _, rpeaks = nk.ecg_peaks(ecg_clean, sampling_rate=fs, correct_artifacts=True)
    except:
        print("Error in ECG peaks: {}, shape: ".format(_cgm_idx, cgm_df.shape))
        return data
    r_peaks = np.unique(rpeaks['ECG_R_Peaks'])

    # _, waves_peak = nk.ecg_delineate(ecg_clean, r_peaks, sampling_rate=fs, method="peak")
    # p_peaks = np.where(np.isnan(waves_peak['ECG_P_Peaks']), -1, waves_peak['ECG_P_Peaks']).astype(int)
    # q_peaks = np.where(np.isnan(waves_peak['ECG_Q_Peaks']), -1, waves_peak['ECG_Q_Peaks']).astype(int)
    # s_peaks = np.where(np.isnan(waves_peak['ECG_S_Peaks']), -1, waves_peak['ECG_S_Peaks']).astype(int)
    # t_peaks = np.where(np.isnan(waves_peak['ECG_T_Peaks']), -1, waves_peak['ECG_T_Peaks']).astype(int)
    
    Times = cgm_df["Time"].values
    cgm_start_idx = cgm_df.index[0]
    for i in range(1, len(r_peaks)):
        rr = Times[r_peaks[i]] - Times[r_peaks[i-1]]
        Time = Times[r_peaks[i]]
        
        start_t = Time - (1/3) * rr
        end_t = Time + (1/2) * rr

        beat_window = cgm_df[(cgm_df["Time"] > start_t) & (cgm_df["Time"] < end_t)]
        beat_start_idx = beat_window.index[0]
        r_peak_idx = cgm_start_idx + r_peaks[i] - beat_start_idx

        avg_HRConfidence = beat_window["HRConfidence"].values.mean()
        avg_ECGNoise = beat_window["ECGNoise"].values.mean()

        data.append({
            "Time": beat_window["Time"].values,
            "EcgWaveform": beat_window["EcgWaveform"].values,
            "HR": beat_window["HR"].values,
            "glucose": glucose,
            "CGM_idx": _cgm_idx,
            'HRConfidence': avg_HRConfidence,
            'ECGNoise': avg_ECGNoise,
            'r_peak': r_peak_idx,
            'Timestamp': Timestamp,
        })
    
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--subject_id', type=str, help='subject id')
    parser.add_argument('--regenerate', action='store_true', help='regenerate the beat file')
    parser.add_argument('--out_folder', default="/mnt/data2/mtseng/dataset/SeNSE/TCH_processed", type=str, help='path to folder containing the combined ECG, summary, and glucose file')
    args = parser.parse_args()

    out_folder = args.out_folder
    subject_id = args.subject_id
    fs = 250

    out_dir = os.path.join(out_folder, "beat")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, "{}.pkl".format(subject_id))

    if not os.path.exists(output_path) or args.regenerate:
        if not os.path.exists(output_path):
            print("Beat data not found, processing ...")
        else:
            print("Regenerating beat data ...")
        print("===========================================")
        df = pd.read_pickle(os.path.join(out_folder, "raw/{}.pkl".format(subject_id)))
        print(df.head())
        print(df.shape)
        cgm_idx = df["Index"].unique()
        print("Number of CGM segments: {}".format(len(cgm_idx)))

        # Parallel processing of each CGM segment
        results = Parallel(n_jobs=-1)(delayed(process_cgm_segment)(df[df["Index"] == _cgm_idx], _cgm_idx, fs) for _cgm_idx in tqdm.tqdm(cgm_idx))

        # Flatten the list of results
        data = [item for sublist in results for item in sublist]
        print("Number of beats: {}".format(len(data)))

        # Save the data
        pd.DataFrame(data).to_pickle(output_path)

