import configparser

def write():
    # CREATE OBJECT
    config_file = configparser.ConfigParser()
    # ADD SECTION
    config_file.add_section("CAMERA")
    # ADD SETTINGS TO SECTION
    config_file.set("CAMERA", "USER", "admin")
    config_file.set("CAMERA", "PASSWORD", "SestanteA")
    config_file.set("CAMERA", "PORT", "554")
    config_file.set("CAMERA", "IP", "192.168.188.39")

    config_file.add_section("DB")
    config_file.set("DB", "HOST", "localhost")
    config_file.set("DB", "USER", "root")
    config_file.set("DB", "PASSWORD", "SestanteA")
    config_file.set("DB", "DB", "cef_bergamo")

    config_file.add_section("GPIO")
    config_file.set("GPIO", "S_ROSSO", "7")
    config_file.set("GPIO", "S_VERDE", "13")
    config_file.set("GPIO", "CICALINO", "15")
    config_file.set("GPIO", "P_MANUALE", "22")
    config_file.set("GPIO", "P_AUTOMATICO", "37")
    config_file.set("GPIO", "PRESENZA_MEZZO", "29")
    config_file.set("GPIO", "CHIAMATA", "31")
    config_file.set("GPIO", "PROCEDURA_OK", "16")

    # SAVE CONFIG FILE
    with open(r"configurations.ini", 'w') as configfileObj:
        config_file.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()

    print("Config file 'configurations.ini' created")

def read():
    config = configparser.ConfigParser()
    config.read(r"configurations.ini")

    return config

