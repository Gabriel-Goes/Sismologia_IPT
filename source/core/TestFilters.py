# Autor: Lucas Schirbel
# Coautor: Marcelo Biachi
# Modificado por Gabriel Góes Rocha de Lima.


# ------------------------------ IMPORTS ------------------------------------ #
from __future__ import print_function, division

import sys

import numpy as np
import matplotlib.pyplot as plt
from obspy.core import UTCDateTime, AttribDict
from obspy import Trace
import datetime
from obspy.clients.fdsn import Client
import argparse


# ------------------------------ FUNCTIONS ---------------------------------- #
# GET TRACES AND DATA
def get(startime: datetime.datetime,
        endtime: datetime.datetime,
        network: str,
        station: str,
        location: str,
        channel: str) -> Trace:
    '''
    Get a trace from a given network, station, location and channel
    between the given startime and endtime.

    :param startime: Start time of the trace
    :param endtime: End time of the trace
    :param network: Network code
    :param station: Station code
    :param location: Location code
    :param channel: Channel code

    :return: Trace object
    '''
    # REMOVER VARIÁVEL GLOBAL, ADICIONAR ARQUIVO DE CONFIGURAÇÃO PARA MAIOR SEG
    global USER, PASSWD
    # REMOVER URL HARDCODED, CRIAR ARQUIVO DE CONFIGURAÇÃO OU TERM INPUT
    client = Client("http://10.100.0.150:8080", user=USER, password=PASSWD)

    try:
        stream = client.get_waveforms(
            network,
            station,
            location,
            channel,
            starttime=startime,
            endtime=endtime)

    except Exception as e:
        print("Error: ", e)
        return None

    trace = stream[0]
    if trace.stats.starttime > startime or trace.stats.endtime < endtime:
        return None

    return trace


# PREPARE THE TRACE FOR ANALYSIS
def prepare(trace: Trace,
            filtro: AttribDict,
            noisewindow: AttribDict,
            pwindow: AttribDict,
            swindow: AttribDict) -> (np.ndarray, np.ndarray, np.ndarray):
    '''
    Prepare the trace for the analysis.

    :param trace: Trace object
    :param filtro: Filter object
    :param noisewindow: Noise window object
    :param pwindow: P window object
    :param swindow: S window object

    :return: Tuple with the noise, P and S windows
    '''
    trace = trace.copy()
    # Pre-process
    trace.detrend('linear')
    trace.filter("bandpass", corners=4, freqmin=filtro.pa, freqmax=filtro.pb)
    # Copy & trim
    noise = trace.copy().trim(noisewindow.t - noisewindow.w / 2,
                              noisewindow.t + noisewindow.w / 2)
    pwindow = trace.copy().trim(pwindow.t - pwindow.w / 2,
                                pwindow.t + pwindow.w / 2)
    swindow = trace.copy().trim(swindow.t - swindow.w / 2,
                                swindow.t + swindow.w / 2)

    return noise.data, pwindow.data, swindow.data


# CALCULATES SIGNAL TO NOISE RATIO OF EACH PHASE
def ratios(trace,
           filtros,
           noisewindow,
           pwindow,
           swindow):
    for filtro in filtros:
        noise, trace_p, trace_s = prepare(trace, filtro, noisewindow,
                                          pwindow, swindow)
        filtro.noise = np.mean(np.abs(noise))
        filtro.p = np.mean(np.abs(trace_p))
        filtro.s = np.mean(np.abs(trace_s))
        filtro.snrp = filtro.p / filtro.noise
        filtro.snrs = filtro.s / filtro.noise


# CREATES A LIST OF FILTER VALUES TO BE USED BY THE FDSN CLIENT
def filterCombos(start=1, end=35, minw=2, maxw=6):
    filtros = list()

    for j in np.arange(start, end - minw + 1., 1.):
        for i in np.arange(j, end + 1., 1.):
            if (i - j) >= minw and (i - j) <= maxw:
                filtros.append(AttribDict({
                    'pa': j,
                    'pb': i,
                    'noise': -1,
                    'p': -1,
                    's': -1,
                    'snrp': -1,
                    'snrs': -1
                }))
    return filtros


