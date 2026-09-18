import os
import shutil
import subprocess
from time import sleep

# --- [1. SABİTLER VE DEĞİŞKENLER] ---
ndos = "r4"
ext_ver = "r1.0.0"
ndos_pkg_ver = "r1.1.1"

FS_ROOT = ".fs/root"
FS_BACKUP_FILE = ".fs/ndos_backup.zip"
EXT_PKG = ".packages/EXT.txt"
NDOS_PKG = ".packages/NDOS.txt"
USER_FILE = ".userinfo/username.txt"
PASSWORD_FILE = ".userinfo/password.txt"

current_path = ["home"]
current_username = "ADMINISTRATOR"
USERNAME = ""

# Sistem Klasörleri
os.makedirs(".packages", exist_ok=True)
os.makedirs(".userinfo", exist_ok=True)
os.makedirs(".fs", exist_ok=True)

if not os.path.exists(NDOS_PKG):
    with open(NDOS_PKG, "w", encoding="utf-8") as pkgndos:
        pkgndos.write(f"{ndos_pkg_ver}")

APP_STORE = {
    "1": {"name": "Youtube", "command": "yt"},
    "2": {"name": "Google", "command": "g"},
    "3": {"name": "Edge", "command": "e"},
    "4": {"name": "Counter", "command": "count"}
}

nw = "Network: Network connection: Main Machine\n"
st = "Reserved Storage: 48 MB\n"
ram = "Reserved Ram: 16 MB\n"
cpu = "=min_req(@0.3 GHz)\n"


# --- [2. FS MODÜLÜ FONKSİYONLARI] ---
def init_file_system():
    """Başlangıçta ana dizinleri gerçek disk üzerinde oluşturur."""
    os.makedirs(os.path.join(FS_ROOT, "home", "apps"), exist_ok=True)
    os.makedirs(os.path.join(FS_ROOT, "home", "Documents"), exist_ok=True)
    os.makedirs(os.path.join(FS_ROOT, "home", "Pictures"), exist_ok=True)
    os.makedirs(os.path.join(FS_ROOT, "home", "Videos"), exist_ok=True)
    os.makedirs(os.path.join(FS_ROOT, "home", "Musics"), exist_ok=True)

def get_real_path():
    """NDOS içindeki sanal yolu, bilgisayardaki gerçek fiziksel yola çevirir."""
    return os.path.join(FS_ROOT, *current_path)

def load_file_system():
    """Fiziksel klasörlerin varlığını kontrol eder."""
    required_folders = ["apps", "Documents", "Pictures", "Videos", "Musics"]
    home_path = os.path.join(FS_ROOT, "home")
    for folder in required_folders:
        os.makedirs(os.path.join(home_path, folder), exist_ok=True)

def get_installed_apps():
    """Uygulamaları /home/apps klasöründeki gerçek dosyalardan okur."""
    apps_path = os.path.join(FS_ROOT, "home", "apps")
    if os.path.exists(apps_path):
        return [f.replace(".napp", "") for f in os.listdir(apps_path) if f.endswith(".napp")]
    return []

def list_directory():
    real_path = get_real_path()
    items = os.listdir(real_path)
    if not items:
        print("(empty)")
    else:
        formatted_items = []
        for item in items:
            full_item_path = os.path.join(real_path, item)
            if os.path.isdir(full_item_path):
                formatted_items.append(f"[{item}]")
            else:
                formatted_items.append(item)
        print("Contents: " + "  ".join(formatted_items))

def create_directory(name):
    target_path = os.path.join(get_real_path(), name)
    if os.path.exists(target_path):
        print(f"Directory or file '{name}' already exists!")
    else:
        os.makedirs(target_path)
        print(f"Directory '{name}' created.")

def change_directory(name):
    global current_path
    if name == "..":
        if len(current_path) > 1: 
            current_path.pop()
    else:
        target_path = os.path.join(get_real_path(), name)
        if os.path.exists(target_path) and os.path.isdir(target_path):
            current_path.append(name)
        else:
            print(f"No such directory: '{name}'")

