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
    config_file.set("DB", "USER", "user")
    config_file.set("DB", "PASSWORD", "password")
    config_file.set("DB", "DB", "db")

    config_file.add_section("GPIO")
    config_file.set("GPIO", "S1_ROSSO", "20")
    config_file.set("GPIO", "S1_VERDE", "21")
    config_file.set("GPIO", "S2_ROSSO", "22")
    config_file.set("GPIO", "S2_VERDE", "23")
    config_file.set("GPIO", "P_MANUALE", "24")

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

