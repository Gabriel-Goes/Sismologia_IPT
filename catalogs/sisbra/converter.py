#!/usr/bin/python3

##
# This code was designed and written 
# by Marcelo Belentani de Bianchi
# @ 2022
###

import argparse, sys
import datetime

#
# Parser
#

def pIo(v):
	v = v.strip("- ")
	if v == "": return None
	if len(v) < 1 or len(v) > 3: raise Exception(f'Bad io {v}')
	for i in v:
		if i not in "0123456789-":
			raise Exception(f'Bad io {v}')

	return v

def pcategoria(v):
	if v not in [ "A", "B", "C", "D", "R", "E", "I" ]:
		raise Exception(f'Bad category {v}')

	return v

def ptm(v):
	if v not in [ "-1", "0", "1", "2", "3", "4", "5" ]:
		raise Exception(f'Bad tm {v}')

	return v

def pstate(v):
	v = v.strip("- ")
	if v == "": return None

	if  len(v) > 2:
		raise Exception(f'Bad state {v}')

	ST  = [ "Acre", "AC",
			"Alagoas", "AL",
			"Amapá", "AP",
			"Amazonas", "AM",
			"Bahia", "BA",
			"Ceará", "CE",
			"Espírito Santo", "ES",
			"Goiás", "GO",
			"Maranhão", "MA",
			"Mato Grosso", "MT",
			"Mato Grosso do Sul", "MS",
			"Minas Gerais", "MG",
			"Pará", "PA",
			"Paraíba", "PB",
			"Paraná", "PR",
			"Pernambuco", "PE",
			"Piauí", "PI",
			"Rio de Janeiro", "RJ",
			"Rio Grande do Norte", "RN",
			"Rio Grande do Sul", "RS",
			"Rondônia", "RO",
			"Roraima", "RR",
			"Santa Catarina", "SC",
			"São Paulo", "SP",
			"Sergipe", "SE",
			"Tocantins", "TO",
			"Distrito Federal", "DF"
	]

	# ~ if v not in ST[1::2]:
		# ~ print(f'Bad state = {v}', file = sys.stderr)

	return v

def pfloat(v):
	if v == "": return None
	if v == "-" or v == "--": return None

	return float(v)

def pdate(a,b,c):
	Y = int(a)
	if Y < 1500 and Y > 2100:
		raise Exception(f'Bad Year = {Y}')

	M = b[:2].strip("-")
	if M == "":
		M = None
	else:
		M = int(M)
		if M < 1 or M > 12:
			raise Exception(f'Bad Month {M}')

	D = b[2:].strip("-")
	if D == "":
		D = None
	else:
		D = int(D)
		if D < 1 or M > 31:
			raise Exception(f'Bad day {D}')

	# Check for valid date!
	if Y is not None:
		if M is not None:
			if D is not None:
				event_date = datetime.date(Y,M,D)
			else:
				event_date = datetime.date(Y,M,15)
		else:
			event_date = datetime.date(Y,6,15)
	else:
		event_date = None

	c = c.strip("- ")

	h = None
	m = None
	s = None
	zone = ""

	if len(c) > 0:
		if c[-1] == "U":
			raise Exception(f'Bad U Zone {c}')

		if c[-1] == "L":
			zone = "L"
			c = c[:-1]

		if len(c) not in [ 2, 4, 6, 8, 9 ]:
			raise Exception(f'Number of fields in seconds is invalid {c}')

		if len(c) >=2:
			h = int(c[0:2])
			if h < 0 or h >= 24: raise Exception(f'Bad hour {h}')
			if len(c) >=4:
				m = int(c[2:4])
				if m < 0 or m >= 60: raise Exception(f'Bad minute {m}')
				if len(c) >=6:
					s = float(c[4:])
					if s < 0 or s >= 60: raise Exception(f'Bad second {m}')

	return Y,M,D,h,m,s,zone,event_date

#
# Formater
#

def fdate(Y,M,D,h,m,s,zone):
	Y = f'{Y:04d}' if Y is not None else ""
	M = f'{M:02d}' if M is not None else ""
	D = f'{D:02d}' if D is not None else ""
	h = f'{h:02d}' if h is not None else ""
	m = f'{m:02d}' if m is not None else ""
	s = f'{s:05.2f}' if s is not None else ""

	zone = str(zone)

	return (Y,M,D,h,m,s,zone)

