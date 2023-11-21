from selenium import webdriver
import pandas as pd
import json

from time import sleep

# Capture network logs

class ExtractAEpChanges:
    def getAEPExtractElements(driver: webdriver):
        log_entries = driver.get_log("performance")
        for log_entry in log_entries:
            data_dict = json.loads(log_entry["message"])
            try:
                if 'interact?' in data_dict['message']['params']['request']['url']:
                    data = data_dict['message']['params']['request']['postData']
                    format = json.loads(data)
                    events_data = format['events'][0]
                    events_df = pd.json_normalize(events_data)
                    print(events_df)
                    melted_df = pd.melt(events_df)
                    # Display the melted DataFrame
                    pd.set_option('display.max_rows', None)
                    print(melted_df)
            except:
                continue



