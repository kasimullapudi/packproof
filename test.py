from pymongo import MongoClient

uri = "mongodb+srv://kasimullapudi42:YxDsHlSMsI7S7jwq@cluster0.rkyag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(uri)
    db = client['uploads']
    print("Connection successful!")
    print("Ping response:", db.command('ping'))
except Exception as e:
    print("Connection failed:", str(e))