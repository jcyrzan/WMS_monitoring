from TEST_INIT import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from PIL import Image, ImageTk
from barcode.writer import ImageWriter
from io import BytesIO
from barcode import generate
import time
import config
import SQL
# Deprecated
# import cx_Oracle
import oracledb
import os
import subprocess
import shutil
import barcode
import tkinter as tk
# For W3C actions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

if config.select_apk == '1':
    connection = oracledb.connect(
            user=config.username_dc2,
            password=config.password_dc2,
            dsn=config.db_ip_dc2 + "/" + config.sid_dc2)
# port=config.port_dc2)
# encoding=config.encoding)
    print(connection)
elif config.select_apk == '2':
    connection = oracledb.connect(
            user=config.username_dc4,
            password=config.password_dc4,
            dsn=config.db_ip_dc4 + "/" + config.sid_dc4)
# port=config.port_dc4)
    print(connection)

number1 = 1


def empty_folder(directory):
    try:
        # Checking directory
        if not os.path.isdir(directory):
            print(f"'{directory}' isn't proper directory!")
            return

        # Removing files from directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        print(f"Files from '{directory}' deleted succesfully!")
    except Exception as e:
        print("Error:", e)


def delete_folder(folder_path, device_id=None):
    try:
        # Get the path to adb.exe using the LOCALAPPDATA environment variable
        adb_path = os.path.join(os.environ['LOCALAPPDATA'], "Android", "Sdk", "platform-tools", "adb.exe")

        # ADB command
        adb_command = [adb_path, "shell", "rm", "-rf", folder_path + "/*"]

        # DEVICEID option
        if device_id:
            adb_command.insert(1, "-s")
            adb_command.insert(2, device_id)

            # Executing ADB
        result = subprocess.run(adb_command, capture_output=True, text=True)

        # Checking results
        if result.returncode == 0:
            print("Files deleted!")
            return True
        else:
            print("Deleting error!")
            print(result.stderr)
            return False
    except Exception as e:
        print("ADB error!", e)
        return False


def trigger_button(driver):
    # Trigger for virtualized scan button
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(1008, 1666)
    actions.w3c_actions.pointer_action.pointer_down()
    actions.w3c_actions.pointer_action.pause(0.5)
    actions.w3c_actions.pointer_action.release()
    actions.perform()


def generate_barcode(tenam):
    # Barcode generator
    if config.select_apk == '1':
        ean = barcode.get_barcode_class('code128')
        my_ean = ean(tenam, writer=ImageWriter())
        fp = BytesIO()
        my_ean.write(fp)
        code128 = barcode.get_barcode_class('code128')
        my_ean13 = code128(tenam, writer=ImageWriter())
        my_ean13.save(config.barcodes_path_dc2 + '\\' + tenam)
        generate('code128', tenam, writer=ImageWriter(), output=fp)
    else:
        ean = barcode.get_barcode_class('code128')
        my_ean = ean(tenam, writer=ImageWriter())
        fp = BytesIO()
        my_ean.write(fp)
        code128 = barcode.get_barcode_class('code128')
        my_ean13 = code128(tenam, writer=ImageWriter())
        my_ean13.save(config.barcodes_path_dc4 + '\\' + tenam)
        generate('code128', tenam, writer=ImageWriter(), output=fp)


def show_image(image_path, x, y, duration=None, pointer_actions=None):
    # Showing generated barcode
    root = tk.Tk()
    root.geometry("+{}+{}".format(x, y))

    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(root, image=photo)
    label.image = photo
    label.pack()

    if duration:
        root.after(duration * 1000, root.destroy)
        if pointer_actions:
            root.after(int(duration / 2 * 1000), pointer_actions)

    root.mainloop()


def create_folder_if_not_exists(folder_name, location):
    folder_path = os.path.join(location, folder_name)
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_name}' created at location '{location}'.")
        except OSError as e:
            print(f"Error creating folder: {e}")
    else:
        print(f"Folder '{folder_name}' already exists at location '{location}'.")


