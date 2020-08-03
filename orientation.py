from math import radians, cos, sin, asin, sqrt, atan2, degrees


def bearing(base, mobile):
    base_coords, mobile_coords = (base.latitude, base.longitude), (mobile.latitude, mobile.longitude)
    base_lat = radians(base_coords[0])
    mobile_lat = radians(mobile_coords[0])
    diffLong = radians(mobile_coords[1] - base_coords[1])
    x = sin(diffLong) * cos(mobile_lat)
    y = cos(base_lat) * sin(mobile_lat) - (sin(base_lat) * cos(mobile_lat) * cos(diffLong))
    return (degrees(atan2(x, y)) + 360) % 360


def distance(p1, p2):
    R = 3959.87433  #mi or 6372.8 km
    R = R*5280  #(feet/mile)
    dLat = radians(p2.latitude - p1.latitude)
    dLon = radians(p2.longitude - p1.longitude)
    a = sin(dLat/2)**2 + cos(radians(p1.latitude))*cos(radians(p2.latitude))*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    return R * c
