from obspy import read_inventory

inv = read_inventory("files/inventario.xml")


inventario_txt = open("files/inventario.txt", "w")
inventario_txt.write("Station Latitude Longitude;\n")
# cria um arquivo de texto com station code, latitude e longitude
for network in inv:
    for station in network:
        lat = station.latitude
        lon = station.longitude
        inventario_txt.write(f"{station.code} {lat} {lon};\n")