def execute_sql(connection, querry, par1, par2=None):
    execute_sql_result = None
    try:
        cur = connection.cursor()
        if par2 is not None:
            cur.execute(querry, str=par1, num=par2)
        else:
            cur.execute(querry, str=par1)
        connection.commit()
        result = cur.fetchall()
        # Fetch the data before closing the cursor
        execute_sql_result = result if result else None
        # Diagnostics
        # print("Results fetched! LoadId:", execute_sql_result)
    except oracledb.Error as error:
        print(f"Błąd wykonania SQL: {error}")
    finally:
        # Diagnostics
        # print("Results fetched! Moving along...")
        time.sleep(1)
    return execute_sql_result


deleting_parameter_mdt = int(input("Do you want to delete files from MDT? 1 - Yes, 2 - No : "))
deleting_parameter_api = int(input("Do you want to delete files from API? 1 - Yes, 2 - No : "))
# Checking folders if not present - creating

create_folder_if_not_exists("BARCODES", "C:\\")
create_folder_if_not_exists("DC2", "C:\\BARCODES\\")
create_folder_if_not_exists("DC4", "C:\\BARCODES\\")
create_folder_if_not_exists("SV_MONITORING", "C:\\")

# Deleting old files
if config.select_apk == '1':
    barcodes = r"C:\BARCODES\DC2"
else:
    barcodes = r"C:\BARCODES\DC4"
downloaded_images = r"C:\SV_MONITORING"
if config.select_apk == '1':
    API_files = config.api_path_dc2
else:
    API_files = config.api_path_dc4
empty_folder(downloaded_images)
if deleting_parameter_api == 1:
    empty_folder(API_files)
    print("Files from API deleted!")
else:
    print("Files from API preserved!")
empty_folder(barcodes)
if deleting_parameter_mdt == 1:
    folder_path = "/sdcard/ImageCapture/PackVerf_Images"
    device_id = config.device_id
    delete_folder(folder_path, device_id)
    print("Files from device deleted!")
elif deleting_parameter_mdt == 2:
    print("Files from device preserved!")
else:
    print("Wrong number selected!")