def create_file(name):
    if "." not in name:
        name += ".ndoc"
        
    target_path = os.path.join(get_real_path(), name)
    if os.path.exists(target_path):
        print(f"File '{name}' already exists!")
    else:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write("=== NDOC ===\n---CONTENT---\n")
        print(f"File '{name}' created with NDOS format.")

def write_file(name):
    if "." not in name:
        name += ".ndoc"
        
    target_path = os.path.join(get_real_path(), name)
    if os.path.exists(target_path) and os.path.isfile(target_path):
        print(f"--- Editing {name} ---")
        print("To finish and save, type $save$ on a new line and press Enter.\n")
        
        lines = []
        while True:
            line = input()
            if line == "$save$":
                break
            lines.append(line)

        content = "\n".join(lines)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(f"=== NDOC ===\n")
            f.write(f"AUTHOR: {current_username}\n")
            f.write(f"---CONTENT---\n")
            f.write(content)
            
        print(f"Data written successfully in NDOS format!")
    else:
        print(f"No such file: '{name}'")

def read_file(name):
    if "." not in name:
        name += ".ndoc"
        
    target_path = os.path.join(get_real_path(), name)
    if os.path.exists(target_path) and os.path.isfile(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            raw_data = f.read()
            
        if "---CONTENT---" in raw_data:
            parts = raw_data.split("---CONTENT---\n")
            meta = parts[0]
            content = parts[1]
            print(f"\n[NDOS File Reader] Metadata:\n{meta.strip()}")
            print(f"---CONTENT---")
            print(f"{content}\n")
        else:
            print(f"\nContent:\n{raw_data}\n")
    else:
        print(f"No such file.")

def delete_file(name):
    if "." not in name and not os.path.exists(os.path.join(get_real_path(), name)):
        if os.path.exists(os.path.join(get_real_path(), name + ".ndoc")):
            name += ".ndoc"
            
    target_path = os.path.join(get_real_path(), name)
    if os.path.exists(target_path):
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
            print(f"Directory deleted.")
        else:
            os.remove(target_path)
            print(f"File deleted.")
    else:
        print(f"No such file or directory.")

def file_system_shell():
    """Dosya sistemi kabuğu"""
    global current_path
    print("\nWelcome to the NDOS File System\nType 'help' for available commands.")
    
    while True:
        path_str = "/".join(current_path)
        command = input(f"NDOS:{path_str} $ ").strip().split()

        if not command: continue
        cmd = command[0]
        args = command[1:]

        if cmd == "ls": list_directory()
        elif cmd == "mkdir" and args: create_directory(args[0])
        elif cmd == "cd" and args: change_directory(args[0])
        elif cmd == "touch" and args: create_file(args[0])
        elif cmd == "write" and args: write_file(args[0])
        elif cmd == "read" and args: read_file(args[0])
        elif cmd == "del" and args: delete_file(args[0])
        elif cmd == "exit":
            print("Exiting file system...\n")
            break
        elif cmd == "help":
            print("\nCommands: ls, mkdir, cd, touch, write, read, del, parameters, users, exit")
        elif cmd == "parameters":
            print(
                "\nls\n"
                "mkdir \n"
                "cd \n"
                "touch \n"
                "write \n"
                "read \n"
                "del \n"
            )
        else: print("Invalid command.")


# --- [3. TECHMD MODÜLÜ FONKSİYONLARI] ---
def tech_mode():
    print(
        "\nNDOS Tech Mode For Advanced Users\n"
        "WARNING: This mode has no limitation, only for advanced users!\n"
        "Type 'help' for help...\n"
    )
    global current_username
    
    # Güncel kullanıcı adını dosyadan okuyalım
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            current_username = f.read().strip()

    while True:
        tech = str(input(">>").strip().lower())
        partitions = tech.split()
        
        if tech == "help" and not os.path.exists(EXT_PKG):
            print(
                ">[COMMAND LIST]:\n"
                ">help\n"
                ">cls\n"
                ">ndos\n"
                ">pkg\n"
                ">exit"
            )
        elif tech == "help" and os.path.exists(EXT_PKG):
            print(
                ">[HELP][COMMANDS]:\n"
                ">help\n"
                ">cls\n"
                ">ndos\n"
                ">ext\n"
                ">pkg\n"
                ">exit"
            )
        elif tech == "cls":
            clear_screen()
        elif tech == "ndos":
            print(
                ">ndos -pwchange  | ndos -pwreset \n"
                ">ndos -unchange  | ndos -unreset \n"
                ">ndos -get -version\n"
                ">ndos -get -nversion\n"
                ">ndos -get -creator\n"
                ">ndos -get -product"
            )
        elif (len(partitions) == 3 and partitions[0] == "ndos" and partitions[1] in ["-pwreset", "-pwchange"]):
            new_password = str(partitions[2])
            with open(PASSWORD_FILE, "w") as f:
                f.write(new_password)
            print(f">>[NDOS][{new_password}] Success!")
        elif (len(partitions) == 3 and partitions[0] == "ndos" and partitions[1] in ["-unreset", "-unchange"]):
            new_un = str(partitions[2])
            current_username = new_un
            with open(USER_FILE, "w", encoding="utf-8") as f:
                f.write(current_username)
            print(f">[NDOS][{new_un}] Success!")
        elif tech == "ndos -get -version":
            print(f">[NDOS][VERSION] NDOS Version: r3.1\n")
        elif tech == "ndos -get -nversion":
            print(f">[NDOS][VERSION] ndos Package Version: {ndos_pkg_ver}\n")
        elif tech == "ndos -get -creator":
            print(">[NDOS][CREATOR] OrhanPivot")
        elif tech == "ndos -get -product":
            print(
                ">[SYS][PRODUCT] Nebula Disk Operating System\n"
                ">[SYS][PRODUCT] A.K.A. NebulaOS-CMD\n"
            )
        elif tech == "pkg":
            print(
                ">pkg -install \n"
                ">pkg -uninstall "
            )
        elif tech == "pkg -install ext" and not os.path.exists(EXT_PKG):
            with open(EXT_PKG, "w", encoding="utf-8") as ext:
                ext.write(f"{ext_ver}")
            print(">[PKG] Success")
        elif tech == "pkg -install ext" and os.path.exists(EXT_PKG):
            print(">[PKG] This package is already installed.")
        elif tech == "pkg -install ndos":
            print(">[PKG] This package is already installed.")
        elif tech == "pkg -uninstall ndos":
            print(">[PKG] System package cannot be deleted.")
        elif tech == "pkg -uninstall ext" and os.path.exists(EXT_PKG):
            try:
                os.remove(EXT_PKG)
                print(">[PKG] Success")
            except PermissionError as e:
                print(f">[PKG] Error: {e}")
        elif tech == "pkg -uninstall ext" and not os.path.exists(EXT_PKG):
            print(">[PKG] This package doesn't exist yet.")
        elif len(partitions) == 3 and partitions[0] == "pkg" and partitions[1] == "-install" and partitions[2] not in ["ndos","ext"]:
            print(f">>[PKG] Invalid package name: {partitions[2]}")
        elif tech == "ext" and os.path.exists(EXT_PKG):
            print(
                ">ext -version\n"
                ">ext -backup\n"
                ">ext -restore"
            )
        elif tech == "ext -backup" and os.path.exists(EXT_PKG):
            if os.path.exists(FS_ROOT):
                try:
                    shutil.make_archive(".fs/ndos_backup", 'zip', FS_ROOT)
                    print(">[EXT] File system successfully backed up as ZIP!")
                except Exception as e:
                    print(f">[EXT] Backup failed: {e}")
            else:
                print(">[EXT] No active filesystem root found to backup.")
        elif tech == "ext -restore" and os.path.exists(EXT_PKG):
            if os.path.exists(FS_BACKUP_FILE):
                try:
                    if os.path.exists(FS_ROOT):
                        shutil.rmtree(FS_ROOT)
                    shutil.unpack_archive(FS_BACKUP_FILE, FS_ROOT, 'zip')
                    load_file_system()
                    print(">[EXT] File system successfully restored from ZIP backup!")
                except Exception as e:
                    print(f">[EXT] Restore failed: {e}")
            else:
                print(">[EXT] No backup file found!")
        elif tech == "ext -version" and os.path.exists(EXT_PKG):
            with open(EXT_PKG, "r", encoding="utf-8") as extverfile:
                extver_val = extverfile.read()
                print(f">[EXT] Version: {extver_val}")
        elif tech == "exit":
            break
        else:
            print(">[ERROR] Invalid command.")


# --- [4. NDOS SİSTEM FONKSİYONLARI] ---
def clear_screen():
    """Terminali temizler."""
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)

