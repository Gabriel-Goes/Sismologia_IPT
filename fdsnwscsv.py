# -*- coding: utf-8 -*-

from __future__ import print_function
from obspy import UTCDateTime
from obspy.clients import fdsn
import sys, utm
from dateutil import relativedelta

class Exporter(object):
	def __init__(self, sep = ";", where = sys.stderr):
		self._ = False
		if isinstance(where, str):
			where =  open(where, "w")
			self._iopen = True
		self._where = where
		self._gotheader = False
		self._sep = sep
		self.fformat = "{:8.4f}"
	
	def __enter__(self):
		if self._iopen: print("Writing to file: {}".format(self._where.name))
		return self
	
	def __exit__(self, type, value, tb):
		if self._iopen:
			print("Closing file {}.".format(self._where.name))
			self._where.close()
	
	def translate(self, evtype):
		evlist = {
			'earthquake'   : 'E',
			'quarry blast' : 'Q',
			'induced or triggered event': 'I'
		}
		if evtype not in evlist:
			return None
		return evlist[evtype]
		
	def flushheader(self):
		if self._gotheader: return
		headers  = [ 'ID', 'Hora de Origem (UTC)','Longitude', 'Latitude', 'UTM X', 'UTM Y', 'MLv', 'Energia', 'Cat' ]
		headersu = [ '', '', '(°)', '(°)', '(m)', '(m)', '', '(J)', '' ]
		print(self._sep.join(headers), file = self._where)
		print(self._sep.join(headersu), file = self._where)
		self._gotheader = True
	
	def feed(self, e, o, m, ID):
		if e.event_type not in ['earthquake', 'quarry blast', 'induced or triggered event']: return False
		
		self.flushheader()
		
		data = []
		if e.resource_id.id.split("/")[-1].split("_")[0] == ID or e.resource_id.id.split("/")[-1].split("z")[0] == 'gf':
			
			# Id
			##
			data.append(e.resource_id.id.split("/")[-1])
			
			# Origin Time
			## 
			t = e.preferred_origin().time
			data.append(t.strftime("%Y-%m-%dT%H:%M:%S"))			
			
			# Coords
			##
			data.append(self.fformat.format(o.longitude))
			data.append(self.fformat.format(o.latitude))
			
			# UTM
			##
			if o.latitude <= 84 and o.latitude >= -84:
				(ux, uy, _, _) = utm.from_latlon(o.latitude, o.longitude)
				data.append("{}".format(ux))
				data.append("{}".format(uy))
			else:
				data.extend([None, None])
			
			# Magnitude
			##
			try:
				data.append("{:3.1f}".format(m.mag))
			except:
				print("Event has no magnitude --- {}".format(e.resource_id.id))
				return False
			
			E = 10**(9.9 + 1.9*m.mag - 0.0024*m.mag**2)/1.0E7
			data.append("{:g}".format(E))
			
			data.append(self.translate(e.event_type))
			
			print(self._sep.join(map(str, data)), file = self._where)
			
			return True

if __name__ == "__main__":
	ta = UTCDateTime(sys.argv[1])
	te = UTCDateTime(sys.argv[2])
	ID = sys.argv[3]
	##
	# = "m" para andar por mes
	# qq outra coisa, para fazer todo o periodo
	mode = "m"
	
	ID_dict = {"MC":'8091',
		   "IT":'8091',
		   "SP":'8085',
		   "PB":'8093',
		   "BC":'8089'}
	
	_CL = fdsn.Client('http://localhost:' + ID_dict[ID])
	print('Client = %s' % _CL)
	
	while ta < te:
		if mode == "m":
			taa = UTCDateTime(ta.datetime + relativedelta.relativedelta(months=1))
			filename=ta.strftime("events-%Y-%m-%d") + "-%s.csv" % ID
		else:
			taa = te
			filename = "events-all.csv"
		
		try:
			print("Time interval from {} to {}.".format(ta, taa))
			catalog = _CL.get_events(ta, taa)
			with Exporter(where = filename) as exporter:
				for e in catalog:
					o = e.preferred_origin()
					m = e.preferred_magnitude()
					exporter.feed(e,o,m,ID)
			print("")
		except fdsn.header.FDSNNoDataException:
			print("No data for period {} to {}".format(ta, taa))
		
		ta = taa
