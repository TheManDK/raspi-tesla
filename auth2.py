import teslapy
import webview
import configparser
config = configparser.ConfigParser()
config.read('settings.ini')
email = config["DEFAULT"]["Email"]

def custom_auth(url):
        result = ['']
        window = webview.create_window('Login', url)
        def on_loaded():
                result[0] = window.get_current_url()
                if 'void/callback' in result[0].split('?')[0]:
                        window.destroy()
        window.loaded += on_loaded
        webview.start()
        return result[0]

with teslapy.Tesla(email, authenticator=custom_auth) as tesla:
        tesla.fetch_token()
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        print(vehicles[0].get_vehicle_data()['vehicle_state']['car_version'])
