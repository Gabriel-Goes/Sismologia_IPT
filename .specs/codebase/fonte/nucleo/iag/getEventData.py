from obspy.clients.fdsn import Client as fdsnClient
from os import mkdir
from optparse import OptionParser
import re

import warnings
warnings.filterwarnings("ignore")


def filter2regexpattern(filter):
    newfilter = []
    for f in filter:
        newfilter.append(f.replace("*", ".+").replace("?", "."))
    return newfilter


def find_p_pick(station, picks):
    for pick in picks:
        if station == pick[2]:
            return pick

    else:
        return None


def find_pick_dist_azi(pickID, arrivals):
    for a in arrivals:
        if a.pick_id == pickID:
            dst = a.distance
            azm = a.azimuth
            return dst, azm


def separate_picks(picks, arrivals):
    """
    It will return PHASE NET STA PickTime DISTANCE AZIMUTH
    """
    pck_pwave = []
    pck_swave = []
    for pck in picks:

        _n = pck.waveform_id.network_code
        _s = pck.waveform_id.station_code
        _p = pck.phase_hint
        _t = pck.time
        _i = pck.resource_id
        _d, _z = find_pick_dist_azi(_i, arrivals)
        if _p == 'P':
            pck_pwave.append((_p, _n, _s, _t, _d, _z))
        elif _p == 'S':
            pck_swave.append((_p, _n, _s, _t, _d, _z))
        else:
            continue

    return pck_pwave, pck_swave


def get_data(pck, flt):

    frq_min = float(flt.split(',')[0])
    frq_max = float(flt.split(',')[1])
    netcode = pck['netcode']
    stacode = pck['stacode']
    ptime = pck['ptime']
    stime = pck['stime']
    window = (stime - ptime)

    try:
        st = fdsn.get_waveforms(network=netcode, station=stacode, location='', channel='HH*',
                            starttime=ptime - 10, endtime=ptime + 50, attach_response=True)
        st.detrend()
        st.taper(max_percentage=0.1)
        # st.filter(type='bandpass', freqmin=frq_min, freqmax=frq_max)
        # st.remove_response(output='DISP')

        # noise_slice = (st[0].copy()).trim(ptime - window, ptime)
        # signal_slice = (st[0].copy()).trim(ptime, ptime + window)
        #
        # #
        # ## Calc SNR
        # _snr = np.sum(signal_slice.data ** 2)
        # _snr /= np.sum(noise_slice.data ** 2)
        #
        # if _snr >= 1:
        #     print('%s SNR: %.1f' % (stacode, _snr))
        #     return st
        # else:
        #     return
        return st
    except:
        pass
        return None


#dumb message...
print ("\nDownloader tool to use with CNN Code\n")

# Usage string:
use = "Usage: %prog --help"
desc = """ To download data! """

# Calling Option Parser:
optParser = OptionParser(usage = use, description = desc)

optParser.add_option("-l", "--evids", dest="evids", help="To download specific events by its ID, "
                                                         "e.g. usp2016jufn or usp2016jufn,usp2024bszu", default=None)

optParser.add_option("-t", "--stList", dest="stList", help="OPTIONAL. List of patterns allowed for station codes "
                                                           "in the form of Net.Station, multiple can be separated "
                                                           "with ',' e.g. BL.DIAM, BL.*", default=None)

optParser.add_option("-p", "--plot", action="store_true", dest="plot", help="OPTIONAL. Plot the downloaded "
                                                                            "events for a quick check", default=None)

# The final step is to parse the options and arguments into variables we can use later:
opts, args = optParser.parse_args()


if opts.evids == None:
    optParser.print_help()
    print(
        "\nYou should use at least a event id to search data...\n")
    exit(-1)

# Setting out the pattern for station codes
stpatterns = opts.stList
if stpatterns:
    if stpatterns.find(",") != -1:
        stpatterns = stpatterns.split(",")
    else:
        stpatterns = [stpatterns]
    allowed_stations = filter2regexpattern(stpatterns)

# Setting out the pattern for event list
evids = opts.evids
if evids:
    if evids.find(",") != -1:
        events = evids.split(",")
    else:
        evids = [evids]


fdsn = fdsnClient(base_url='http://seisarc.sismo.iag.usp.br')
flt = ('1,50')

for evid in evids:

    evt = fdsn.get_events(eventid=evid, includearrivals=True)[0]

    ori = evt.preferred_origin()
    ev_time = ori.time
    ev_type = evt.event_type
    m_value = evt.preferred_magnitude().mag
    m_type = evt.preferred_magnitude().magnitude_type
    desc = evt.event_descriptions[0].text

    print(ev_type, ev_time, m_type+':', '%.2f' % m_value, desc)

    p_picks, s_picks = separate_picks(evt.picks, ori.arrivals)

    for s_pck in s_picks:

        station_pick = {}

        pha = s_pck[0]  # phase
        net = s_pck[1]  # net code
        sta = s_pck[2]  # sta code
        tos = s_pck[3]  # time of S
        dis = s_pck[4]  # distance
        azi = s_pck[5]  # azimuth

        p_pck = find_p_pick(sta, p_picks)

        if not p_pck:
            continue

        #
        ## To discard station not chosen
        fullcode = "%s.%s" % (net, sta)
        if stpatterns:
            for pattern in allowed_stations:
                if re.match(pattern, fullcode):
                    break
            else:
                continue

        top = p_pck[3]  # time of P

        # Populate Pick Dictionary:
        station_pick['netcode'] = net
        station_pick['stacode'] = sta
        station_pick['ptime'] = top
        station_pick['stime'] = tos
        station_pick['dist'] = dis
        station_pick['azi'] = azi

        y = str(ev_time.year)
        j = '%.3d' % ev_time.julday
        h = '%.2d' % ev_time.hour
        m = '%.2d' % ev_time.minute
        s = '%.2d' % ev_time.second

        evname = ''.join((y, j, 'T', h, m, s))
        filename = '_'.join((net, sta, evname)) + '.mseed'

        signal = get_data(station_pick, flt)
        if not signal: continue
        try:
            mkdir(evname)
        except:
            pass
        signal.write(evname+'/'+filename, format='MSEED')
        print('Found %s data' % (net+'.'+sta))
        if opts.plot:
            signal.plot()
