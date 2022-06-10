import configparser
from guizero import App, PushButton, Box, Text
from datetime import datetime, timedelta
import teslapy

email = ""
vehicle_index = 0
suspend_minutes = 30

suspended_until = False
vehicles = []

def toogle_fullscreen():
  is_full = app.full_screen
  if is_full:
    app.tk.config(cursor="arrow")
  else:
    app.tk.config(cursor="none")
  app.full_screen = not app.full_screen

def exit_pressed():
  app.destroy()

def suspend_pressed():
  global suspend_minutes
  global suspended_until
  if suspended_until == False:
    suspended_until = datetime.now() + timedelta(minutes=suspend_minutes)
  else:
    suspended_until = False
    suspend_button.text = "Suspend"

def update_ui():
  global summary
  if summary == {}:
    return
  global suspended_until
  if suspended_until != False:
    timediff = suspended_until - datetime.now()
    if timediff.total_seconds() < 0:
      suspended_until = False
      suspend_button.text = "Suspend"
    else:
      suspend_button.text = str(timediff).split('.')[0]
      offline.visible = False
      sleeping.visible = False
      awake.visible = False
      charging.visible = False
      suspended.visible = True
      return

  if 'display_name' in summary:
    name_text.text = summary['display_name']
  if summary['state'] == 'online':
    if vd != {} and vd['charge_state']['charging_state'] == 'Charging':
      offline.visible = False
      sleeping.visible = False
      awake.visible = False
      charging.visible = True
      suspended.visible = False

      charging.text = 'Charging\n'
      charging.text += str(vd['charge_state']['battery_level']) + '%\n'
      charging.text += str(vd['charge_state']['minutes_to_full_charge']) + 'mins'

    else:
      offline.visible = False
      sleeping.visible = False
      awake.visible = True
      charging.visible = False
      suspended.visible = False
      sleeping.text = "Sleeping"
      if vd != {}:
        sleeping.text += "\n" + str(vd['charge_state']['battery_level']) + '%'
      awake.text = str(vd['charge_state']['battery_level']) + '%'
        
  elif summary['state'] == 'asleep':
    offline.visible = False
    sleeping.visible = True
    awake.visible = False
    charging.visible = False
    suspended.visible = False
  else:
    offline.visible = True
    sleeping.visible = False
    awake.visible = False
    charging.visible = False
    suspended.visible = False

def update_data():
  with teslapy.Tesla(email) as tesla:
    global vehicles
    if (vehicles == []):
      vehicles = tesla.vehicle_list()
    global summary
    global suspended_until
    summary = vehicles[vehicle_index].get_vehicle_summary()
    if summary['state'] == 'online' and suspended_until == False:
      global vd
      vd = vehicles[vehicle_index].get_vehicle_data()
      print(vd)
    update_ui()
  return

def sleeping_pressed():
  sleeping.bg = "blue"
  sleeping.text = "Wakey\n  wakey..."
  app.update()
  it_worked = True
  with teslapy.Tesla(email) as tesla:
    try:
      global vehicles
      vehicles[vehicle_index].sync_wake_up(timeout=20)
    except teslapy.VehicleError:
      it_worked = False
      sleeping.bg = "yellow"
      sleeping.text = "Didn't\nwake up :("
  if it_worked:
    sleeping.bg = "yellow"
    sleeping.text = "Sleeping"


def awake_pressed():
  if summary['state'] != 'online':
    return
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[vehicle_index].command('CHARGE_PORT_DOOR_OPEN')
    app.info("Open", "Open sesame")



def charging_pressed():
  if summary['state'] != 'online':
    return
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[vehicle_index].command('STOP_CHARGE')
    vehicles[vehicle_index].command('CHARGE_PORT_DOOR_OPEN')
    app.info("Unlock", "Unlocked")

config = configparser.ConfigParser()
config.read('settings.ini')
email = config["DEFAULT"]["Email"]
vechicle_index = config["DEFAULT"]["VehicleIndex"]
suspend_minutes  = config["DEFAULT"]["SuspendMinutes"]
summary = {}
vd = {}
text_size = 60
app = App(title="Tesla app")
app.repeat(1000, update_data)
toogle_fullscreen()
if (app.width > 1000):
  toogle_fullscreen()

menu = Box(app, layout="grid", width="fill")

suspend_button = PushButton(menu, grid=[0,0], command=suspend_pressed, text="Suspend", width="fill", align="right", padx=1, pady=1)
suspend_button.text_size = 15

toogle = PushButton(menu, grid=[1,0], command=toogle_fullscreen, text="Toogle fullscreen", width="fill", padx=1, pady=1)
toogle.text_size = 15

exit_button = PushButton(menu, grid=[2,0], command=exit_pressed, text="Exit", width="fill", padx=1, pady=1)
exit_button.text_size = 15

name_text = PushButton(menu, text="---", align="right", grid=[6,0], padx=1, pady=1)
name_text.text_size = 15





offline = PushButton(app, width="fill", height="fill", text="Offline")
offline.bg = "red"
offline.text_size = text_size

sleeping = PushButton(app, command=sleeping_pressed, width="fill", height="fill", text="Sleeping")
sleeping.bg = "yellow"
sleeping.text_size = text_size

awake = PushButton(app, command=awake_pressed, width="fill", height="fill", text="Awake")
awake.bg = "blue"
awake.text_size = text_size + 80

charging = PushButton(app, command=charging_pressed, width="fill", height="fill", text="Charging")
charging.bg = "green"
charging.text_size = text_size

suspended = PushButton(app,  width="fill", height="fill", text="Suspended")
suspended.bg = "grey"
suspended.text_size = text_size
update_data()
app.display()

