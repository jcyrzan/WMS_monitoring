import os
import time
import subprocess
import wmi
import re
import config


def modify_python_script(file_path, old_string, new_string):
    # Opening python script file for reading
    with open(file_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    # Finding and replacing content
    modified_content = re.sub(re.escape(old_string), new_string, script_content, count=0)

    # Opening file for writing
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)


def check_string_in_script(file_path, target_string):
    # Opening python script file for reading
    with open(file_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    # Check if the target string exists in the script content
    if target_string in script_content:
        return True

    else:
        return False


def run_cmd_venv(cmd_command):
    try:
        # Activating venv
        # exec(open(r"C:\Users\jcyrzan\PycharmProjects\Sxx\Scripts\activate_this.py").read(), {'__file__': 'activate_this.py'})
        # Executing CMD command
        process = subprocess.Popen(cmd_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if output:
            print("Result:")
            print(output.decode("utf-8"))
        if error:
            print("Error:")
            print(error.decode("utf-8"))
        if process.returncode != 0:
            raise Exception(f"Command execution failed with return code {process.returncode}")
    except Exception as e:
        print("Exception:", e)


def check_process_running(process_name):
    c = wmi.WMI()
    for process in c.Win32_Process():
        if process.Name == process_name:
            return True
    return False


def install_app(apk_path):
    subprocess.call(["adb", "install", apk_path])


current_directory = os.path.dirname(os.path.abspath(__file__))


select_apk_input = int(input("Select Apk version: 1 - 1xxx, 2 - 2xxx : "))
file_path = os.path.join(current_directory, "config.py")
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
select_apk_found = False

for i, line in enumerate(lines):
    if line.startswith('select_apk'):
        lines[i] = f"select_apk = '{select_apk_input}'\n"
        select_apk_found = True
        break
if not select_apk_found:
    lines.append(f"select_apk = '{select_apk_input}'\n")
with open(file_path, 'w', encoding='utf-8') as file:
    file.writelines(lines)
if select_apk_input == 1:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "TEST_INIT.py")
    target_string = 'Shipment1'
    apk_path = os.path.join(current_directory, config.apk_dc2_path)
    install_app(apk_path)
    if check_string_in_script(file_path, target_string) is False:
        time.sleep(1)
    if check_string_in_script(file_path, target_string) is True:
        old_string = 'Shipment2'
        new_string = 'Shipment1'
        modify_python_script(file_path, old_string, new_string)
if select_apk_input == 2:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "TEST_INIT.py")
    target_string = 'Shipment2'
    apk_path = os.path.join(current_directory, config.apk_dc4_path)
    install_app(apk_path)
    if check_string_in_script(file_path, target_string) is False:
        time.sleep(1)
    if check_string_in_script(file_path, target_string) is True:
        old_string = 'Shipment1'
        new_string = 'Shipment2'
        modify_python_script(file_path, old_string, new_string)
select_suite = int(input("Select Suite: 1 - TE info test, 2 - Loading test : "))
# Creating path
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path_1 = os.path.join(current_directory, "TEST_INFO_JT.py")
file_path_2 = os.path.join(current_directory, "TEST_LOADING.py")

if select_suite == 1:
    process_name = "node.exe"
    # Process check
    if check_process_running(process_name) is True:
        print(f"Process {process_name} works, moving to Suite startup...")
        # Running suite
        subprocess.run(["python", "-m", "pytest", file_path_1, "-q", "-s"])
    elif check_process_running(process_name) is False:
        print(f"Process {process_name} offline, starting...")
        subprocess.Popen("start npm exec appium", shell=True)
        # Waiting for Appium Srv start
        time.sleep(2)
        subprocess.run(["python", "-m", "pytest", file_path_1, "-q", "-s"])
    else:
        print("Failed to start test suite:", select_suite)
elif select_suite == 2:
    process_name = "node.exe"
    if check_process_running(process_name) is True:
        print(f"Process {process_name} works, moving to Suite startup...")

        subprocess.run(["python", "-m", "pytest", file_path_2, "-q", "-s"])
    elif check_process_running(process_name) is False:
        print(f"Process {process_name} offline, starting...")
        subprocess.Popen("start npm exec appium", shell=True)
        time.sleep(2)
        subprocess.run(["python", "-m", "pytest", file_path_2, "-q", "-s"])
    else:
        print("Failed to start test suite:", select_suite)
