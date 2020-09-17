import numpy as np

k0 = 0.9996
axis_a = 6378137.0
rf = 298.257223563


E = 2 / rf - 1 / rf / rf
EP = 2 / (rf - 1) + 1 / (rf - 1) / (rf - 1)
G = 1 / (2 * rf - 1)

E2 = E * E
E3 = E2 * E

G2 = G * G
G3 = G2 * G
G4 = G3 * G
G5 = G4 * G


M1 = 1 - 1 / 4 * E - 3 / 64 * E2 - 5 / 256 * E3
M2 = 3 / 8 * E + 3 / 32 * E2 + 45 / 1024 * E3
M3 = 15 / 256 * E2 + 45 / 1024 * E3
M4 = 35 / 3072 * E3

P2 = 3 / 2 * G - 27 / 32 * G3 + 269 / 512 * G5
P3 = 21 / 16 * G2 - 55 / 32 * G4
P4 = 151 / 96 * G3 - 417 / 128 * G5
P5 = 1097 / 512 * G4

B = k0 * axis_a
BM1 = B * M1

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def latitude_to_zone_letter(latitude):
    if -80 <= latitude <= 84:
        return ZONE_LETTERS[int(latitude / 8) + 10]
    return "Z"


def latlng_to_zone_number(latitude, longitude):
    if 3 <= longitude < 12 and 56 <= latitude < 64:
        return 32

    if longitude >= 0 and 72 <= latitude <= 84:
        if longitude < 9:
            return 31
        if longitude < 21:
            return 33
        if longitude < 33:
            return 35
        if longitude < 42:
            return 37

    return int(longitude / 6) + 31


def zone_number_to_central_longitude(zone_number):
    return zone_number * 6 - 183


def calulate_lng_offset(longitude, zone_number):
    central_lng = zone_number_to_central_longitude(zone_number)
    return np.deg2rad(longitude) - np.deg2rad(central_lng)


def utm_to_latlng(easting, northing, zone_number, zone_letter=None, is_northern=None):
    """Converts an UTM coordinate into Latitude and Longitude

        Parameters
        ----------
        easting: int
            Easting value of UTM coordinate

        northing: int
            Northing value of UTM coordinate

        zone number: int
            Zone Number is represented with global map numbers of an UTM Zone
            Numbers Map. More information see utmzones [1]_

        zone_letter: str
            Zone Letter can be represented as string values. Where UTM Zone
            Designators can be accessed in [1]_

        is_northern: bool
            You can set True or False to set this parameter. Default is None


       .. _[1]: http://www.jaworski.ca/utmzones.htm

    """
    if zone_letter is None and is_northern is None:
        raise ValueError("either zone_letter or is_northern needs to be set")

    if zone_letter is not None:
        if zone_letter not in ZONE_LETTERS:
            raise ValueError("zone letter out of range (must be between C and X)")

        is_zone_northern = zone_letter > "M"
        if is_northern is not None:
            if is_northern != is_zone_northern:
                raise ValueError("zone letter conflicts is_northern")
        is_northern = is_zone_northern

    if zone_number < 0 or zone_number > 60:
        raise ValueError("zone number out of range (must be between 1 and 60)")

    if easting < 100000 or easting >= 1000000:
        raise ValueError("easting out of range (must be between 100000 m and 999999 m)")

    if northing < 0 or northing > 10000000:
        raise ValueError("northing out of range (must be between 0 m and 10000000 m)")

    x = easting - 500000
    y = northing

    if not is_northern:
        y -= 10000000

    mu = y / BM1

    phi_rad = (
        mu
        + P2 * np.sin(2 * mu)
        + P3 * np.sin(4 * mu)
        + P4 * np.sin(6 * mu)
        + P5 * np.sin(8 * mu)
    )

    sin_phi = np.sin(phi_rad)
    cos_phi = np.cos(phi_rad)
    tan_phi = np.tan(phi_rad)

    T = tan_phi * tan_phi
    T2 = T * T

    ep_sin = 1 - E * sin_phi ** 2
    ep_sin_sqrt = np.sqrt(ep_sin)

    R = (1 - E) / ep_sin

    C = EP * cos_phi ** 2
    C2 = C * C

    D = x * ep_sin_sqrt / B

    D2 = D * D
    D3 = D2 * D
    D4 = D3 * D
    D5 = D4 * D
    D6 = D5 * D

    latitude = phi_rad - tan_phi / R * (
        1 / 2 * D2
        - (5 + 3 * T + 10 * C - 4 * C2 - 9 * EP) / 24 * D4
        + (61 + 90 * T + 298 * C + 45 * T2 - 252 * EP - 3 * C2) / 720 * D6
    )

    longitude = (
        D
        - (1 + 2 * T + C) / 6 * D3
        + (5 - 2 * C + 28 * T - 3 * C2 + 8 * EP + 24 * T2) / 120 * D5
    ) / cos_phi

    return (
        np.rad2deg(latitude),
        np.rad2deg(longitude) + zone_number_to_central_longitude(zone_number),
    )


def latlng_to_utm(latitude, longitude):
    """Converts Latitude and Longitude to UTM coordinate

        Parameters
        ----------
        latitude: float
            Latitude between 80 deg S and 84 deg N, e.g. (-80.0 to 84.0)

        longitude: float
            Longitude between 180 deg W and 180 deg E, e.g. (-180.0 to 180.0).
    """
    if not -80.0 <= latitude <= 84.0:
        raise ValueError(
            "latitude out of range (must be between 80 deg S and 84 deg N)"
        )
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(
            "longitude out of range (must be between 180 deg W and 180 deg E)"
        )

    lat_rad = np.deg2rad(latitude)
    sin_lat = np.sin(lat_rad)
    cos_lat = np.cos(lat_rad)
    tan_lat = np.tan(lat_rad)
    T = tan_lat * tan_lat

    zone_number = latlng_to_zone_number(latitude, longitude)
    lng_offset = calulate_lng_offset(longitude, zone_number)

    A = cos_lat * lng_offset

    N = 1 / np.sqrt(1 - E * sin_lat ** 2)
    C = EP * cos_lat ** 2

    A2 = A * A
    A3 = A2 * A
    A4 = A2 * A2
    A5 = A2 * A3
    A6 = A3 * A3

    T2 = T * T

    BN = B * N

    easting = (
        BN
        * (A + (1 - T + C) / 6 * A3 + (5 - 18 * T + T2 + 72 * C - 58 * EP) / 120 * A5)
        + 500000
    )

    M = (
        M1 * lat_rad
        - M2 * np.sin(2 * lat_rad)
        + M3 * np.sin(4 * lat_rad)
        - M4 * np.sin(6 * lat_rad)
    )

    northing = B * M + BN * tan_lat * (
        1 / 2 * A2
        + (5 - T + 9 * C + 4 * C * C) / 24 * A4
        + (61 - 58 * T + T2 + 600 * C - 330 * EP) / 720 * A6
    )

    if latitude < 0:
        northing += 10000000

    zone_letter = latitude_to_zone_letter(latitude)

    return easting, northing, zone_number, zone_letter
