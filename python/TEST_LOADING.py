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

if config.select_apk == 1:

    connection = oracledb.connect(
        user=config.username_dc2,
        password=config.password_dc2,
        dsn=config.db_ip_dc2 + "/" + config.sid_dc2)
    # encoding=config.encoding)
else:
    connection = oracledb.connect(
        user=config.username_dc4,
        password=config.mdt_password_dc4,
        dsn=config.db_ip_dc4 + "/" + config.sid_dc4)


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


def empty_folder(directory):
    try:

        if not os.path.isdir(directory):
            print(f"'{directory}' isn't proper directory!")
            return

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        print(f"Files from '{directory}' deleted successfully!")
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
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(1008, 1666)
    actions.w3c_actions.pointer_action.pointer_down()
    actions.w3c_actions.pointer_action.pause(0.5)
    actions.w3c_actions.pointer_action.release()
    actions.perform()


def generate_barcode(tenam):
    if config.select_apk == 1:
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


def test_loading():
    deleting_parameter = int(input("Do you want to delete files from MDT? 1 - Yes, 2 - No : "))
    # Checking folders if not present - creating
    create_folder_if_not_exists("BARCODES", "C:\\")
    create_folder_if_not_exists("SV_MONITORING", "C:\\")

    # Deleting old files
    barcodes = r"C:\BARCODES"
    downloaded_images = r"C:\SV_MONITORING"
    api_files = r"N:\DC2ShipmentStorage"
    empty_folder(downloaded_images)
    empty_folder(api_files)
    empty_folder(barcodes)

    if deleting_parameter == 1:
        folder_path = "/sdcard/ImageCapture/PackVerf_Images"
        device_id = "21337B3F51"
        delete_folder(folder_path, device_id)
        print("Files from device deleted!")
    elif deleting_parameter == 2:
        print("Files from device preserved!")
    else:
        print("Wrong number selected!")

    def execute_sql(connection, querry, par1, par2=None):
        execute_sql_result = None
        try:
            cur = connection.cursor()
            if par2 is not None:
                cur.execute(querry, str=par1, str2=par2)
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

    def wait_for_element(driver, timeout, locator):
        try:
            element = WebDriverWait(driver, timeout).until(ec.presence_of_element_located(locator))
            return element
        except TimeoutException:
            return None

    locator = (By.XPATH, '//android.widget.EditText[@resource-id="AnwNam"]')
    element = wait_for_element(driver, 5, locator)

    if element:
        time.sleep(1)
        if config.select_apk == 1:
            anwnam = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="AnwNam"]')
            anwnam.send_keys(config.mdt_login_dc2)
        else:
            anwnam = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="AnwNam"]')
            anwnam.send_keys(config.mdt_login_dc4)
        time.sleep(1)
        anwknw = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="AnwKnw"]')
        anwknw.click()
        time.sleep(1)
        if config.select_apk == 1:
            anwknw = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="AnwKnw"]')
            anwknw.send_keys(config.mdt_password_dc2)
        else:
            anwknw = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="AnwKnw"]')
            anwknw.send_keys(config.mdt_password_dc4)
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
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(349, 1147)
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
        # Login = driver.find_element(By.XPATH, '//android.view.View[@content-desc="Zaloguj"]').click()
        time.sleep(1)
        driver.press_keycode(66)
        loading_parameter = int(
            input("Do you want to perform Pallet loading or Carton loading? 1 - Pallet, 2 - Carton : "))
        if loading_parameter == 1:
            time.sleep(1)
            driver.press_keycode(132)
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(540, 262)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            if config.select_apk == 1:
                actions = ActionChains(driver)
                actions.send_keys(config.loading_destination_dc2)
                actions.perform()
            else:
                actions = ActionChains(driver)
                actions.send_keys(config.loading_destination_dc4)
                actions.perform()

            driver.press_keycode(66)
            if config.select_apk == 1:
                ladmdt = execute_sql(connection, SQL.ladid_from_gate_dc2, config.loading_destination_dc2)
            else:
                ladmdt = execute_sql(connection, SQL.ladid_from_gate_dc4, config.loading_destination_dc4)
            ladmdt2 = str(ladmdt)
            ladmdt3 = "".join(c for c in ladmdt2 if c.isalnum() or c == '_')
            # LAD = driver.find_element(By.XPATH, '//android.widget.Button[@text="DC23854WYSYLKA_WYS_BUF_1"]').click()
            # LAD = driver.find_element(By.XPATH, '//*[contains(text(),"DC23854WYSYLKA_WYS_BUF_1")]').click()
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(879, 424)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            driver.press_keycode(66)
            # Tenamtrg = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="TeNamTrg"]').click()
            # Tenamtrg = driver.find_element(By.ID, 'TeNamTrg').click()
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(1012, 320)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            if config.select_apk == 1:
                tenamtrg = execute_sql(connection, SQL.tenam_from_place_and_ladid_dc2, config.loading_gate_dc2, ladmdt3)
            else:
                tenamtrg = execute_sql(connection, SQL.tenam_from_place_and_ladid_dc4, config.loading_gate_dc4, ladmdt3)
            tenamtrg2 = str(tenamtrg)
            tenamtrg3 = "".join(c for c in tenamtrg2 if c.isalnum() or c == '_')

            actions = ActionChains(driver)
            actions.send_keys(tenamtrg3)
            actions.perform()
            driver.press_keycode(66)
            # Tenamcounter = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="Input"]').click()

            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(1005, 261)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            if config.select_apk == 1:
                tenamcount = execute_sql(connection, SQL.tenam_count_from_pallet_dc2, tenamtrg3)
            else:
                tenamcount = execute_sql(connection, SQL.tenam_count_from_pallet_dc4, tenamtrg3)
            tenamcount2 = str(tenamcount)
            tenamcount3 = "".join(c for c in tenamcount2 if c.isalnum() or c == '_')

            actions = ActionChains(driver)
            actions.send_keys(tenamcount3)
            actions.perform()
            driver.hide_keyboard()
            time.sleep(1)

            # enter = driver.find_element(By.XPATH, '//android.view.View[@resource-id="numblockEnter"]/android.view.View').click()

            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(1014, 1045)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()

            if config.select_apk == 1:
                actions = ActionChains(driver)
                actions.send_keys(config.loading_destination_dc2)
                actions.perform()
            else:
                actions = ActionChains(driver)
                actions.send_keys(config.loading_destination_dc4)
                actions.perform()

            driver.hide_keyboard()
            driver.press_keycode(66)
            print("Number of TE relased:" + tenamtrg3)

        elif loading_parameter == 2:
            if config.select_apk == 1:
                ladmdt = execute_sql(connection, SQL.ladid_from_gate_dc2, config.loading_destination_dc2)
            else:
                ladmdt = execute_sql(connection, SQL.ladid_from_gate_dc4, config.loading_destination_dc4)
            ladmdt2 = str(ladmdt)
            ladmdt3 = "".join(c for c in ladmdt2 if c.isalnum() or c == '_')

            if config.select_apk == 1:
                tenamtrg = execute_sql(connection, SQL.tenam_from_place_and_ladid_dc2, config.loading_gate_dc2, ladmdt3)
            else:
                tenamtrg = execute_sql(connection, SQL.tenam_from_place_and_ladid_dc4, config.loading_gate_dc4, ladmdt3)
            tenamtrg2 = str(tenamtrg)
            tenamtrg3 = "".join(c for c in tenamtrg2 if c.isalnum() or c == '_')

            if config.select_apk == 1:
                cartons_to_ship = execute_sql(connection, SQL.tenam_count_from_plnam_dc2, config.loading_gate_dc2)
            else:
                cartons_to_ship = execute_sql(connection, SQL.tenam_count_from_plnam_dc4, config.loading_gate_dc4)
            cartons_to_ship2 = str(cartons_to_ship)
            cartons_to_ship3 = "".join(c for c in cartons_to_ship2 if c.isalnum() or c == '_')
            cartons_to_ship4 = int(cartons_to_ship3)
            print("Cartons possible to ship: " + cartons_to_ship3)
            box_cycles = int(input("How many cartons you want to ship: "))
            if box_cycles <= cartons_to_ship4:
                driver.press_keycode(135)
                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(980, 264)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.1)
                actions.w3c_actions.pointer_action.release()
                actions.perform()

                if config.select_apk == 1:
                    actions = ActionChains(driver)
                    actions.send_keys(config.loading_destination_dc2)
                    actions.perform()
                else:
                    actions = ActionChains(driver)
                    actions.send_keys(config.loading_destination_dc4)
                    actions.perform()

                driver.hide_keyboard()
                driver.press_keycode(66)

                # accept = driver.find_element(By.XPATH, '//android.view.View[@resource-id="numblockEnter"]/android.view.View').click()

                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(879, 424)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.1)
                actions.w3c_actions.pointer_action.release()
                actions.perform()
                driver.press_keycode(66)
                y = 0
                # Not used
                # teonpaletcounter = execute_sql(connection, SQL.tenam_count_from_pallet, tenamtrg3)
                # teonpaletcounter2 = str(teonpaletcounter)
                # teonpaletcounter3 = "".join(c for c in teonpaletcounter2 if c.isalnum() or c == '_')
                # teonpaletcounter4 = int(teonpaletcounter3)

                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                actions.w3c_actions.pointer_action.move_to_location(1012, 320)
                actions.w3c_actions.pointer_action.pointer_down()
                actions.w3c_actions.pointer_action.pause(0.1)
                actions.w3c_actions.pointer_action.release()
                actions.perform()

                generate_barcode(tenamtrg3)
                if config.select_apk == 1:
                    show_image(config.barcodes_path_dc2 + '\\' + tenamtrg3 + ".png", -25, 700, duration=2,
                               pointer_actions=lambda: trigger_button(driver))
                else:
                    show_image(config.barcodes_path_dc4 + '\\' + tenamtrg3 + ".png", -25, 700, duration=2,
                               pointer_actions=lambda: trigger_button(driver))
                actions = ActionChains(driver)
                actions.send_keys(tenamtrg3)
                time.sleep(1)
                actions.perform()
                driver.hide_keyboard()

                driver.press_keycode(66)

                for number in range(box_cycles):

                    # scan_carton = driver.find_element(By.XPATH, '//android.widget.EditText[@resource-id="TeNam"]').click()
                    # /\ no object to hook up

                    actions = ActionChains(driver)
                    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                    actions.w3c_actions.pointer_action.move_to_location(1002, 687)
                    actions.w3c_actions.pointer_action.pointer_down()
                    actions.w3c_actions.pointer_action.pause(0.1)
                    actions.w3c_actions.pointer_action.release()
                    actions.perform()

                    if config.select_apk == 1:
                        tenam_from_palet = execute_sql(connection, SQL.tenam_from_pallet_dc2, tenamtrg3)
                    else:
                        tenam_from_palet = execute_sql(connection, SQL.tenam_from_pallet_dc4, tenamtrg3)
                    tenam_from_palet2 = str(tenam_from_palet)
                    tenam_from_palet3 = "".join(c for c in tenam_from_palet2 if c.isalnum() or c == '_')

                    actions = ActionChains(driver)
                    generate_barcode(tenam_from_palet3)
                    if config.select_apk == 1:
                        show_image(config.barcodes_path_dc2 + '\\' + tenam_from_palet3 + ".png", -25, 700, duration=2,
                                   pointer_actions=lambda: trigger_button(driver))
                    else:
                        show_image(config.barcodes_path_dc4 + '\\' + tenam_from_palet3 + ".png", -25, 700, duration=2,
                                   pointer_actions=lambda: trigger_button(driver))
                    actions.send_keys(tenam_from_palet3)
                    actions.perform()

                    # scan_carton.send_keys(carton_for_loading3)
                    time.sleep(2)
                    driver.press_keycode(66)

                    actions = ActionChains(driver)
                    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
                    actions.w3c_actions.pointer_action.move_to_location(1014, 1045)
                    actions.w3c_actions.pointer_action.pointer_down()
                    actions.w3c_actions.pointer_action.pause(0.1)
                    actions.w3c_actions.pointer_action.release()
                    actions.perform()

                    if config.select_apk == 1:
                        generate_barcode(config.loading_destination_dc2)
                        show_image(config.barcodes_path_dc2 + '\\' + config.loading_destination_dc2 + ".png", -25, 700,
                                   duration=2, pointer_actions=lambda: trigger_button(driver))
                    else:
                        generate_barcode(config.loading_destination_dc4)
                        show_image(config.barcodes_path_dc4 + '\\' + config.loading_destination_dc4 + ".png", -25, 700,
                                   duration=2, pointer_actions=lambda: trigger_button(driver))

                    if config.select_apk == 1:
                        actions = ActionChains(driver)
                        actions.send_keys(config.loading_destination_dc2)
                        actions.perform()
                    else:
                        actions = ActionChains(driver)
                        actions.send_keys(config.loading_destination_dc4)
                        actions.perform()

                    time.sleep(1)
                    driver.hide_keyboard()
                    driver.press_keycode(66)
                    y += 1
                    print("Cycle number: ", y)
                assert y == box_cycles

            elif box_cycles < 1:
                print("Cannot handle number less than 1")

            folder_path = "/sdcard/ImageCapture/PackVerf_Images"

            device_id = "21337B3F51"

            local_path = r"C:\SV_MONITORING"

            pull_folder(folder_path, local_path, device_id)

            def list_files_info(directory):

                num_files = 0
                file_types = {}
                total_size = 0

                for root, dirs, files in os.walk(directory):
                    for file in files:

                        file_path = os.path.join(root, file)

                        num_files += 1

                        file_extension = os.path.splitext(file)[1]

                        if file_extension in file_types:
                            file_types[file_extension] += 1
                        else:
                            file_types[file_extension] = 1

                        file_size = os.path.getsize(file_path)
                        total_size += file_size

                print(f"Files count: {num_files}")
                print("Files types:")
                for file_type, count in file_types.items():
                    print(f"- {file_type}: {count} files")
                    print(f"Total files size: {total_size / (1024 * 1024):.2f} MB")

            driver.press_keycode(134)
            driver.press_keycode(66)
            driver.press_keycode(134)
            driver.press_keycode(134)
            driver.press_keycode(134)
            driver.press_keycode(66)
            driver.terminate_app('com.wms.xxx.xxx.mobile')
            driver.terminate_app('com.apk.android.xxx.xxx')
            print("Files from MDT:")
            directory = r"C:\SV_MONITORING"
            list_files_info(directory)
            print("Files from API:")
            directory = r"N:\DC2ShipmentStorage"
            list_files_info(directory)

    else:
        print("ANWnam not found!")