def flat(v):
	if v is None: return ""

	return f'{v:+.3f}'

def flon(v):
	if v is None: return ""

	return f'{v:+.3f}'

def fdep(v):
	if v is None: return ""

	return f'{v:5.1f}'

def ferr(v):
	if v is None: return ""

	return f'{v:.0f}'

def fmag(v):
	if v is None: return ""

	return f'{v:4.1f}'

def ftm(v):
	if v is None: return ""

	return str(v)

def fcat(v):
	return fstr(v)

def fIo(v):
	return fstr(v)

def farea(v):
	if v is None: return ""

	return f'{v:f}'

def festado(v):
	return fstr(v)

def fstr(v):
	if v is None: return ""
	if "," in v:
		raise Exception(f'Found comma in str {v}')
	v = v.replace('"', "'")

	return '"' + str(v).strip(" ") + '"'

def mag2size(v, factor = 25):
	if v is None: return 2.0/factor
	if v < 2.0:   return 2.0/factor

	return v / factor + ((v-2.0)/(factor/3.5))**3

#
# Main code
#

if __name__ == "__main__":
	epilog = '''
	This is the sisbra swiss army knife, a validation and conversion tool.

	It was designed initially to validate and find mistakes in the file.
	After that, it was evolving gaining options to allow for exporting to
	CSV and GMT format.
	'''

	parser = argparse.ArgumentParser(prog = 'converter.py', 
	                                 description = 'Catalog Converter',
	                                 epilog = epilog)
	parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='Be verbose.')

	parser.add_argument('filename', metavar='Filename', type=str, help='The RAW catalog filename.', nargs='?')

	parser.add_argument('-of', '--output-format', dest = 'format', choices=[ 'csv', 'raw', 'gmt' ], help = 'What is the output format.', default = 'raw')
	parser.add_argument('-m', '--mode', dest = 'mode', choices=[ 'raw', 'clean', 'scr', 'scr2.5' ], help = 'What filter to apply to loaded file.', default = 'raw')

	parser.add_argument('-s', '--start', dest = 'start', help = 'Filter only events that occured after indicated START date.', type = datetime.date.fromisoformat, default = None)
	parser.add_argument('-e', '--end', dest = 'end', help = 'Filter only events that occured before indicated END date.', type = datetime.date.fromisoformat, default = None)
	parser.add_argument('-Sr', '--SearchRadius', dest='sr', help = 'Filter only events that occurred in a area around a specific location (input: radius_in_km/lon/lat [radius_in_km > 0])', type=str, default = None)

	group = parser.add_mutually_exclusive_group(required=False)
	group.add_argument('-H', dest='oldonly', action='store_true', help='Only print historic events (uses tm for selecting + mode filters).')
	group.add_argument('-I', dest='newonly', action='store_true', help='Only print instrumental events (uses tm for selecting + mode filters).')

	parser.add_argument('--gmt-legend', dest='gmt_leg', action='store_true', help='Print a legend string to GMT (input file is ignored).')
	parser.add_argument('--gmt-scale', dest='gmt_scale', type=int, default=25, help='Indicate a scaling factor for the GMT symbol size based on magnitude.')


	args = parser.parse_args()

	if args.gmt_leg:
		values = [6, 5, 4, 3, 2]
		mags = args.gmt_scale

		print('L 12p,Helvetica,black L Magnitude Instrumental:')
		print('G 0.3c')
		print('N 6')

		for i,m in enumerate(values[:-1]):
			msize = mag2size(m, mags)
			print(f'S 0.5 c {msize:.2f} red 1.0p 1. {m:.1f}')

		print(f'S 0.5 c {mag2size(values[-1],mags):.2f} red 1.0p 1. @~\\243@~ {values[-1]:.1f}')
		print('G 0.3c')
		print('N 2')
		print(f'S 0.5 c {mag2size(5,mags):.2f}   -  1.0p 1. Sentidos no Brasil')
		print(f'S 0.5 c {mag2size(5,mags):.2f} blue 1.0p 1. Sismos históricos')

		sys.exit(0)

	if args.filename is None or len(args.filename) == 0:
		print(f'No filename was supplied for processing - abort.', file = sys.stderr)
		sys.exit(1)

	if args.sr is not None:
		try:
			from obspy.geodetics import locations2degrees as loc2deg
			from obspy.geodetics import degrees2kilometers as deg2km
			
			sr_r, sr_lon, sr_lat = [ float(value) for value in args.sr.split('/') ]
		except ModuleNotFoundError:
			print(f'Feature you -Sr depends on modeule `obspy`.')
			sys.exit(1)
		except Exception as E:
			print(f'Invalid Search Radius - abort.', file = sys.stderr)
			sys.exit(1)

	#
	# Options
	#
	as_format = args.format
	mode      = args.mode

	#
	# Setup
	#
	csv_header = [ "year", "mm", "dd", "hh", "min", "ss.s", "L",
	               "latit", "longit", "depth", "err(km)", "mag", "tm",
	               "CAT", "Io", "Area", "ST", "Localities", "(source) comments" ]

	if args.verbose:
		print(f'Transforming {args.filename} using mode = {mode} and format = {as_format}', file = sys.stderr)

	with open(args.filename, "r") as fio:
		for i,raw_line in enumerate(fio):
			#
			# Loading part
			#
			raw_line = raw_line.rstrip("\n")
			line = raw_line.rstrip()

			if line[0] == "#":
				if as_format == "csv":
					if i == 0:
						print(",".join(csv_header), file = sys.stdout)
					continue
				if as_format == "raw":
					print(raw_line, file = sys.stdout)
					continue

				continue

			if line[0] != " ":
				raise Exception(f'Error on line {i} = {line}')

			try:
				p1 = line[:66]
				p1l = p1.split()
				Y,M,D,h,m,s,zone,event_date = pdate(p1l[0],p1l[1],p1l[2])
				latitude  = pfloat(p1l[3])
				longitude = pfloat(p1l[4])
				err       = pfloat(p1l[5])
				estado    = pstate(p1l[6])
				depth     = pfloat(p1l[7])
				mag       = pfloat(p1l[8])
				tm        = ptm(p1l[9])
				categoria = pcategoria(p1l[10])
				Io        = pIo(p1l[11])
				Af        = None

				if len(p1l) == 13:
					Af        = pfloat(p1l[12])

				localidade = line[66:89]
				comment    = line[89:]

				payload = fdate(Y,M,D,h,m,s,zone)

				payload = payload + (
					flat(latitude), flon(longitude), fdep(depth), ferr(err), fmag(mag), ftm(tm),
					fcat(categoria), fIo(Io), farea(Af), festado(estado), fstr(localidade), fstr(comment)
				)
			except Exception as E:
				print(f'Error on {i} - {line}', file = sys.stderr)
				print(E, file = sys.stderr)
				break

			#
			# Filter part
			#
			if mode in [ "clean", "scr", "scr2.5" ] and (categoria in [ "D", "R", "E" ] or err > 100.):
				continue

			# WARNING -- This filter is now 100% since some events has no complete dates
			if args.start is not None and (event_date is None or event_date < args.start):
				continue

			if args.end is not None and (event_date is None or event_date > args.end):
				continue

			if args.sr is not None:
				if latitude is None or longitude is None: continue
				if (deg2km(loc2deg(latitude, longitude, sr_lat, sr_lon)) > sr_r): continue

			if mode in [ "scr", "scr2.5" ]:
				if depth >= 60.0: continue
				if latitude is None: continue
				if longitude is None: continue
				if latitude > 5  and longitude > -45: continue
				if latitude > 0  and longitude > -40: continue
				if latitude > -5 and longitude > -32: continue

			if mode == "scr2.5" and mag < 2.5:
				continue

			if args.oldonly and tm not in [ '-1', '3', '4' ]:
				continue

			if args.newonly and tm not in [ '0', '1', '2', '5' ]:
				continue

			#
			# Dump part
			#
			if as_format == "raw":
				print(raw_line, file = sys.stdout)
			elif as_format == "csv":
				print(",".join(payload), file = sys.stdout)
			elif as_format == "gmt":
				print(longitude, latitude, mag2size(mag, args.gmt_scale))
			else:
				raise Exception(f'Bad as_format = {as_format}')
	
	sys.exit(0)