def set_username():
    global USERNAME, current_username
    if not os.path.exists(USER_FILE):
        name = input("Set a username for NDOS (Press Enter for 'ADMINISTRATOR'): ").strip()
        USERNAME = name if name else "ADMINISTRATOR"
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write(USERNAME)
    else:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            USERNAME = f.read().strip()
    
    current_username = USERNAME

def change_username():
    global USERNAME, current_username
    print(f"\nCurrent username: {USERNAME}")
    new_name = input("Enter new username (Press X to cancel): ").strip()
    
    if new_name.lower() == 'x':
        print("Canceled.")
    elif new_name:
        USERNAME = new_name
        current_username = USERNAME
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write(USERNAME)
        print(f"Username changed to '{USERNAME}' successfully!")
    else:
        print("Username cannot be empty.")

def set_password():
    if not os.path.exists(PASSWORD_FILE):
        password = input("Set a new password for NDOS: ")
        with open(PASSWORD_FILE, "w") as f:
            f.write(password)
        print("Password set successfully!")

def check_password():
    if not os.path.exists(PASSWORD_FILE):
        set_password()
    with open(PASSWORD_FILE, "r") as f:
        saved_password = f.read().strip()
    attempts = 3
    while attempts > 0:
        password = input(f"Enter password ({attempts} attempts left): ")
        if password == "ndos -pwreset":
            verify_user = input("Enter your username to verify identity: ").strip()
            if verify_user == USERNAME:
                new_password = input("Enter new password: ")
                with open(PASSWORD_FILE, "w") as f:
                    f.write(new_password)
                print("Password reset successfully!")
                return
            else:
                print("Verification failed! Incorrect username.\n")
                continue
        elif password == "ndos -pwpass":
            return
        elif password == saved_password:
            print("Access granted!")
            return
        else:
            attempts -= 1
            if attempts > 0:
                print(f"Wrong password! Try again. ({attempts} attempts left)\n")
            else:
                print("Too many wrong attempts! NDOS is locking down.")
                exit()

