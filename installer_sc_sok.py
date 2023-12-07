import configparser
import os
import csv
import urllib.request
import urllib.error
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog

# - Error codes
# TODO: implementar los codigos de error en los mensajes de error de la GUI
error_codes = {
    0: "No error",
    1: "Error opening URL CSV",
    2: "Error opening URL JSON",
    3: "System not supported",
    4: "Error downloading global.ini",
}

# TODO: usando las entrys (textvariables), volver a implementar la traduccion de los textos

# - Global variables
installer = {
    "lang": "es_ES",
    "csv_url": "https://raw.githubusercontent.com/Sons-of-Kareah/SC_Spanish_Installer/master/config/lang.csv",
    "online_config_url": "https://raw.githubusercontent.com/Sons-of-Kareah/SC_Spanish_Installer/master/config/onlineConfig.json",
    "home": os.path.expanduser("~"),
    "url_ini": "https://github.com/Autovot/SC_Spanish_SOK/releases/latest/download/global.ini",  # + .{idioma}
}
game = {
    'default_folder': 'C:/Program Files/Roberts Space Industries/StarCitizen/',
    # "default_folder": "C:/Games/Roberts Space Industries/StarCitizen/",
    "lang_fodler": "data/Localization/",
    "lang": "en",
    "config_file": "user.cfg",
}
translations = {}
online_config = {}


# - Functions
# -- Get game folder
def get_game_folder(passed_entrys):
    # TODO: comprobar el que el binario/Data.p4k del juego exista
    folder_filedialog_input = tk.filedialog.askdirectory(
        title=translations["folder_select_button"][installer["lang"]]
    )
    if folder_filedialog_input:
        passed_entrys["game_folder"].set(f"{folder_filedialog_input}/")
        passed_entrys["folder_is_selected"].set(True)
        get_game_version(passed_entrys)
        # Update dropdown menu
        menu_version = version_dropdown["menu"]
        menu_version.delete(0, "end")
        for version in passed_entrys["versions_available"]:
            menu_version.add_command(
                label=version,
                command=lambda v=version: passed_entrys["selected_version"].set(v),
            )


# -- Get game version installed
def get_game_version(passed_entrys):
    # Check if any of the versions is installed and if so, save it temporarily in array
    passed_entrys["versions_available"] = []
    for version in online_config["versions"]:
        if os.path.exists(passed_entrys["game_folder"].get() + version):
            passed_entrys["versions_available"].append(version)
    passed_entrys["selected_version"].set(passed_entrys["versions_available"][0])


# -- Ser installer config in home
def set_installer_config():
    pass


# -- Set user config in entrys['game_folder'] + game['config_file']
def set_user_config(passed_lang_complete):
    # Check if user.cfg exist inside game version folder
    temp_cfg_path = (
            entrys["game_folder"].get()
            + entrys["selected_version"].get()
            + "/"
            + game["config_file"]
    )

    config_user = configparser.ConfigParser()
    # Check if user.cfg not exist inside game version folder and create it using configparser
    if os.path.exists(temp_cfg_path):
        # try catch if file contains no section headers
        try:
            config_user.read(temp_cfg_path)
        except configparser.MissingSectionHeaderError:
            # read all file, except if line only contains \n
            with open(temp_cfg_path, "r") as file:
                lines_raw = file.readlines()
            # split lines in dict, spliting by '='
            for line in lines_raw:
                # remove \n from line
                temp_line = line.rstrip("\n").split("=")
                config_user["Global"] = {temp_line[0]: temp_line[1]}

    config_user["Global"] = {"g_language": passed_lang_complete}
    with open(temp_cfg_path, "w") as file:
        config_user.write(file)


# -- Get globlal.ini from gitHub
def install_localization(passed_lang):
    # TODO: cuando se instala, se crea un archivo de configuracion en home, con el idioma seleccionado y la version
    #  del juego seleccionada, aparte se añade la vesion del .ini descargado
    temp_lang_complete = online_config["user_cfg_lang"][passed_lang]
    temp_ini_path = (
            entrys["game_folder"].get()
            + entrys["selected_version"].get()
            + "/"
            + game["lang_fodler"]
            + temp_lang_complete
    )
    temp_url_ini = installer["url_ini"] + "." + passed_lang

    # Check path not exist
    if not os.path.exists(temp_ini_path):
        os.makedirs(temp_ini_path)

    # Delete global.ini if exist
    if os.path.exists(temp_ini_path + "/global.ini"):
        os.remove(temp_ini_path + "/global.ini")

    # Download global.ini from gitHub
    try:
        urllib.request.urlretrieve(
            temp_url_ini, os.path.join(temp_ini_path, "global.ini")
        )
    except urllib.error.URLError as urlError:
        tk.messagebox.showerror(
            "Error", f"Error: {error_codes[4]} - {urlError.reason}"
        )
        exit(4)

    # Set user.cfg
    set_user_config(temp_lang_complete)


