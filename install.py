# Created for using script standalone by team
# Open with admin rights always!
import subprocess
import os
import zipfile
import time
import win32gui
import win32con


def unzip_file(zip_file_path, extract_to_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
        print("Installation files extracted successfully!")
    except Exception as e:
        print("Error during extraction of files!", e)


# Creating dynamic file path
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, "Android.zip")

zip_file_path = file_path
local_app_data_path = os.environ['LOCALAPPDATA']

if not os.path.exists(local_app_data_path):
    os.makedirs(local_app_data_path)


def set_environment_variable(name, value):
    subprocess.run(['setx', name, value])
    os.environ[name] = value


if __name__ == "__main__":
    android_sdk_path = (local_app_data_path + r"\Android\Sdk")

print("SV_monitoring AUTOTST installer")
print("Be sure to install python first!")
choice = int(input("To continue type 1: "))

if choice == 1:
    # Installing dependencies
    subprocess.run(["pip", "install", "-r", "requirements.ini", "--user"])
    # New cmd with appium installation
    appium_instalation = subprocess.Popen('start "appium_installation" npm install appium', shell=True)
    while appium_instalation.poll() is None:
        time.sleep(1)
    if appium_instalation.returncode == 0:
        # If installation of appium proceeded opening plugin installation window
        appium_window_handle = None
        while not appium_window_handle:
            appium_window_handle = win32gui.FindWindow(None, "Administrator: appium_installation")
            time.sleep(1)
    else:
        print("Appium installation failed!")

    # Closing window after found
    if appium_window_handle:
        win32gui.PostMessage(appium_window_handle, win32con.WM_CLOSE, 0, 0)
        print("Appium window closed!")

    uiautomator2_installation = subprocess.run(
        'start "uiautomator2_installation" npm exec appium driver install uiautomator2', shell=True)
    # Hanlding auto-closing of windows
    if uiautomator2_installation.returncode == 0:
        uiautomator2_installation_handle = None
        while not uiautomator2_installation_handle:
            uiautomator2_installation_handle = win32gui.FindWindow(None, "Administrator: uiautomator2_installation")
            time.sleep(1)
        if uiautomator2_installation_handle:
            win32gui.PostMessage(uiautomator2_installation_handle, win32con.WM_CLOSE, 0, 0)
            print("UIautomator2 window closed!")
        else:
            print("UIautomator2 installation window not found!")
    else:
        print("UIautomator2 installation failed!")

    print("Requirements installed!")
    print("Installing Android SDK...")
    unzip_file(zip_file_path, local_app_data_path)
    time.sleep(2)
    set_environment_variable('ANDROID_HOME', android_sdk_path)
    print("Closing...")
else:
    print("Wrong number selected!")
