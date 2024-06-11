# Zephyr ECG, Summary, Glucose data processing Processing

## Overview
This project is a comprehensive suite for extracting ECG morphology, RR, and statistical features from Zephyr devices.

## Get Started
### Installation
1. Clone the repository
```
git clone https://github.com/Morris88826/SeNSE.git
cd SeNSE
```
2. Install dependent packages
```
conda create --name ecg python=3.11
conda activate ecg
pip install -r requirements.txt
```
### Download the Data
We use the data in the **TCH: Cohort 1 Data** and **TCH: Cohort 2 Data** folder from the **[SeNSE TAMU](https://drive.google.com/drive/folders/1Pts4PLTFIYqpPU53k8ZE4H-J4zZNH-WY?usp=drive_link)** team drive.
* Please reach out to Professor [Gutierrez-Osuna](mailto:rgutier@cse.tamu.edu) at the PSI Lab in the Department of Computer Science & Engineering at Texas A&M University if you wish to access the ECG data.

There should be five subject folders (S01-S05) in both **TCH: Cohort 1 Data** and **TCH: Cohort 2 Data** respectively. We only need the ***zephyr*** and ***cgm*** folders from each.
* For zephyr: download all folders inside
* For cgm: There should be one Clarity_report_..._.csv file

Download all the data and put them in the same folder. For example:

- SeNSE
  - TCH
    - cohort1
      - s01
        - 2022_06_08-13_32_45
        - 2022_06_08-17_47_46
        - ...
        - Clarity_Export_C01S01_2022-07-05.csv
      - s02
    - cohort2

### Run
Run the main script to collect the folder datas and combine with the glucose and summary files.

```
python main.py -c {cohort_id} -s {subject_id}
```

### Tasks

We also provides other scripts for further processing the data

- [x] Beat Extraction
- [x] Extract a 10s ECG window from the raw signal
