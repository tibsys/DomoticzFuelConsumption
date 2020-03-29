from datetime import datetime
import json
import os

duration_in_s = 3600
s_in_hour = 1/3600
debit_par_heure = 2.4 #L/h
debit_par_seconde = 2.4*s_in_hour
consommation = duration_in_s*debit_par_seconde

print(duration_in_s)
print(s_in_hour)
print(debit_par_heure)
print(debit_par_seconde)
print(consommation)

filedir = os.path.dirname(os.path.realpath(__file__))
print(filedir)

def readDb():
    try:
        with open('fuel_consumption.json', 'r') as f:
            try:
                data = json.load(f)
                print(json.dumps(data))
                return data
            except:    
                print("ko")
                return None
    except:
        print("pas de fichier")
        return False

def updateDb(data):
    with open('fuel_consumption.json', 'w') as f:
        try:
            json.dump(data, f)
        except(json.decoder.JSONDecodeError):
            print("ko")
            return False            

def initDb(data):
    with open('fuel_consumption.json', 'w+') as f:
        try:
            data = json.load(f)
            return True
        except(json.decoder.JSONDecodeError):
            print("Initialize db file")
            json.dump({"today": 0.0, "total": 0.0, "current_date": "1970-01-01", "total_duration": 0}, f)
            return True

    return False

data = readDb()
if data == False:
    res = initDb(data)
    print(res)

data = readDb()    
json.dumps(data)
data["total"] = 3.88821
updateDb(data)
data = readDb()    
json.dumps(data)