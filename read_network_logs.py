#import selenium and other libraries
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json



if __name__ == "__main__":
    desired_capabilities = DesiredCapabilities.CHROME
    print(desired_capabilities)
    #desired_capabilities["goog:loggingPrefs"] = {"performance":"ALL"}

