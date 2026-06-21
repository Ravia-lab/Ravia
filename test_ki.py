from ravia_ki.device_recognizer import DeviceRecognizer

rec = DeviceRecognizer()

text = "LG Therma V 16kW R290 Monoblock"
info = rec.parse(text)

print(info)
