import logging
import re

from dwdparse.utils import fetch


logger = logging.getLogger(__name__)


class StationIDConverter:

    STATION_LIST_URL = (
        'https://www.dwd.de/DE/leistungen/klimadatendeutschland/statliste/'
        'statlex_html.html?view=nasPublication')
    STATION_TYPES = ['SY', 'MN']

    def __init__(self):
        self.dwd_to_wmo = {}
        self.dwd_to_wmo_date = {}
        self.wmo_to_dwd = {}
        self.wmo_to_dwd_date = {}
        self.dwd_to_coords = {}
        self.wmo_to_coords = {}

    def load(self, path=None):
        logger.info("Updating station ID mappings")
        if path:
            with open(path) as f:
                station_list = f.read()
        else:
            station_list = fetch(self.STATION_LIST_URL).decode()
        self.parse_station_list(station_list)

    def parse_station_list(self, html):
        dwd_to_wmo = {}
        wmo_to_dwd = {}
        dwd_to_wmo_date = {}
        wmo_to_dwd_date = {}
        dwd_to_coords = {}

        for line in html.splitlines():
            if not line.startswith('<tr>') or not line.count('<td') == 11:
                continue
            values = re.findall(r'<td[^>]*?>(.*?)</td>', line)
            if values[2] not in self.STATION_TYPES:
                continue
            dwd_id = values[1].zfill(5)
            wmo_id = values[3]
            end_date = values[10]
            if not (dwd_id in dwd_to_wmo_date) or \
                (end_date[-4:] > dwd_to_wmo_date[dwd_id][-4:]): # use most current station based on year
                dwd_to_wmo[dwd_id] = wmo_id
                dwd_to_wmo_date[dwd_id] = end_date
                dwd_to_coords[dwd_id] = [values[4],values[5]]

            if not (wmo_id in wmo_to_dwd_date) or \
                (end_date[-4:] > wmo_to_dwd_date[wmo_id][-4:]): # use most current station based on year
                wmo_to_dwd[wmo_id] = dwd_id
                wmo_to_dwd_date[wmo_id] = end_date
                wmo_to_coords[wmo_id] = [values[4],values[5]]

        assert dwd_to_wmo, "Found no stations in station list"
        self.dwd_to_wmo = dwd_to_wmo
        self.dwd_to_wmo_date = dwd_to_wmo_date
        self.wmo_to_dwd = wmo_to_dwd
        self.wmo_to_dwd_date = wmo_to_dwd_date
        self.dwd_to_coords = dwd_to_coords
        self.wmo_to_coords = wmo_to_coords
        logger.info("Parsed %d station ID mappings", len(dwd_to_wmo))

    def convert_to_wmo(self, dwd_id):
        return self.dwd_to_wmo.get(dwd_id)

    def convert_to_dwd(self, wmo_id):
        return self.wmo_to_dwd.get(wmo_id)


_converter = StationIDConverter()
dwd_id_to_wmo = _converter.convert_to_wmo
wmo_id_to_dwd = _converter.convert_to_dwd
load_stations = _converter.load
