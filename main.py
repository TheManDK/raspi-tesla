from guizero import App, PushButton, Box
import teslapy

email = "elon@tesla.com"
vehicle_index = 0

def toogle_fullscreen():
  is_full = app.full_screen
  if is_full:
    app.tk.config(cursor="arrow")
  else:
    app.tk.config(cursor="none")
  app.full_screen = not app.full_screen

def exit_pressed():
  app.destroy()

def update_ui():
  if summary == {}:
    return
  if summary['state'] == 'online':
    if vd != {} and vd['charge_state']['charging_state'] == 'Charging':
      offline.visible = False
      sleeping.visible = False
      awake.visible = False
      charging.visible = True

      charging.text = 'Charging\n'
      charging.text += str(vd['charge_state']['battery_level']) + '%\n'
      charging.text += str(vd['charge_state']['minutes_to_full_charge']) + 'mins'

    else:
      offline.visible = False
      sleeping.visible = False
      awake.visible = True
      charging.visible = False

      awake.text = str(vd['charge_state']['battery_level']) + '%'
        
  elif summary['state'] == 'asleep':
    offline.visible = False
    sleeping.visible = True
    awake.visible = False
    charging.visible = False
  else:
    offline.visible = True
    sleeping.visible = False
    awake.visible = False
    charging.visible = False

def update_data():
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    global summary
    summary = vehicles[vehicle_index].get_vehicle_summary()
    if summary['state'] == 'online':
      global vd
      vd = vehicles[vehicle_index].get_vehicle_data()
    update_ui()
  return

def sleeping_pressed():
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[vehicle_index].sync_wake_up()

def awake_pressed():
  if summary['state'] != 'online':
    return
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[vehicle_index].command('CHARGE_PORT_DOOR_OPEN')



def charging_pressed():
  if summary['state'] != 'online':
    return
  with teslapy.Tesla(email) as tesla:
    vehicles = tesla.vehicle_list()
    vehicles[vehicle_index].command('STOP_CHARGE')
    vehicles[vehicle_index].command('CHARGE_PORT_DOOR_OPEN')

summary = {}
vd = {}
text_size = 60
app = App(title="Tesla app")
app.repeat(1000, update_data)
toogle_fullscreen()

menu = Box(app, layout="grid", width="fill")

toogle = PushButton(menu, grid=[0,0], command=toogle_fullscreen, text="Toogle fullscreen", width="fill")
toogle.text_size = 5
exit_button = PushButton(menu, grid=[1,0], command=exit_pressed, text="Exit", width="fill")
exit_button.text_size = 5


offline = PushButton(app, width="fill", height="fill", text="Offline")
offline.bg = "red"
offline.text_size = text_size

sleeping = PushButton(app, command=sleeping_pressed, width="fill", height="fill", text="Sleeping")
sleeping.bg = "yellow"
sleeping.text_size = text_size

awake = PushButton(app, command=awake_pressed, width="fill", height="fill", text="Awake")
awake.bg = "blue"
awake.text_size = text_size

charging = PushButton(app, command=charging_pressed, width="fill", height="fill", text="Charging")
charging.bg = "green"
charging.text_size = text_size

app.display()

