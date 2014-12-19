import requests
from lxml import etree
from lxml import objectify
import raven
import traceback, sys

import settings

raven_client = raven.Client(settings.SENTRY_URL)

def notify_missing_attribute(error_url):
    _,_,tb = sys.exc_info()
    missing_attribute = traceback.extract_tb(tb)[-1][-1]
    raven_client.captureMessage('Could not get attribute {} from meteo'
                                'trentino API at url {}.'.format(
                                    missing_attribute,
                                    error_url))

def get_stations():
    """Returns list of available stations. Each station is a dictionary with
    attibutes : code, name, altitude, lat, lon, est, north"""

    #get stations details
    r = requests.get(settings.STATIONS_URL)
    if not r.ok:
        raven_client.captureMessage('Could not fetch meteo stations information'
                                    'from url '+settings.STATIONS_URL)
        return []

    #parse stations details
    root = etree.fromstring(r.content)
    stations = []
    try:
        for station in root:
        #assign identifiers to station's attributes
            stations.append(
                dict(code=station.find('{*}codice').text,
                     name=station.find('{*}nome').text,
                     altitude=station.find('{*}quota').text,
                     lat=station.find('{*}latitudine').text,
                     lon=station.find('{*}longitudine').text,
                     est=station.find('{*}est').text,
                     north=station.find('{*}north').text)
            )
    except AttributeError as e:
        _,_,tb = sys.exc_info()
        missing_attribute = traceback.extract_tb(tb)[-1][-1]
        raven_client.captureMessage('Could not get attribute {} from meteo'
                                    'trentino API at url {}.'.format(
                                        missing_attribute,
                                        settings.STATIONS_URL))
    return stations

def get_station_last_data(station_code):
    """Returns a dictionary with the following entries:

    date, tmin, tmax, rain -> single values
    temperature, precipitation, wind, radiation ->
      lists of couples (date,value), lists are empty if no data found
    """

    data = {'date': '',
            'tmin': '',
            'tmax': '',
            'rain': '',
            'temperature': [],
            'precipitation': [],
            'wind': [],
            'radiation': []}

    #get station data
    parameters = {'codice' : station_code}
    r = requests.get(settings.STATION_LAST_DATA_URL, params=parameters)
    if not r.ok:
        raven_client.captureMessage('Could not fetch data for station {} at'
                                    ' url {}.'.format(station_code,
                                                      r.url))
        return data

    #parse retrieved data
    root = etree.fromstring(r.content)

    #retrieve single values
    try:  data['date'] = root.find('{*}data').text
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:  data['tmin'] = root.find('{*}tmin').text
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:  data['tmax'] = root.find('{*}tmax').text
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:  data['rain'] = root.find('{*}rain').text
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    #retrieve lists of values
    try:
        for temp in root.find('{*}temperature'):
            data['temperature'].append((temp.find('{*}data').text,
                                        temp.find('{*}temperatura').text))
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:
        for prec in root.find('{*}precipitazioni'):
            data['precipitation'].append((prec.find('{*}data').text,
                                          prec.find('{*}pioggia').text))
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:
        for wind in root.find('{*}venti'):
            data['wind'].append((wind.find('{*}data').text,
                                 wind.find('{*}v').text,
                                 wind.find('{*}d').text))
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    try:
        for rad in root.find('{*}radiazione'):
            data['radiation'].append((rad.find('{*}data').text,
                                      rad.find('{*}rsg').text))
    except (AttributeError,TypeError): notify_missing_attribute(r.url)

    return data


if __name__=='__main__':
    stations = get_stations()
    for station in stations:
        get_station_last_data(station['code'])
