from urlparse import urljoin

#meteotrentino api's url
METEOTRENTINO_URL = 'http://dati.meteotrentino.it'

#stations' list url
STATIONS_URL = urljoin(METEOTRENTINO_URL, '/service.asmx/listaStazioni')

#station last data url
STATION_LAST_DATA_URL = urljoin(METEOTRENTINO_URL,'/service.asmx/ultimiDatiStazione')

#sentry server url
SENTRY_URL = 'http://u:p@localhost:9000/1'