# WRITES OUTPUT TO FILE
def write(data):
    raise Exception("No funciona mais!")

    fout = open("filters.txt", "w")
    z_p = np.array([data[key].p for key in sorted(data.keys())])
    norm_p = np.max(z_p)
    z_s = np.array([data[key].s for key in sorted(data.keys())])
    norm_s = np.max(z_s)
    fout.write("# pa pb snr_p snr_s\n")
    for key in sorted(data.keys()):
        fout.write("%s %.03f %.03f\n" % (key,
                                         data[key].p / norm_p,
                                         data[key].s / norm_s))
    fout.close()


# MAKES THE COMMAND LINE PARSER
def make_cmdline_parser():
    parser = argparse.ArgumentParser(description='Display event summary',
                                     usage='%(prog)s [options]')

    parser.add_argument("-wn", dest="wn", default=None,
                        help="Noise window specification Date/Length.")
    parser.add_argument("-wp", dest="wp", default=None,
                        help="P-window specification Date/Length.")
    parser.add_argument("-ws", dest="ws", default=None,
                        help="S-window specification Date/Length.")
    parser.add_argument("-S", dest="ns", default=None,
                        help="Network.Station.Location.Channel to make the analysis")
    parser.add_argument("-p", "--preview-window",
                        action="store_true", dest="preview", default=False,
                        help="Preview data & windows that will be used.")
    parser.add_argument("-jp", "---just-preview",
                        action="store_true", dest="justpreview", default=False,
                        help="Preview data & windows that will be used and quit.")
    parser.add_argument("-g", "--graph",
                        action="store_true", dest="graph", default=False,
                        help="Plot graphs as scatter points")
    parser.add_argument("-t", "--trisurf",
                        action="store_true", dest="trisurf", default=False,
                        help="Draw a surface connecting points")
    parser.add_argument("-m", "--mesh",
                        action="store_true", dest="mesh", default=False,
                        help="Plot meshes for p and s")
    parser.add_argument("-o", "--output",
                        action="store_true", dest="makeoutput", default=False,
                        help="Save results as PNG.")

    return parser


# DOES WHAT THE NAME SUGGESTS
def plot2d(filtros, norm=False, makeoutput=None):
    x = np.array([filtro.pa for filtro in filtros])
    y = np.array([filtro.pb for filtro in filtros])

    z_p = np.array([filtro.snrp for filtro in filtros])
    if norm:
        z_p = z_p / np.max(z_p)

    z_s = np.array([filtro.snrs for filtro in filtros])
    if norm:
        z_s = z_s / np.max(z_s)

    fig = plt.figure(figsize=(10, 5))
    axp = fig.add_subplot(1, 2, 1)
    axs = fig.add_subplot(1, 2, 2)

    axp.set_xlabel("High Pass (Hz)")
    axp.set_ylabel("Low Pass (Hz) ")
    axp.set_title("S/N Ratio for P-wave")

    axs.set_xlabel("High Pass (Hz)")
    axs.set_ylabel("Low Pass (Hz) ")
    axs.set_title("S/N Ratio for PwP-wave")

    caxp = axp.tricontourf(x, y, z_p)
    caxs = axs.tricontourf(x, y, z_s)

    fig.colorbar(caxp, ax=axp)
    fig.colorbar(caxs, ax=axs)

    plt.tight_layout()

    if makeoutput is not None:
        plt.savefig("{}_{}.png".format(makeoutput, "ratio2D"))
    else:
        plt.show()
    plt.close()

    return