# - Load - Translations - CSV
try:
    response_csv = urllib.request.urlopen(installer["csv_url"])
    data_csv = csv.reader(response_csv.read().decode("utf-8").splitlines())
    next(data_csv)
    for row in data_csv:
        id_value, en_value, es_value = row
        translations[id_value] = {"en": en_value, "es_ES": es_value}
except urllib.error.URLError as e:
    tk.messagebox.showerror("Error", "Error: " + str(e.reason))
    exit(1)

# - Load - Online config - JSON
try:
    response_json = urllib.request.urlopen(installer["online_config_url"])
    online_config = eval(response_json.read().decode("utf-8"))
except urllib.error.URLError as e:
    tk.messagebox.showerror("Error", "Error: " + str(e.reason))
    exit(2)

# - Check - System OS
if not os.name == "nt":
    tk.messagebox.showerror(
        "Error", f"Error: {translations['check_system'][installer['lang']]}"
    )
    exit(3)

# - GUI - Start
main_window = tk.Tk()
main_window.title(translations["main_title"][installer["lang"]])
main_window.protocol("WM_DELETE_WINDOW", main_window.destroy)
mw_size = {
    "x": 600,
    "y": 125,
}
mw_center = {
    "x": (main_window.winfo_screenwidth() // 2) - (mw_size["x"] // 2),
    "y": (main_window.winfo_screenheight() // 2) - (mw_size["y"] // 2),
}
main_window.geometry(f"{mw_size['x']}x{mw_size['y']}+{mw_center['x']}+{mw_center['y']}")
main_window.resizable(False, False)

# - GUI - Variables
entrys = {
    "game_folder": tk.StringVar(),
    "folder_is_selected": tk.BooleanVar(),
    "selected_version": tk.StringVar(),
    "versions_available": [],
}

# - Check - Game folder
if os.path.exists(game["default_folder"]):
    entrys["game_folder"].set(game["default_folder"])
    entrys["folder_is_selected"].set(True)
    # TODO: integrar esto en la funcion get_game_version
    get_game_version(entrys)
else:
    entrys["game_folder"].set(
        f'<- {translations["folder_path_no_selected"][installer["lang"]]} '
    )
    entrys["folder_is_selected"].set(False)

# - GUI - (0 , 0) - Folder - Input
# TODO: cambiar el label del boton cuando se tenga una carpeta seleccionada
folder_select_button = tk.Button(
    master=main_window,
    text=translations["folder_select_button"][installer["lang"]],
    command=lambda: get_game_folder(entrys),
)
folder_select_button.grid(row=0, column=0, padx=10, pady=10)

# - GUI - (0 , 1) - Folder - Label
folder_path_label = tk.Entry(
    master=main_window, textvariable=entrys["game_folder"], state="disabled", width=75
)
folder_path_label.grid(row=0, column=1, pady=10)

# - GUI - (1 , 0) - Version - Dropdown
# TODO: desactivar el dropdown si no hay carpeta seleccionada y motrar un mensaje
# TODO: si se selecciona ingles, se desactiva la traduccion
version_dropdown = tk.OptionMenu(
    main_window, entrys["selected_version"], *entrys["versions_available"]
)
version_dropdown.config(state="disabled", width=15)
version_dropdown.grid(row=1, column=0, padx=10)

# # - GUI - (1 , 1) - Language - Dropdown
# # TODO: desactivar el dropdown si no hay carpeta seleccionada y motrar un mensaje
# # TODO: si se selecciona ingles, se desactiva la traduccion
temp_lang = tk.StringVar()
# temp_lang.set(online_config['languages'][0])
temp_lang_small = "es_ES"
temp_lang.set(
    translations[temp_lang_small][installer["lang"]]
)  # TODO: acordarse de quitar esto
language_dropdown = tk.OptionMenu(main_window, temp_lang, *online_config["languages"])
language_dropdown.config(state="disabled", width=15)
language_dropdown.grid(row=1, column=1)

# - GUI - (2 , 0) - Uninstall - Button
# TODO: borrar la carpeta de configuracion del instalador, la linea de
#  configuracion del user.cfg, y borrar el archivo de traduccion
uninstall_button = tk.Button(
    master=main_window, text=translations["uninstall_button"][installer["lang"]]
)
uninstall_button.config(state="disabled", width=17)
uninstall_button.grid(row=2, column=0, padx=10, pady=10)

# - GUI - (2 , 1) - Install/Update - Button
# TODO: Comprueba si existe el archivo de configuracion del usuario en home, si no existe lo crea
# TODO: Si se selecciona ingles, se desactiva la traduccion, y muestra un texto, "Set default | Por defecto"
# TODO: Si se selecciona cualquier otro idioma, si en el archivo del home, no existe el idioma, el boton mostrara
#  "Install | Instalar", si existe, mostrara "Update | Actualizar"
install_button = tk.Button(
    master=main_window,
    text=translations["install_button"][installer["lang"]],
    command=lambda: install_localization(temp_lang_small),
)
install_button.config(width=17)
install_button.grid(row=2, column=1)

# - GUI - Show and cath Ctrl+C for exit
try:
    main_window.mainloop()
except KeyboardInterrupt:
    main_window.destroy()