def test_info_jt():
    global number1

    def wait_for_element(driver, timeout, locator):
        try:
            element = WebDriverWait(driver, timeout).until(ec.presence_of_element_located(locator))
            return element
        except TimeoutException:
            return None

    locator = (By.XPATH, '//android.widget.Image[@text="user"]')
    element = wait_for_element(driver, 5, locator)
    # Logging in section
    if element:
        time.sleep(1)
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(999, 286)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(999, 286)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        if config.select_apk == '1':
            actions.send_keys(config.mdt_login_dc2)
            actions.perform()
        else:
            actions.send_keys(config.mdt_login_dc4)
            actions.perform()
        time.sleep(1)
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(1002, 444)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        if config.select_apk == '1':
            actions.send_keys(config.mdt_password_dc2)
            actions.perform()
        else:
            actions.send_keys(config.mdt_password_dc4)
            actions.perform()
        time.sleep(1)
        driver.hide_keyboard()
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(959, 1737)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(996, 223)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        time.sleep(1)
        if config.select_apk == '1':
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(966, 1160)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        else:
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(349, 1267)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        time.sleep(1)
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(961, 210)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(915, 1752)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        time.sleep(1)
        # commented due to fact of multi-languages users
        # driver.find_element(By.XPATH, '//android.view.View[@content-desc="Zaloguj"]').#click()
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(1013, 602)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()
        actions.perform()
        time.sleep(1)
        driver.press_keycode(133)
    else:
        print("ANWnam not found!")
    print("Logged in!")
    # Counting TE's
    if config.select_apk == '1':
        counter3 = execute_sql(connection, SQL.tenam_count_from_plnam_dc2, config.info_jt_place_dc2)
    else:
        counter3 = execute_sql(connection, SQL.tenam_count_from_plnam_dc4, config.info_jt_place_dc4)

    counter2 = counter3 if counter3 else print(counter3)
    counter1 = str(counter2)
    counter0 = "".join(c for c in counter1 if c.isalnum())
    counter = int(counter0)
    print("Number of TEs possible to scan: ", counter)
    num_cycles = int(input("How many times to cycle: "))
    j = 0
    # Loop
    # logcat_process = subprocess.Popen(["adb", "logcat"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    # try:
    # Loop
    # while True:
    #    logcat_output = logcat_process.stdout.readline()
    #    if not logcat_output:
    #   save_logcat(logcat_output, logcat_file_path)
    # except KeyboardInterrupt:
    # Stopping loop
    # pass
    # finally:
    # Closing logcat
    #  logcat_process.kill()

    for number in range(num_cycles):
        if config.select_apk == '1':
            tenam2 = execute_sql(connection, SQL.tenam_on_place_with_rowid_dc2, config.info_jt_place_dc2, number1)
        else:
            tenam2 = execute_sql(connection, SQL.tenam_on_place_with_rowid_dc4, config.info_jt_place_dc4, number1)

        tenam1 = str(tenam2)
        tenam0 = "".join(c for c in tenam1 if c.isalnum())
        # tenam = int(tenam0)
        if tenam0:
            print(tenam0)
            time.sleep(1)
            # TeNamToScan = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="TeNam"]')
            tenamtoscan = driver.find_element(By.CLASS_NAME, 'android.widget.EditText')
            tenamtoscan.click()
            time.sleep(1)

            generate_barcode(tenam0)

            if config.select_apk == '1':
                show_image(config.barcodes_path_dc2 + '\\' + tenam0 + ".png", -25, 700, duration=2, pointer_actions=lambda: trigger_button(driver))
            else:
                show_image(config.barcodes_path_dc4 + '\\' + tenam0 + ".png", -25, 700, duration=2, pointer_actions=lambda: trigger_button(driver))

            driver.find_element(By.CLASS_NAME, 'android.widget.EditText').send_keys(tenam0)
            driver.press_keycode(66)
            time.sleep(1)
            driver.press_keycode(131)
            j += 1
            print("Cycle done, number ", j)
            number1 += 1
        else:
            print("Error: tenam is None.")
    print(num_cycles, "TEs scanned")
    driver.press_keycode(134)
    time.sleep(2)
    driver.press_keycode(134)
    time.sleep(2)
    driver.press_keycode(134)
    time.sleep(2)
    driver.press_keycode(66)
    time.sleep(2)
    # Shutting down app
    driver.terminate_app('com.xxx.logistics.wms.xxx')
    driver.terminate_app('com.xxx.android.xxx.xxx')
    assert num_cycles == j
    time.sleep(1)
    # Verifying photos

    def pull_folder(folder_path, local_path, device_id=None):
        try:
            # Get the path to adb.exe using the LOCALAPPDATA environment variable
            adb_path = os.path.join(os.environ['LOCALAPPDATA'], "Android", "Sdk", "platform-tools", "adb.exe")
            # ADB command

            adb_command = [adb_path, "pull", folder_path, local_path]
            if device_id:
                adb_command.insert(1, "-s")
                adb_command.insert(2, device_id)
            result = subprocess.run(adb_command, capture_output=True, text=True)
            if result.returncode == 0:
                print("Files downloaded!")
                return True
            else:
                print("Downloading error!")
                print(result.stderr)
                return False
        except Exception as e:
            print("ADB error!", e)
            return False
    # Android path
    folder_path = "/sdcard/ImageCapture/PackVerf_Images"
    device_id = "21337B3F51"
    # Local path
    local_path = r"C:\SV_MONITORING"
    # Executing pull
    pull_folder(folder_path, local_path, device_id)

    def list_files_info(directory):
        try:
            # Counters ini
            num_files = 0
            file_types = {}
            total_size = 0

            # Going through files
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # Full path
                    file_path = os.path.join(root, file)

                    # Counter
                    num_files += 1

                    # File types
                    file_extension = os.path.splitext(file)[1]

                    # Calculating count
                    if file_extension in file_types:
                        file_types[file_extension] += 1
                    else:
                        file_types[file_extension] = 1

                    # Calculating sizes
                    file_size = os.path.getsize(file_path)
                    total_size += file_size

            # Showing info
            print(f"Files count: {num_files}")
            print("Files types:")
            for file_type, count in file_types.items():
                print(f"- {file_type}: {count} files")
            print(f"Total files size: {total_size / (1024 * 1024):.2f} MB")

        except Exception as e:
            print("Error:", e)
    # Listing files from device
    print("Files from MDT:")
    directory = r"C:\SV_MONITORING"
    list_files_info(directory)
    # Listing files from network
    print("Files from API:")
    if config.select_apk == '1':
        directory = config.api_path_dc2
    else:
        directory = config.api_path_dc4
    list_files_info(directory)