def plot3d(filtros, trisurf, makeoutput):
    x = np.array([filtro.pa for filtro in filtros])
    y = np.array([filtro.pb for filtro in filtros])

    z_p = np.array([filtro.snrp for filtro in filtros])
    z_p = z_p / np.max(z_p)

    z_s = np.array([filtro.snrs for filtro in filtros])
    z_s = z_s / np.max(z_s)

    fig = plt.figure(figsize=(20, 20))

    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.set_xlabel("High Pass (Hz)", labelpad=15)
    ax.set_ylabel("Low Pass (Hz) ", labelpad=15)
    ax.set_title("S/N Ratio for Different Filters", pad=35)

    ax.scatter(x, y, z_p, color='red', label='P')
    ax.scatter(x, y, z_s, color='black', label='S')

    if trisurf:
        ax.plot_trisurf(x, y, z_p, color='0.2', alpha=0.7)
        ax.plot_trisurf(x, y, z_s, color='0.2', alpha=0.7)

    plt.legend()

    if makeoutput is not None:
        plt.savefig("{}_{}.png".format(makeoutput, "ratio3D"))
    else:
        plt.show()
    plt.close()

    return


# Parse the data and window length to consider
def parsewindow(line):
    date, w = line.split("/")
    w = float(w)
    date = UTCDateTime(date)
    return AttribDict({
        't': date + w / 2,
        'w': w
    })


# Program main body
if __name__ == '__main__':
    global USER, PASSWD
    PASSWD = 'data2@lucas'
    USER = 'lucas'

    args = None

    parser = make_cmdline_parser()
    args = parser.parse_args()

    pwindow = swindow = noisewindow = None

    if args.wn is not None:
        noisewindow = parsewindow(args.wn)

    if args.wp is not None:
        pwindow = parsewindow(args.wp)

    if args.ws is not None:
        swindow = parsewindow(args.ws)

    try:
        N, S, L, C = str(args.ns).split(".")
    except ValueError:
        print("Bad channel specification, use -S to specify a valid one")

    if pwindow is None or swindow is None or noisewindow is None:
        print("No windows found", file=sys.stderr)
        sys.exit(1)

    if not args.preview and \
       not args.graph and \
       not args.trisurf and \
       not args.mesh and \
       not args.justpreview:
        print("Nothing to do!")
        sys.exit(1)

    trace = get(noisewindow.t - noisewindow.w - 2,
                swindow.t + swindow.w + 5,
                N, S, L, C)

    if args.preview or args.justpreview:
        trace_copy = trace.copy()
        trace_copy.detrend('linear').filter('bandpass', corners=4,
                                            freqmin=5.0, freqmax=15.0)
        t = np.arange(trace_copy.stats.npts) * trace_copy.stats.delta

        a, b = \
            noisewindow.t - trace_copy.stats.starttime - noisewindow.w / 2, \
            noisewindow.t - trace_copy.stats.starttime + noisewindow.w / 2

        plt.axvspan(a, b, alpha=0.5, label='Noise Window', color='red')

        a, b = \
            pwindow.t - trace_copy.stats.starttime - pwindow.w / 2, \
            pwindow.t - trace_copy.stats.starttime + pwindow.w / 2
        plt.axvspan(a, b, alpha=0.5, label='P-Window', color='yellow')

        a, b = \
            swindow.t - trace_copy.stats.starttime - swindow.w / 2, \
            swindow.t - trace_copy.stats.starttime + swindow.w / 2
        plt.axvspan(a, b, alpha=0.5, label='S-Window', color='green')

        plt.plot(t, trace_copy.data, c='k')
        plt.legend()

        if args.makeoutput:
            plt.savefig(
                "{}.{}.{}.{}_{}_preview.png".format(N, S, L, C, pwindow.t))
        else:
            plt.show()

        plt.close()
        if args.justpreview:
            sys.exit(0)

    filtros = filterCombos(1., 35., 2., 12.)
    ratios(
        trace, filtros, noisewindow,
        pwindow,
        swindow)

    if args.graph or args.trisurf:
        plot3d(filtros, args.trisurf, makeoutput="{}.{}.{}.{}_{}".format(
            N, S, L, C, pwindow.t) if args.makeoutput else None)

    if args.mesh:
        plot2d(filtros, makeoutput="{}.{}.{}.{}_{}".format(
            N, S, L, C, pwindow.t) if args.makeoutput else None)

    sys.exit(0)
