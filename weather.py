import requests
from lxml import etree
from lxml import objectify

import settings

def get_stations():
    """Returns list of available stations. Each station is a dictionary with
    attibutes : code, name, altitude, lat, lon, est, north"""

    #get stations details
    r = requests.get(settings.STATIONS_URL)
    r.raise_for_status()

    #parse stations details
    root = etree.fromstring(r.content)
    stations = []
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

    return stations

def get_station_last_data(station_code):
    """Returns a dictionary with the following entries:

    date, tmin, tmax, rain -> single values
    temperature, precipitation, wind, radiation ->
      lists of couples (date,value), lists are empty if no data found
    """

    #get station data
    parameters = {'codice' : station_code}
    r = requests.get(settings.STATION_LAST_DATA_URL, params=parameters)
    r.raise_for_status()

    #parse retrieved data
    root = etree.fromstring(r.content)
    data = {}
    data['date'] = root.find('{*}data').text
    data['tmin'] = root.find('{*}tmin').text
    data['tmax'] = root.find('{*}tmax').text
    data['rain'] = root.find('{*}rain').text
    data['temperature'] = []
    for temp in root.find('{*}temperature'):
        data['temperature'].append((temp.find('{*}data').text,
                                     temp.find('{*}temperatura').text))
    data['precipitation'] = []
    for prec in root.find('{*}precipitazioni'):
        data['precipitation'].append((prec.find('{*}data').text,
                                       prec.find('{*}pioggia').text))
    data['wind'] = []
    for wind in root.find('{*}venti'):
        data['wind'].append((wind.find('{*}data').text,
                             wind.find('{*}v').text,
                             wind.find('{*}d').text))
    data['radiation'] = []
    for rad in root.find('{*}radiazione'):
        data['radiation'].append((rad.find('{*}data').text,
                                  rad.find('{*}rsg').text))

    return data


if __name__=='__main__':
    stations = get_stations()
    for station in stations:
        print get_station_last_data(station['code'])
