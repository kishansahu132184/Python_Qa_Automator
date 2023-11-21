# Code to check and install the libs
import subprocess
import sys
import importlib

# List of required libraries
required_libraries = ['customtkinter', 'numpy', 'selenium', 'pandas', 'urllib', 'openpyxl', 'Flask']

# Function to install a library using pip
def install_library(library_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", library_name])

# Check if required libraries are installed and install them if missing
missing_libraries = []

for library in required_libraries:
    try:
        importlib.import_module(library)
    except ImportError:
        missing_libraries.append(library)

# Function to upgrade a library using pip
def upgrade_library(library_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", library_name])
    # subprocess.check_call(['pip', 'install', '--upgrade', library_name])

# Check and upgrade required libraries
for library in required_libraries:
    try:
        upgrade_library(library)
        print(f"{library} has been upgraded.")
    except subprocess.CalledProcessError:
        print(f"Error upgrading {library}.")

print("All required libraries have been checked and upgraded if necessary.")

if missing_libraries:
    print("The following libraries are missing and will be installed:")
    for library in missing_libraries:
        print(library)
        install_library(library)
    print("All required libraries have been installed.")


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import DataExtractionFromDataLayer as dataExtractor
from urllib.parse import urlparse,parse_qs
import re
import json
import os
import customtkinter
import tkinter.messagebox as tkmb 
import validators
from validators import ValidationError
from flask import Flask, render_template, request
import time

# defining global variables
aa_vars_list = []
clickedItems = []
dataUnavailableUrls = []
requestURL = ""
input_url = ""
link = ""
dataLayerSamples = ["adobeDataLayer","digitalData","dataLayer"]

app = Flask(__name__)
# UI of the APP
# customtkinter.set_appearance_mode("dark")
# customtkinter.set_default_color_theme("dark-blue")

# root =customtkinter.CTk()
# root.geometry("500x350")

# frame = customtkinter.CTkFrame(master=root)
# frame.pack(pady=30, padx=60, fill="both", expand=True)

# label= customtkinter.CTkLabel(master=frame, text="Data Extractor")
# label.pack(pady=13, padx=10)

# URL= customtkinter.CTkEntry(master=frame, placeholder_text="Enter the URL to Extract")
# URL.pack(pady=13, padx=10)

# which_Data_To_extract= customtkinter.CTkEntry(master=frame, placeholder_text="Enter the Data to Extract AA or AEP or GA")
# which_Data_To_extract.pack(pady=13, padx=10)

# dataLayer= customtkinter.CTkEntry(master=frame, placeholder_text="Enter the DataLayer integrated in the site")
# dataLayer.pack(pady=13, padx=10)


# Initialize ChromeDriver with the new path
chrome_driver_path = '/Users/kishansahu/Library/Python/3.9/bin/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
# Create a Service object for ChromeDriver
# chrome_driver_service = webdriver.Chrome.service(chrome_driver_path)

driver = webdriver.Chrome(options=options)



class WaitForBSSToAppear(object):
    def __init__(self):
        pass

    def __call__(self):
        network_requests = driver.execute_script(
            "return window.performance.getEntries();")
        for request in network_requests:
            if object in request['name']:
                return True
        return False

class AADataExtraction:
    updateProgress = True
    dataLayerName = ''
    pagesVisited = []
    pagesFailed = []
    totalPages = []
    currentURL = ""
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/render', methods=['POST'])
    def getAAData():

        # techSpec = pd.ExcelFile(r'C:/Users/KishanSahu/Downloads/SDR_QA.xlsx')

        # # Reading the first tab of the excel sheet
        # techSpecDictionary = pd.read_excel(techSpec, 'Sheet1')

        # # Create the output excel to write the output
        # # Fetch the eVars,props and events list
        # aa_vars_list = validator.DefineVariables.analyticsVars()

        url = request.form['url']
        implementation_details = request.form['implementation_details']
        data_layer_name = request.form['data_layer_name']

        if url != "":
            try:
                req = validators.url(url)
            except ValidationError as ex:
                print(f'Something went wrong: {ex}')
                print('Try again!')
                tkmb.showinfo(title="URL Validation",message="URL is correct")
            if req:
                if implementation_details == "AA" or implementation_details == "GA" or implementation_details == "AEP":
                    if data_layer_name != "":
                        print ("\nImplementation Details : ",implementation_details,"\n")
                        driver.get(url)
                        input_link = driver.current_url
                        try:
                            if implementation_details == "AA":
                                AADataExtraction.fetchAANetworkElements(input_link,AADataExtraction.pagesVisited)
                            elif implementation_details == "AEP":
                                AADataExtraction.fetchAEPNetworkChanges(input_link,AADataExtraction.pagesVisited)
                            elif implementation_details == "GA":
                                AADataExtraction.fetchGANetworkChanges(input_link,AADataExtraction.pagesVisited)
                            else:
                                print("get GA changes")
                            # Find a clickable link in the page and click to move to the next page
                            AADataExtraction.clickByXPATH(input_link,implementation_details, data_layer_name)
                        except Exception as ex:
                            print(f'Exception = {ex}')
                            driver.quit
                    else:
                        print('Please Enter your Datalayer to proceed')
                else:
                    print('Please Enter your Implementation Details in correcct format either AA or GA or AEP')
            else:
                print('Please Enter the correct URl to proceed')
        else:
            print('Please Enter your URl to proceed')  
        
        # input_url = 
        

        # return True
    
   
    def fetchAANetworkElements(input_link, pagesCrawled):
        # taken only pageload call using adobeDatalayer[0]
        isHomePagePassed = "Fail"
        if driver.current_url == input_link:
            isHomePagePassed = "Fail"
        else:
            isHomePagePassed = "Pass"
        try:
            WebDriverWait(driver, 30).until(WaitForBSSToAppear())
        except Exception:
            print("Timed out waiting for the 'b/ss' server call")
        AADataExtraction.pagesVisited.append(driver.current_url)
        # Get all the captured network requests
        network_requests = driver.execute_script(
                    "return window.performance.getEntries();")
        dataValues = pd.DataFrame()
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
                    networkCall = dataExtractor.DataExtraction.getAdobeDataDedicated(
                            request["name"])
                    if len(dataValues) > 0:
                        dataValues = pd.concat([dataValues,pd.DataFrame(networkCall)], ignore_index=True)
                    else:
                        dataValues = pd.DataFrame(networkCall)
        AADataExtraction.printComparisionResult(
                    dataValues, input_link, pagesCrawled, dataUnavailableUrls, isHomePagePassed)            

    def fetchAEPNetworkChanges(input_link, pagesCrawled):
        # taken only pageload call using adobeDatalayer[0]
        isHomePagePassed = "Fail"
        if driver.current_url == input_link:
            isHomePagePassed = "Fail"
        else:
            isHomePagePassed = "Pass"
        pagesCrawled.append(driver.current_url)
        log_entries = driver.get_log("performance")
        for log_entry in log_entries:
            data_dict = json.loads(log_entry["message"])
            try:
                if 'interact?' in data_dict['message']['params']['request']['url']:
                    data = data_dict['message']['params']['request']['postData']
                    format = json.loads(data)
                    events_data = format['events'][0]
                    events_df = pd.json_normalize(events_data)
                    # print(events_df)
                    melted_df = pd.melt(events_df)
                    # Display the melted DataFrame
                    pd.set_option('display.max_rows', None)
                    melted_df = pd.DataFrame(melted_df)
                    # print(melted_df)
                    AADataExtraction.printComparisionResult(
                        melted_df, input_link, pagesCrawled, dataUnavailableUrls,isHomePagePassed)
            except:
                continue
    
    def fetchGANetworkChanges(input_link, pagesCrawled):
        # 
        isHomePagePassed = "Fail"
        if driver.current_url == input_link:
            isHomePagePassed = "Fail"
        else:
            isHomePagePassed = "Pass"
        # adobeDataLayer = dataExtractor.DataExtraction.dataExtraction(isThisTheCurrentURL, driver, dataLayer)
        # if adobeDataLayer == "Datalayer doesn't persist":
        #     dataUnavailableUrls.append(driver.current_url)
        #     print(dataUnavailableUrls)
        pagesCrawled.append(driver.current_url)
        network_requests = driver.execute_script(
                    "return window.performance.getEntries();")
        for request in network_requests:
            request_url = request['name']
            if "https://analytics.google.com/g/collect?v=2" in request_url:
                parsed_url = urlparse(request_url)          
                # Get the query string parameters as a dictionary
                query_params = parse_qs(parsed_url.query)
                # Convert the dictionary to a Pandas DataFrame
                df = pd.DataFrame(query_params)        
                # Print the DataFrame
                #print(df)
                melted_df = pd.melt(df)
                # # Display the melted DataFrame
                # print(melted_df)
                AADataExtraction.printComparisionResult(
                    melted_df, input_link, pagesCrawled, dataUnavailableUrls, isHomePagePassed)                      
    
    # Move to next page with Clickable URL finder by using xPath
    def clickByXPATH(input_link,implementationDetails, dataLayer):
            # We also have to add a filter if the clickable url is internal or external
        elements = driver.find_elements(By.TAG_NAME, "a")
        if(len(elements) == 0):
            driver.back
        # print("input link" + input_link)
        elements_to_drive = []
        for element in elements:
            href = element.get_attribute('href')
            elements_to_drive.append(href)
            # print(href)
            
        for element in elements_to_drive:
            print(element)
            try:
                parsedURl = urlparse(element)
                inputlink = urlparse(input_link)
                if (element not in clickedItems and 
                    parsedURl.netloc == inputlink.netloc
                    and ".pdf" not in element):
                    clickedItems.append(element)
                    driver.get(element)
                    driver.implicitly_wait(5)
                    if implementationDetails == "AA":
                        AADataExtraction.fetchAANetworkElements(input_link, AADataExtraction.pagesVisited)
                    elif implementationDetails == "AEP":
                        AADataExtraction.fetchAEPNetworkChanges(input_link, AADataExtraction.pagesVisited)
                    elif implementationDetails == "GA":
                        AADataExtraction.fetchGANetworkChanges(input_link, AADataExtraction.pagesVisited)
                else:
                    continue
            except Exception:
                continue
        # print("pages Crawled"+len(clickedItems) +"Pages missed" + len())
        updateProgress = False
        # driver.quit()


    def driverQuit():
        driver.quit()


    def getDataLayer(dataLayerSamples, isThisTheCurrentURL):
        adobeDataLayer = ""
        # 
        for dataLayer in dataLayerSamples:
            try:
                adobeDataLayer = driver.execute_script(f"return {dataLayer}")  
                if(adobeDataLayer != None and adobeDataLayer !='' and adobeDataLayer !=[]):
                    print(adobeDataLayer)
                    AADataExtraction.dataLayerName = dataLayer
                    break
                else:
                    continue
                    # AADataExtraction.getDataLayer(dataLayerSamples,isThisTheCurrentURL)

                    # return dataLayerJSON   
            except Exception as ex:
                print(f'Something went wrong: {ex}')
                print('Try again!')
                if len(dataLayerSamples) > 1:
                    dataLayerSamples.pop(0)    
                    AADataExtraction.getDataLayer(dataLayerSamples,isThisTheCurrentURL)
                elif isThisTheCurrentURL == "Pass":
                    dataUnavailableUrls.append(driver.current_url)
                    print(dataUnavailableUrls)
                    pass
                else:
                    tkmb.showwarning(title='Wrong Input',message='Please Enter your Datalayer to proceed')
                    break
        

    def printComparisionResult(dataFrame, input_link, pagesCrawled, dataUnavailableUrls, isHomePagePassed):
        prod = dataFrame
        
        if isHomePagePassed != "Pass":
            AADataExtraction.getDataLayer(dataLayerSamples, isHomePagePassed)
        
        try:
            dataLayerJSON = json.dumps(driver.execute_script(f"return {AADataExtraction.dataLayerName}"))
            dataLayer_new=json.loads(dataLayerJSON)
            # print(dataLayer_new)
            dataLayer_dl_df = pd.DataFrame(pd.json_normalize(dataLayer_new))
            melted_dl_df = pd.melt(dataLayer_dl_df)
            # print(melted_dl_df)
            
            result = pd.concat([melted_dl_df, prod], axis=1)
            
            print(result)
                
                # write dataframe to excel and name the sheet name as pagename
            
            pageName = driver.execute_script("return document.title")
            pageName = re.sub(r'[/?*\[\]:]', '_', pageName)

            df1=pd.DataFrame(dataUnavailableUrls)
            df2=pd.DataFrame({"No. of Pages":len(pagesCrawled)},index=[0])
            df3=pd.DataFrame(pagesCrawled)
        
            with pd.ExcelWriter("./Output.xlsx", mode="a", engine="openpyxl", if_sheet_exists='replace') as writer:
                result.to_excel(writer, sheet_name=pageName)
                df3.to_excel(writer, sheet_name='URLs')
                # df2.to_excel(writer, sheet_name='pages crawled')
                df1.to_excel(writer, sheet_name='dataUnavailableUrls')
                # writer.close()
        except Exception as ex:
            print(f'Exception = {ex}') 
            pageName = driver.execute_script("return document.title")
            pageName = re.sub(r'[/?*\[\]:]', '_', pageName)
            excel_exist = os.path.exists('./Output.xlsx')
            if excel_exist:
                with pd.ExcelWriter("Output.xlsx", mode="a", engine="openpyxl", if_sheet_exists='replace') as writer:
                    prod.to_excel(writer, sheet_name=pageName)
                    # writer.close()
            else:
                prod.to_excel("Output.xlsx", sheet_name=pageName) 
                pass
        finally:
            pass

if __name__ == "__main__":
    app.run()
    print("call when import")
# 






# def initiateTheExtractionProcess():
    
#     input_url = URL.get()
#     datalayer = dataLayer.get()
#     implementationDetails = which_Data_To_extract.get()
    
#     if input_url != "":
#         try:
#             req = validators.url(input_url)
#         except ValidationError as ex:
#             print(f'Something went wrong: {ex}')
#             print('Try again!')
#             tkmb.showinfo(title="URL Validation",message="URL is correct")
#         if req:
#             if implementationDetails == "AA" or implementationDetails == "GA" or implementationDetails == "AEP":
#                 if datalayer != "":
#                     print ("\nImplementation Details : ",implementationDetails,"\n")
#                     button1.configure(state="disabled")
#                     URL.configure(state="disabled")
#                     which_Data_To_extract.configure(state="disabled")
                    
#                     AADataExtraction.getAAData(input_url,implementationDetails, datalayer)
#                 else:
#                     tkmb.showwarning(title='Wrong Input',message='Please Enter your Datalayer to proceed')
#             else:
#                 tkmb.showwarning(title='Wrong Input',message='Please Enter your Implementation Details in correcct format either AA or GA or AEP')
#         else:
#             tkmb.showwarning(title='Validation Failed',message='Please Enter the correct URl to proceed')
#     else:
#         tkmb.showwarning(title='Wrong Input',message='Please Enter your URl to proceed')  

   
# # def updateUi(clickedItem):
# #     print(len(clickedItems))

# def closeTheProgress():
#     AADataExtraction.driverQuit()

# button1= customtkinter.CTkButton(master=frame, text="Start", command=initiateTheExtractionProcess)
# button1.pack(pady=13, padx=30, side=customtkinter.LEFT)

# button3= customtkinter.CTkButton(master=frame, text="Close", command=closeTheProgress)
# button3.pack(pady=13, padx=30, side=customtkinter.LEFT)

# root.mainloop()