def change_password():
    with open(PASSWORD_FILE, "r") as f:
        saved_password = f.read().strip()
    while True:
        old_password = input("Enter your current password: ")
        if old_password == saved_password:
            new_password = input("Enter new password: ")
            with open(PASSWORD_FILE, "w") as f:
                f.write(new_password)
            print("Password changed successfully!")
            break
        else:
            print("Incorrect password!")

def welcome_screen():
    print("   ---NDOS---  \n")
    print("Welcome to NDOS!\n")

def login():
    giris = input('Write "L" to log in to NDOS: ').strip().lower()
    if giris == "l":
        print("\nLoading requirements...\n")
        return True
    else:
        print("\nLeaving...")
        return False

def user_info():
    print(f"Logged as: {USERNAME}\n")

def calculator():
    print("\nNDOS Calculator\n")
    while True:
        select = str(input("1 for basic, 2 for advanced mode> "))
        if select == "1":
            try:
                num1 = float(input("Enter first number: "))
                operator = str(input("Enter operation (+, -, *, /): ").strip())
                num2 = float(input("Enter second number: "))
                if operator == "+": result = num1 + num2
                elif operator == "-": result = num1 - num2
                elif operator == "*": result = num1 * num2
                elif operator == "/":
                    if num2 == 0: print("Error: Division by zero."); continue
                    result = num1 / num2
                else: print("Invalid operator!"); continue
                print(f"Result: {result}\n")
            except ValueError: print("Error: Invalid numbers.\n"); continue
            if input("Calculate again? (Y/N): ").strip().lower() != "y": break
        elif select == "2":
            inp_math_op = input("Enter a full mathematical operation: ")
            try:
                adv_result = eval(inp_math_op)
                print(f"Result is: {adv_result}")
            except ValueError: print("Error: Invalid input.\n"); continue
            if input("Calculate again? (Y/N): ").strip().lower() != "y": break
        else:
            input("Enter a valid number!")

