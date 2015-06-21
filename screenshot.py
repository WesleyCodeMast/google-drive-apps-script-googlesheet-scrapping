from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import requests
from time import sleep
import loginFormDR_up
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
from selenium.webdriver.chrome.options import Options

screenshot_path = ".\screenshot.png"

def login():
    # Set Chrome options to start the browser in full screen mode
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # Set the path to your ChromeDriver executable
    s = Service('D:\programs\chromedriver_win32\chromedriver.exe')

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=chrome_options, service=s)

    # Navigate to the login page
    driver.get("https://app.formdr.com/login")
    sleep(6)
    # Find the username and password input fields and enter your credentials
    username_input = driver.find_element("name", "email")
    password_input = driver.find_element("name", "password")

    username_input.send_keys("admin@oregonfirstresponderevals.com")
    password_input.send_keys("Packets66!")

    # Submit the login form
    password_input.send_keys(Keys.RETURN)

    # Wait for the page to load after login (adjust the sleep time or use WebDriverWait)
    sleep(7)

    return driver

def screenshot_signature(driver, candidate_name):

# Search for a custom value in the table
# You need to implement your logic to locate and interact with the table based on the custom value

# Click on the item in the table
# You need to implement your logic to click the item based on your search

# Wait for the tabs to appear after clicking the item (adjust the sleep time or use WebDriverWait)

    driver.get("https://app.formdr.com/submissions")
    sleep(5)
    elements = driver.find_elements(By.CSS_SELECTOR, ".MuiInputBase-input.MuiInput-input.MuiInputBase-inputAdornedEnd")
    if len(elements) == 2:
        search_input = elements[1]
    else:
        search_input = None
    search_input.send_keys(candidate_name)

    elements = driver.find_elements(By.CSS_SELECTOR, ".MuiInputAdornment-root.MuiInputAdornment-positionEnd")
    if len(elements) == 2:
        start_search_icon = elements[1]
        start_search_icon.click()
    else:
        print("There is no search icon")
        return None
    sleep(5)

    elements = driver.find_elements(By.CSS_SELECTOR, ".name-container.formdr-flex-grow")
    if len(elements) > 0:
        candidate_item = elements[0]
    else:
        print("there is no candidate with such name")
        return None
    
    candidate_item.click()
    sleep(4)

    tabs = driver.find_elements(By.CSS_SELECTOR, ".MuiButtonBase-root.MuiTab-root.MuiTab-textColorInherit.sc-iUuytg.esdhrP")
    if len(tabs) < 6:
        print("There are no 6 tabs")
        return None
    background_tab = tabs[5]

    background_tab.click()
    sleep(1)
    elements = driver.find_elements(By.CSS_SELECTOR, ".fd-field-item.field-type-group")

    ROI_form = None
    element_title = None
    # element_title = driver.find_element(By.XPATH("//h2[contains(text(), 'AUTHORIZATION FOR RELEASE OF HEALTH INFORMATION')]"))
    for container in elements:
        sleep(1)
        try:
            container_title_element = container.find_element(By.TAG_NAME, "h2")
            container_title = container_title_element.text
            if container_title == "AUTHORIZATION FOR RELEASE OF HEALTH INFORMATION":
                ROI_form = container
                element_title = container_title_element
                break
            else:
                continue
        except:
            continue
    if ROI_form == None:
        child_elements = driver.find_elements(By.CSS_SELECTOR, 'h2.fd-field-item-title[style="font-size: 30px; text-align: left;"]')
        for element in child_elements:
            if element.text == "AUTHORIZATION FOR RELEASE OF HEALTH INFORMATION":
                element_title = element
    if element_title:
        location = element_title.location
        size = element_title.size
        
        # Crop the screenshot to include only the desired element

        top = location['y']

        driver.execute_script("window.scrollTo(0, arguments[0]);", top-65)  # Replace 345 with the Y-coordinate of the element
        sleep(2)
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        screenshot.save(screenshot_path)
        # Open the saved screenshot using PIL
        element_screenshot_opened = Image.open(screenshot_path)
        element_screenshot_opened.show()  # Display the image
        # signature_screenshot = screenshot.crop((left, top, right, bottom))
        
        # signature_screenshot.save(screenshot_path)

        # # Convert the cropped screenshot to BytesIO
        # element_screenshot_bytes = BytesIO()
        # signature_screenshot.save(element_screenshot_bytes, format='PNG')
        # element_screenshot_bytes.seek(0)  # Reset the BytesIO cursor to the beginning
        driver.quit()
        return screenshot_path
        # return element_screenshot_bytes.read()
    else:
        
        driver.quit()
        return None

# Close the browser

if __name__ == "__main__":
    driver = login()

    screenshot_signature(driver, "Cara Pszczolkowski")