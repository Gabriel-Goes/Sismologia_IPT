from obspy.clients.fdsn import Client
from obspy import UTCDateTime

# MOHO IAG = https://www.moho.iag.usp.br/fdsnws/
client = Client(base_url='http://localhost:8091')

start_time = UTCDateTime("2022-01-01")
end_time = UTCDateTime("2022-01-31")

catalog = client.get_events(starttime=start_time,endtime=end_time,includearrivals=True)

print("Número de eventos: ", len(catalog))


# Get magnitude of an event
# se existir
for event in catalog:
    if event.preferred_magnitude():
        print(event.preferred_magnitude().mag)
    else:
        pass
