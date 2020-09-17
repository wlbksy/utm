import pytest

from utm import latlng_to_utm, utm_to_latlng


def test_center():
    lat, lng = 39.90708, 116.39122
    easting, northing, zone_number, zone_letter = latlng_to_utm(lat, lng)

    converted_lat, converted_lng = utm_to_latlng(
        easting, northing, zone_number, zone_letter
    )

    assert zone_number == 50
    assert zone_letter == "S"
    assert easting == pytest.approx(447964.1787141946, abs=1e-3)
    assert northing == pytest.approx(4417621.446515778, abs=1e-3)
    assert converted_lat == pytest.approx(lat, abs=1e-6)
    assert converted_lng == pytest.approx(lng, abs=1e-6)
