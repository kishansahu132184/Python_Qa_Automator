from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import numpy as np
import URLValidation as validator
import DataExtractionFromDataLayer as dataExtractor
from openpyxl import load_workbook
import re
import json
# from selenium.webdriver.chrome.service import Service as ChromeService

# defining global variables
aa_vars_list = []
clickedItems = []
requestURL = ""
url_list = []
link = ""
driver = webdriver.Chrome()


class WaitForBSSToAppear(object):
    def __init__(self):
        pass

    def __call__(self, driver):
        network_requests = driver.execute_script(
            "return window.performance.getEntries();")
        for request in network_requests:
            if "interact" in request['name']:
                return True
        return False


    
# Move to next page with Clickable URL finder by using xPath
def clickByXPATH(driver):
        # We also have to add a filter if the clickable url is internal or external
        elements = driver.find_elements(By.XPATH, "//a | //button")
        for element in elements:
            try:
                if (element.get_attribute("href") not in clickedItems and element.get_attribute("href").startswith(link)):
                    try:
                        # print(element.get_attribute("href"))
                        clickedItems.append(element.get_attribute("href"))
                        driver.get(element.get_attribute("href"))
                        fetchTheNetworkElementsForEachPage()
                    except  :
                        pass
                else:
                    pass
            except Exception:
                pass



def remove_square_brackets(data):
    if isinstance(data, list):
        if len(data) >= 1:
            return remove_square_brackets(data[0])
        else:
            if len(data) == 0:
                # return [remove_square_brackets(item) for item in data]
                return ''
    elif isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[key] = remove_square_brackets(value)
        return new_data
    else:
        return data
    
# # This function will be used to write the excel outputs
# def getPageName(combined_df):
#     pageName = ""
#     for i in range(len(combined_df)):
#         row = combined_df.loc[i]
#         if "pageName" in row['Datalayer']:
#             pageName = row['key_value']
#             print(f"Row {i}: Datalayer={row['Datalayer']}, key_value={row['key_value']}")
#             break
#     pageName = re.sub(r'[/?*\[\]:]', '_', pageName)
    
#     return pageName


def printComparisionResult(request_URL, dataLayer, driver):
        dataValues = dataExtractor.DataExtraction.getAdobeDataDedicated(
            request_URL)
        prod = pd.DataFrame(dataValues)
        print(prod)
        
        new_dict = remove_square_brackets(dataLayer)
        # json_normalize() to flatten the simple to moderately semi-structured nested JSON structures to flat tables
        df = pd.json_normalize(new_dict, sep='.')
        # seperating the flattened semi-dict into two coloumns,used melt to segregate
        df = df.melt(var_name='Datalayer', value_name='key_value')
        # bypassing the pandas and making expanded rows
        pd.set_option('display.max_rows', None)
        # now dictionary is been flattened adding "adobeDataLayer." to "Datalayer" coloumn as a constant across all rows
        df['Datalayer'] = "adobeDataLayer." + df['Datalayer']
        # using left join keeping structure as a base
        # df3 = techSpecDictionary.merge(
        #         df, on='Datalayer', how='left')
        # # after extracted DL values are mapped to base, now checking for eg : lets say some extra var populating in extracted data layer now after mapping to the base nan will be coming so removed that for clean look
        # df3['key_value'] = df3['key_value'].replace(np.nan, '')
        # # now at this place creating another df to basically hide the datalayer coloumn and making evar/props and keyvalue visible so to map this table with network call.
        # uat = df3[['eVar/Prop', 'key_value']]
        # print(uat)
        # print(pd.DataFrame(dataValues))

        result = pd.concat([df, prod], axis=1)
        # result['result'] = np.where(result['key_value'] !=
        #                             result['values_prod'], False, True)
        print(result)
        
        # write dataframe to excel
      
        pageName = driver.execute_script("return document.title")
        pageName = re.sub(r'[/?*\[\]:]', '_', pageName)
        try:
            with pd.ExcelWriter("/Users/kishansahu/Documents/Output.xlsx", mode="a", engine="openpyxl") as writer:
                result.to_excel(writer, sheet_name=pageName) 
        # with pd.ExcelWriter('/Users/kishansahu/Desktop/Python_Qa_Automator/Output.xlsx', engine='openpyxl', mode='a') as writer:
        #     writer.book = load_workbook('/Users/kishansahu/Desktop/Python_Qa_Automator/Output.xlsx')
        #     combined_df.to_excel(writer, index=False, sheet_name=pageName)
        except Exception as ex:
            print(f'Exception = {ex}') 
            result.to_excel('/Users/kishansahu/Documents/Output.xlsx', sheet_name=pageName)
            pass
        
        # Find a clickable element and click the link to land on the next page
        clickByXPATH(driver)



def getAADetails():
    # # sys.path.insert(0,'C:/Users/KishanSahu')
    # chrome_driver_path = '/Users/kishansahu/Library/Python/3.9/bin/chromedriver'
    # chrome_sevice = ChromeService(chrome_driver_path)
    # chrome_sevice.start()

    chrome_driver_path = '/Users/kishansahu/Library/Python/3.9/bin/chromedriver'

    # Initialize ChromeDriver with the new path
    # driver = webdriver.Chrome(executable_path=chrome_driver_path)

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    driver = webdriver.Chrome(executable_path=chrome_driver_path,options=options)
    # Extract the values from the tech spec
    # Defining the path of the excel
    techSpec = pd.ExcelFile(r'/Users/kishansahu/Downloads/SDR_QA.xlsx')

    # Reading the first tab of the excel sheet
    techSpecDictionary = pd.read_excel(techSpec, 'Sheet1')

    # Create the output excel to write the output
    # Fetch the eVars,props and events list
    aa_vars_list = validator.DefineVariables.analyticsVars()

    url = validator.Validation.valid_url(
            input("Please enter the website url : "))
    driver.get(url)
    link = driver.current_url
    try: 
        # taken only pageload call using adobeDatalayer[0]
        adobeDataLayer = dataExtractor.DataExtraction.dataExtraction("adobeDataLayer", driver)
        
        # Wait for the "b/ss" string-based server call
        try:
                WebDriverWait(driver, 30).until(WaitForBSSToAppear())
        except Exception:
                print("Timed out waiting for the 'b/ss' server call")

        # Get all the captured network requests
        network_requests = driver.execute_script(
                "return window.performance.getEntries();")
        for request in network_requests:
            request_url = request['name']
            if "b/ss" in request_url or "interact" in request_url:
                domainName = dataExtractor.DataExtraction.getQueryParamsValue(
                        request_url, "g")
                if driver.current_url in domainName:
                    if ("pe: lnk_o" in requestURL):
                            print("Link Click call")
                    else:   
                            print("Page View call")
                    print("*" * 50)
                    printComparisionResult(
                    request["name"], adobeDataLayer, driver)

        # Find a clickable link in the page and click to move to the next page
        clickByXPATH(driver)
    except Exception as ex:
        print(f'Exception = {ex}')
        driver.quit

getAADetails()