def Youtube(): print("\nSorry! Youtube is not supporting! Wait the GUI VERSION.")
def Google(): print("\nSorry! Google is not supporting! Wait the GUI VERSION.")
def Edge(): print("\nSorry! Edge is not supporting! Wait the GUI VERSION.")
def Counter_app():
    while True:
        try:
            a = float(input("\nStart number(must be smaller than end number): "))
            b = float(input("End number: "))
            d = float(input("Wait time (seconds): "))
            e = float(input("Step size: "))
            if a >= b or d < 0 or e <= 0: print("Invalid parameters."); break
            while a < b + e:
                print(a); a += e; sleep(d)
        except ValueError: print("Invalid input.")
        if input("Return? (r): ").strip().lower() != "r": break

def app_store():
    installed = get_installed_apps()
    print("\n📲 NDOS App Store (Connected to FS Module)")
    for k, v in APP_STORE.items():
        status = "Installed" if v["name"] in installed else "Available"
        print(f"{k}. {v['name']} - {status}")
    
    choice = input("Select to install (X to exit): ").strip()
    if choice in APP_STORE:
        name = APP_STORE[choice]["name"]
        if name not in installed:
            app_file_path = os.path.join(FS_ROOT, "home", "apps", f"{name}.napp")
            with open(app_file_path, "w", encoding="utf-8") as f:
                f.write("Third Party Application")
            print(f"{name} installed to /home/apps/!")
        else: 
            print("Already installed.")

