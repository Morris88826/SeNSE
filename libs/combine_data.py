import os
import glob
import tqdm
import pandas as pd
from datetime import datetime

# Attempt to convert it to a datetime object
def is_valid_timestamp(timestamp_string):
    try:
        # Define the format based on the given string
        format_string = "%Y_%m_%d-%H_%M_%S"
        converted_time = datetime.strptime(timestamp_string, format_string)
        return True, converted_time
    except ValueError:
        return False, None

def verify_folder(folder_path):
    # Check if folder exists
    if not os.path.isdir(folder_path):
        return False

    folder_name = os.path.basename(folder_path)
    # Check if folder name is a valid timestamp
    if not is_valid_timestamp(folder_name)[0]:
        return False
    
    # Check if folder contains ECG and summary files
    file_path = glob.glob(os.path.join(folder_path, '*_ECG.csv'))
    if len(file_path) != 1:
        print("Skipping folder: {} (Doesn't have _ECG.csv)".format(folder_name))
        return False
    
    file_path = glob.glob(os.path.join(folder_path, '*_SummaryEnhanced.csv'))
    if len(file_path) != 1:
        print("Skipping folder: {} (Doesn't have _SummaryEnhanced.csv)".format(folder_name))
        return False

    return True

# combine ECG files
def ECG_read_and_combine(valid_folders):
    ecg_combined_df = pd.DataFrame()
    for folder_path in tqdm.tqdm(valid_folders):
        file_path = glob.glob(os.path.join(folder_path, '*_ECG.csv'))[0]
        df = pd.read_csv(file_path)        
        ecg_combined_df = pd.concat([ecg_combined_df, df])
    return ecg_combined_df

# combine summary files
def summary_read_and_combine(valid_folders):
    summary_combined_df = pd.DataFrame()

    for folder_path in tqdm.tqdm(valid_folders):
        file_path = glob.glob(os.path.join(folder_path, '*_SummaryEnhanced.csv'))[0]
        df = pd.read_csv(file_path)
        summary_combined_df = pd.concat([summary_combined_df, df])
    
    return summary_combined_df

def process_glucose(glucose_path):
    glucose_df = pd.read_csv(glucose_path,delimiter=',')
    glucose_df = glucose_df[glucose_df['Event Type'] == 'EGV'].reset_index(drop = True) 
    glucose_df['Glucose Value (mg/dL)'] = glucose_df['Glucose Value (mg/dL)'].str.replace('Low','40')
    glucose_df['Glucose Value (mg/dL)'] = glucose_df['Glucose Value (mg/dL)'].str.replace('High','400')

    glucose_df = glucose_df[['Timestamp (YYYY-MM-DDThh:mm:ss)','Glucose Value (mg/dL)', 'Index']]
    glucose_df.columns = ['Timestamp','glucose','Index']

    try:
        glucose_df['Timestamp'] = pd.to_datetime(glucose_df['Timestamp'],format = '%Y-%m-%dT%H:%M:%S')
    except:
        glucose_df['Timestamp'] = pd.to_datetime(glucose_df['Timestamp'],format = '%Y-%m-%d %H:%M:%S')
    glucose_df['glucose'] = glucose_df['glucose'].astype(float)
    glucose_df = glucose_df.sort_values('Timestamp').reset_index(drop = True)

    return glucose_df
