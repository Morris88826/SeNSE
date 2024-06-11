import os
import tqdm
import glob
import argparse
import pandas as pd
from libs.combine_data import verify_folder, ECG_read_and_combine, summary_read_and_combine, process_glucose

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine ECG and summary files')
    parser.add_argument('-c', '--cohort_id', type=int, help='cohort id')
    parser.add_argument('-s', '--subject_id', type=int, help='subject id')
    parser.add_argument('--regenerate', action='store_true', help='regenerate the combined file')
    parser.add_argument('--data_path', default='/mnt/data2/mtseng/dataset/SeNSE/TCH', type=str, help='path to folder to store combined files')
    parser.add_argument('--out_folder', default='/mnt/data2/mtseng/dataset/SeNSE/TCH_processed', type=str, help='path to folder to store combined files')

    args = parser.parse_args()

    folder_path = os.path.join(args.data_path, 'cohort{}'.format(args.cohort_id), 's{:02d}'.format(args.subject_id))
    subject_id = 'c{}s{:02d}'.format(args.cohort_id, args.subject_id)
    out_path = args.out_folder 

    os.makedirs(out_path, exist_ok=True)

    raw_out_dir = os.path.join(out_path, 'raw')
    os.makedirs(raw_out_dir, exist_ok=True)
    raw_out_path = os.path.join(raw_out_dir, '{}.pkl'.format(subject_id))

    if not os.path.exists(raw_out_path) or args.regenerate:  
        if not os.path.exists(raw_out_path):
            print("Raw data not found, processing ...")
        else:
            print("Regenerating raw data ...")
        print("===========================================")
        valid_folders = []
        # Iterate over only directories in the folder
        folders = glob.glob(os.path.join(folder_path, '*'))
        for folder in folders:
            if verify_folder(folder):
                valid_folders.append(folder)
        valid_folders.sort()
        print("Found {} valid folders".format(len(valid_folders)))

        print("===========================================")
        print("Combine ECG files")
        ecg_combined_df = ECG_read_and_combine(valid_folders)
        ecg_combined_df["Time"] = pd.to_datetime(ecg_combined_df["Time"], format='%d/%m/%Y %H:%M:%S.%f')
        print(ecg_combined_df.head())
        print(ecg_combined_df.shape)
        print("OK")

        print("===========================================")
        print("Combine summary files")
        summary_combined_df = summary_read_and_combine(valid_folders)
        summary_combined_df["Time"] = pd.to_datetime(summary_combined_df["Time"], format='%d/%m/%Y %H:%M:%S.%f')
        print(summary_combined_df.head())
        print(summary_combined_df.shape)
        print("OK")

        print("===========================================")
        print("Processing glucose file")
        glucose_path = glob.glob(os.path.join(folder_path, '*.csv'))[0]
        glucose_df = process_glucose(glucose_path)
        glucose_df["Timestamp"] = pd.to_datetime(glucose_df["Timestamp"], format='%d/%m/%Y %H:%M:%S.%f')
        glucose_df['Time'] = glucose_df['Timestamp'].copy()
        print(glucose_df.head())
        print(glucose_df.shape)
        print("OK")

        print("===========================================")
        print("Merging ECG, summary, and glucose files")
        hr_df = summary_combined_df[["Time", "HR", "HRConfidence", "ECGNoise"]]
        combined_df = pd.merge_asof(ecg_combined_df.sort_values('Time'), hr_df.sort_values('Time'), on='Time', direction='nearest', tolerance=pd.Timedelta('1s'))
        final_df = pd.merge_asof(combined_df.sort_values('Time'), glucose_df.sort_values('Time'), on='Time', tolerance=pd.Timedelta('330s'), direction='forward', allow_exact_matches=True)
        print(final_df.head())
        print(final_df.shape)
        
        print("===========================================")
        print("Rows with missing values:")
        print(final_df[final_df.isnull().any(axis=1)])
        print("Dropping rows with missing values ...")
        raw_final_df = final_df.dropna()

        print("===========================================")
        print("Saving the combined file")
        raw_final_df.to_pickle(os.path.join(raw_out_path, '{}.pkl'.format(subject_id)))
        print("Done")
