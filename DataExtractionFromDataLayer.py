import URLValidation as validator
from urllib.parse import urlparse, parse_qs
from selenium import webdriver


class DataExtraction:
    
    def dataLayerCheck(dataLayerNameList: list, driver: webdriver, isHomePagePassed: str):
        adobeDataLayer = "";
        for dataLayerName in dataLayerNameList:
            try:
                adobeDataLayer = driver.execute_script(f"return {dataLayerName}")
                if len(adobeDataLayer) > 0:
                    return adobeDataLayer
                else:
                    continue       
            except Exception as ex:
                print(f'Something went wrong: {ex}')
                print('Try again!')
                if isHomePagePassed == "Pass":
                    return "Datalayer doesn't persist"
                else:
                    continue
        if adobeDataLayer == "" and isHomePagePassed == "Pass":
            return "Datalayer doesn't persist"
        else:
            return DataExtraction.dataLayerCheck(dataLayerNameList.append(input("Please enter the datalayer: ")), driver, isHomePagePassed)
    
    def dataExtraction(isHomePagePassed, driver):
        dataLayerSamples = ["adobeDataLayer","digitalData","dataLayer"]
        adobeDataLayer = DataExtraction.dataLayerCheck(
            dataLayerSamples, driver, isHomePagePassed)
        return adobeDataLayer

    def getAdobeDataDedicated(request_URL):
        # url_list.append(request_URL)
        aa_vars_list = validator.DefineVariables.analyticsVars()
        keys = []
        values = []
        # Parse the URL string into a URL object
        parsed_url = urlparse(request_URL)
        # Extract query parameters as a dictionary
        query_params = parse_qs(parsed_url.query)

        for key, value in query_params.items():
            if key in aa_vars_list:
                keys.append(key)
                values.append(value[0])

        # Adding variables and value to the dataframe
        dataValues = {'eVar/Prop': keys, 'values_prod': values}

        return dataValues

    def getQueryParamsValue(request_URL, keyValue):
        # url_list.append(request_URL)
        aa_vars_list = validator.DefineVariables.analyticsVars()
        variables = []
        values = []
        # Parse the URL string into a URL object
        parsed_url = urlparse(request_URL)
        # Extract query parameters as a dictionary
        query_params = parse_qs(parsed_url.query)

        return query_params[keyValue][0]
