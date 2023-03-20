from dwdparse.stations import StationIDConverter


def test_station_id_converter(data_dir):
    c = StationIDConverter()
    c.load(path=data_dir / 'station_list.html')
    assert len(c.dwd_to_wmo) == 4
    assert len(c.wmo_to_dwd) == 5
    assert c.convert_to_wmo('00003') == '10501'
    assert c.convert_to_wmo('01766') == '10315'
    assert c.convert_to_dwd('10315') == '01766'
    # Always use the last row for duplicated DWD IDs
    assert c.convert_to_wmo('05745') == 'F263'