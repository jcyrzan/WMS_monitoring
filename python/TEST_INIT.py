from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import config
import os
import subprocess
# For W3C actions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
# Creating dynamic file path
current_directory = os.path.dirname(os.path.abspath(__file__))
apk_path = os.path.join(current_directory, config.apk_dc2_path)


# Used for uploading config onto device
def upload_file_to_device(local_file_path, device_directory):
    try:
        # ADB command
        adb_command = f"adb push {local_file_path} {device_directory}"

        # Executing ADB command
        subprocess.run(adb_command, shell=True, check=True)
        # Printing results
        print(f"File '{local_file_path}' uploaded to '{device_directory}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Used to kill apk without Appium on the start
def check_and_kill_app(package_name):
    try:
        # Getting list of processes
        adb_command = "adb shell ps"
        process = subprocess.Popen(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Converting output to string and splitting it into lines
        output = output.decode("utf-8")
        lines = output.strip().split('\n')

        # Checking does APK works
        for line in lines:
            if package_name in line:
                pid = line.split()[1]
                print(f"App '{package_name}' is running with PID {pid}. Killing...")

                # Force-stop instead of kill bcs of no-root, using package name
                subprocess.run(f"adb shell am force-stop {package_name}", shell=True, check=True)
                print(f"App '{package_name}' killed successfully.")
                return

        print(f"App '{package_name}' is not running.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


options = AppiumOptions()
options.load_capabilities({
    "platformName": "Android",
    "appium:platformVersion": "11.0",
    "appium:deviceName": "XX",
    "appium:automationName": "uiautomator2",
    "appium:appActivity": ".screen.configuration.xx",
    "appium:appPackage": "com.xx.android.xxx.xx",
    "appium:ensureWebviewsHavePages": True,
    "appium:nativeWebScreenshot": True,
    "appium:newCommandTimeout": 3600,
    "appium:connectHardwareKeyboard": True,
    "appium:autoGrantPermissions": True,
    "appium:app": apk_path
})

package_name_wms = "com.wms.xxx.xxx.xxx"
check_and_kill_app(package_name_wms)

package_name_sv = "'com.xxx.android.xxx.xxx'"
check_and_kill_app(package_name_sv)


if config.select_apk == "1":
    local_file_path = os.path.join(current_directory, "mdt4.ini")
    device_directory = "/sdcard/Download/xx/"
    upload_file_to_device(local_file_path, device_directory)
else:
    current_directory_up = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_file_path = os.path.join(current_directory_up, "mdt4.ini")
    device_directory = "/sdcard/Download/xx/"
    upload_file_to_device(local_file_path, device_directory)
# Initializing driver
driver = webdriver.Remote("http://localhost:4723", options=options)


def test_preparing_app_to_work():

    def wait_for_element(driver, timeout, locator):
        try:
            element = WebDriverWait(driver, timeout).until(ec.presence_of_element_located(locator))
            return element
        except TimeoutException:
            return None

    # Waiting for proper initialization
    time.sleep(3)
    # Touch action for reloading DOM
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(362, 551)
    actions.w3c_actions.pointer_action.pointer_down()
    actions.w3c_actions.pointer_action.pause(0.1)
    actions.w3c_actions.pointer_action.release()
    actions.perform()
    time.sleep(2)
    # Waiting for reload button
    locator = (By.XPATH, '//android.widget.Button[@text=" Reload "]')
    element = wait_for_element(driver, 10, locator)
    time.sleep(1)
    if element:
        print("Reloading...")
        reload_button_xpath = '//android.widget.Button[@text=" Reload "]'
        reload_button = driver.find_element(By.XPATH, reload_button_xpath)
        if reload_button:
            # Executing reload
            driver.find_element(By.XPATH, '//android.widget.Button[@text=" Reload "]').click()
            if reload_button:
                print("Error with logging in! Check server/internet/vpn status!")
        else:
            time.sleep(1)
    else:
        print("Proceeding login...")
        # If hourglass located, problems with changing stoNam if did - restarting
        locator = (By.XPATH, '//android.widget.Image[@text="hourglass"]')
        element = wait_for_element(driver, 2, locator)
        time.sleep(1)
        if element:
            print("Restarting due to problems with changing stoNam...")
            driver.terminate_app('com.wms.xxx.xxx.mobile')
            driver.terminate_app('com.xxx.android.xxx.xxx')
            driver.activate_app('com.xxx.android.xxx.xxx')
            time.sleep(2)


assert 1 == 1
time.sleep(1)
