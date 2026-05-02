import time
from os.path import join
import os
from time import sleep
import requests
from datetime import datetime
from google.cloud import bigquery


ADC_SYSFS_PATH = "/sys/bus/iio/devices/iio:device0/"
PH_RAW_FILE = join(ADC_SYSFS_PATH, "in_voltage0-voltage3_raw")
PH_SCALE_FILE = join(ADC_SYSFS_PATH, "in_voltage0-voltage3_scale")
PH_SENSITIVITY_MV = 59.16
PH_BOARD_GAIN = -3.4
PH_TOTAL_GAIN = None
PH_FILE = None

ORP_RAW_FILE = join(ADC_SYSFS_PATH, "in_voltage1-voltage3_raw")
ORP_SCALE_FILE = join(ADC_SYSFS_PATH, "in_voltage1-voltage3_scale")
ORP_BOARD_GAIN = -1
ORP_TOTAL_GAIN = None
ORP_FILE = None

REF_RAW_FILE = join(ADC_SYSFS_PATH, "in_voltage3_raw")
REF_SCALE_FILE = join(ADC_SYSFS_PATH, "in_voltage3_scale")
REF_TOTAL_GAIN = None
REF_FILE = None


AVERAGES = 64


with open(PH_SCALE_FILE, "r") as f:
    PH_TOTAL_GAIN = float(f.read()) / PH_BOARD_GAIN


with open(ORP_SCALE_FILE, "r") as f:
    ORP_TOTAL_GAIN = float(f.read()) / ORP_BOARD_GAIN


with open(REF_SCALE_FILE, "r") as f:
    REF_TOTAL_GAIN = float(f.read())


def measure_orp() -> float:
    ORP_FILE.seek(0)
    orp_adc = int(ORP_FILE.read())
    return orp_adc * ORP_TOTAL_GAIN


def measure_ph() -> float:
    PH_FILE.seek(0)
    ph_adc = int(PH_FILE.read())
    #print(f'Raw ph: {ph_adc}')
    ph = 7.0 - ph_adc * PH_TOTAL_GAIN / PH_SENSITIVITY_MV
    return ph


def measure_ref() -> float:
    REF_FILE.seek(0)
    orp_adc = int(REF_FILE.read())
    return orp_adc * REF_TOTAL_GAIN * 0.001


if __name__ == "__main__":

    with (open(ORP_RAW_FILE, "r") as ORP_FILE,
          open(PH_RAW_FILE, "r") as PH_FILE,
          open(REF_RAW_FILE, "r") as REF_FILE):
        orps = [0] * AVERAGES
        phs = [0] * AVERAGES
        refs = [0] * AVERAGES

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "mortgage-276004-bd87af0758d7.json"
        client = bigquery.Client()
        table_id = "mortgage-276004.pool1.data_table"

        with open('data.csv', 'w') as f_txt:

            try:
                while True:
                    for i in range(AVERAGES):
                        orps[i] = measure_orp()
                        phs[i] = measure_ph()
                        refs[i] = measure_ref()
                    orp = sum(orps) / AVERAGES
                    ph = sum(phs) / AVERAGES
                    ref = sum(refs) / AVERAGES
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{dt} ORP: {orp:.2f}, pH: {ph:.2f}, ref: {ref:.3f}V")

                    try:
                        requests.post(r'http://localhost/api/CHEM/pH/set', data={'value': ph})
                        requests.post(r'http://localhost/api/CHEM/ORP/set', data={'value': orp})
                    except requests.exceptions.ConnectionError:
                        pass

                    f_txt.write(f"{dt},{orp:.2f},{ph:.2f},{ref:.3f}\n")

                    continue

                    rows_to_insert = [{"dt": dt, "water_temp": 22.5, "orp": orp, "ph": ph}]

                    if errors := client.insert_rows_json(table_id, rows_to_insert):
                        print(f"Encountered errors while inserting rows: {errors}")
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