def uninstall_apps():
    installed = get_installed_apps()
    if not installed: 
        print("No apps installed!")
        return
    
    for i, app in enumerate(installed, 1): 
        print(f"{i}. {app}")
    choice = input("Uninstall app # (X to exit): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(installed):
        app_to_remove = installed[int(choice)-1]
        app_file_path = os.path.join(FS_ROOT, "home", "apps", f"{app_to_remove}.napp")
        if os.path.exists(app_file_path):
            os.remove(app_file_path)
            print(f"{app_to_remove} deleted from file system!")
        else:
            print("App file could not be found.")

def run_apps():
    installed = get_installed_apps()
    if not installed: print("No apps installed inside /home/apps!"); return
    
    print("\nInstalled Apps (Found in /home/apps):")
    for i, app in enumerate(installed, 1): print(f"{i}. {app}")
    
    choice = input("Run app # (X to exit): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(installed):
        app = installed[int(choice)-1]
        print(f"Launching {app}...")
        if app == "Youtube": Youtube()
        elif app == "Google": Google()
        elif app == "Edge": Edge()
        elif app == "Counter": Counter_app()

def apps():
    while True:
        print("\nC: Calculator | E: Exit")
        c = input("Choice: ").strip().lower()
        if c == "c": calculator()
        elif c == "e": break
        else: print("Invalid.")

def shw_upd():
    rel = "Release "+ndos
    print(
        "\n"
        f"-NDOS {rel}-\n"
        f"-NDOS {ndos} Changes-\n"
        "-Big Changes (0):\n"
        "   -None"
        "-Small Changes (1):\n"
        "   -Hotfix"
    )
    input("Press Enter...")

def show_os_info():
    print("\n📌 NDOS Information Category:\n")
    print(
        f"{nw}"
        f"{st}"
        f"{ram}"
        f"{cpu}"
    )
    input("Press Enter...")

def administrator():
    while True:
        with open(PASSWORD_FILE, "r") as f:
            saved_password = f.read().strip()
        with open(USER_FILE, "r") as ff:
            saved_username = ff.read().strip()
        cmd = input("> ").strip().lower()
        parts = cmd.split()
        if cmd == "exit": break
        elif cmd == "techmode": tech_mode()
        elif cmd == "cls": clear_screen()
        elif cmd == "help": print("\ncls, help, params, info, pkg, ndos, exit,")
        elif cmd == "params": print("\nParameters:\nndos -pwchange\nndos -unchange\nndos -version\nndos -nversion\n")
        elif cmd == "info": show_os_info()
        elif cmd == "pkg": print("\nInstalled packages:\n    -ndos: NDOS System Package\n")
        elif cmd == "ndos": 
            print(
                "\n"
                "\"ndos\" commands:\n"
                "-pwchange | -pwreset: Change password (requires current password)\n"
                "-pwchange   | -pwreset  \n"
                "-unchange | -unreset: Change username\n"
                "-unchange  | -unreset "
                "-version: Show NDOS version\n"
                "-nversion: Show ndos package version\n"
            )
        elif cmd == "ndos -pwchange" or cmd == "ndos -pwreset": change_password()
        elif cmd == "ndos -unchange" or cmd == "ndos -unreset": change_username()
        elif len(parts) == 4 and parts[0] == "ndos" and parts[1] == "-pwreset" and parts[2] == saved_password:
            new_password = parts[3]
            with open(PASSWORD_FILE, "w") as f:
                f.write(new_password)
                print(f"Password successfully changed to {new_password}")
        elif len(parts) == 3 and parts[0] == "ndos" and parts[1] == "-unchange":
            new_username = parts[2]
            with open(USER_FILE, "w") as ff:
                ff.write(new_username)
                print(f"Username successfully changed to {new_username}")
        elif cmd == "ndos -version": print(f"\nNDOS Version: {ndos}\n")
        elif cmd == "ndos -nversion": print(f"\nndos Package Version: {ndos_pkg_ver}\n")
        elif cmd == "ndos -users":
            print(
                "\nUsers:"
                f"\n     {USERNAME}:"
                "\n         Permissions:"
                "\n             Fully Control"
                "\n             Reading&Writing"
                "\n             Reading"
                "\n             Opening"
                "\n             Deleting\n"
            )
        else: print("\nUnknown command. 'help' for commands.")

def show_main_menu():
    while True:
        workings = input(
            "SYSTEM---------------------------------\n"
            "\n"
            "Enter 'Upd' to see the update notes\n"
            "Enter 'info' to view OS info\n"
            "Enter 'cls' to clear screen\n"
            "Enter 'p' to change password\n"
            "Enter 'un' to change username\n"
            "Enter 'fs' to access File System\n"
            "Enter 'cmd' to enter Administrator Mode\n"
            "Apps and Store-------------------------\n"
            "\n"
            "Enter 'A' to view system apps\n"
            "Enter 'R' to run installed apps\n"
            "Enter 'U' to uninstall an installed app.\n"
            "Enter 'St' to open NDOS AppStore\n"
            "\n"
            "QUIT-----------------------------------\n"
            "Enter 'Q' to quit\n"
            "---------------------------------------\n\n"
            "Enter command: "
        ).strip().lower()

        if workings == "upd": shw_upd()
        elif workings == "techmode": tech_mode()
        elif workings == "p": change_password()
        elif workings == "un": change_username()
        elif workings == "info": show_os_info()
        elif workings == "fs": file_system_shell()
        elif workings == "a": apps()
        elif workings == "st": app_store()
        elif workings == "r": run_apps()
        elif workings == "u": uninstall_apps()
        elif workings == "cmd": administrator()
        elif workings == "cls": clear_screen()
        elif workings == "q":
            print("Leaving NDOS...")
            sleep(2); break
        else:
            print("Invalid command.")


# --- [5. SİSTEM BAŞLATICI (MAIN)] ---
init_file_system()
set_username()
set_password()
check_password()
welcome_screen()

if login():
    user_info()
    show_main_menu()