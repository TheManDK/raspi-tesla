import teslapy
import configparser
config = configparser.ConfigParser()
config.read('settings.ini')
email = config["DEFAULT"]["Email"]

with teslapy.Tesla(email) as tesla:
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        print(vehicles[0].get_vehicle_data()['vehicle_state']['car_version'])
