
import time

print(dom.VERSION)

server = dom.Server(address="192.168.1.26", port=8080)
print(server.address)
print(server.port)
print(server.protocol)

#if server.exists():
if False:
    print("Domoticz version ........... : {}".format(server.version))
    print("Build time ................. : {}".format(server.build_time_dt))
    print("DomoticzUpdateURL .......... : {}".format(server.domoticzupdateurl))
    print("Update available ........... : {}".format(server.haveupdate))
    print("\r")

    if server.haveupdate:
        server.update()

    print("--------------------------------------------------------------------------------")
    print("SunRiseSet")
    print("--------------------------------------------------------------------------------")
    print("servertime ................. : {}".format(server.servertime))
    print("servertime_dt .............. : {}".format(server.servertime_dt))
    print("act_time ................... : {}".format(server.act_time))
    print("\r")
    if server.has_location():
        print("Location set:")
        print("sunrise .................... : {}".format(server.sunrise))
        print("sunset ..................... : {}".format(server.sunset))
        print("sunrise_dt ................. : {}".format(server.sunrise_dt))
        print("sunset_dt .................. : {}".format(server.sunset_dt))
        print("is_day ..................... : {}".format(server.is_day))
        print("is_night ................... : {}".format(server.is_night))
    else:
        print("Location NOT set!!!")
        print("sunrise .................... : {}".format(server.sunrise))
    print("\r")

    print("--------------------------------------------------------------------------------")
    print("Log message")
    print("--------------------------------------------------------------------------------")
    server.logmessage("DomoticzAPI.server.logmessage: Test 1")
    print("querystring ................ : {}".format(server.api.querystring))
    print("url ........................ : {}".format(server.api.url))
    print("\r")

    print("--------------------------------------------------------------------------------")
    print("Settings")
    print("--------------------------------------------------------------------------------")
    print("AcceptNewHardware .......... : {}".format(
        server.setting.get_value("AcceptNewHardware")))
    if server.has_location():
        print("Latitude ................... : {}".format(
            server.setting.get_value("Location").get("Latitude")))
    print("SecPassword ................ : {}".format(
        server.setting.get_value("SecPassword")))
    print("Name ....................... : {}".format(
        server.setting.get_value("Title")))
else:
    print("Server not found!!!")
    print(server.api.message)
    

var1 = dom.UserVariable(
    server,
    "test_date",
    dom.UserVariable.UVE_TYPE_INTEGER,
    "0")
if var1.exists():
    print("'{}' exists in Domoticz".format(var1.name))
else:
    print("'{}' NOT exists in Domoticz".format(var1.name))

debut = time.time()
time.sleep(2)
fin = time.time()

print("Début : {}".format(debut))
print("Fin : {}".format(fin))
print("Durée : {}".format(fin-debut))

if var1.exists():
    var1.value = (round(debut))