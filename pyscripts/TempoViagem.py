from obspy.clients.iris import Client

inventario_txt = open("files/inventario.txt", "r",
                      encoding="utf-8")
inventario = inventario_txt.readlines()
inventario_txt.close()



result = client.traveltime(evloc=(-36.122,-72.898),
    staloc=[(-33.45,-70.67),(47.61,-122.33),(35.69,139.69)],
    evdepth=22.9)
print(result.decode())
