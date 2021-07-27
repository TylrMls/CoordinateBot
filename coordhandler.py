import re

suffixes = ["N", "E", "S", "W"]


def check_dms_bounds(lat, long):
    if -90 <= lat[0] <= 90 and -180 <= long[0] <= 180:
        if 0 <= lat[1] < 60 and 0 <= long[1] < 60:
            if 0 <= lat[2] < 60 and 0 <= long[2] < 60:
                return True
    return False


def convert_ddms(lat, long):
    latitude = re.split("\u00b0|['\"]", lat)
    longitude = re.split("\u00b0|['\"]", long)
    lat_suffix = latitude[3]
    long_suffix = longitude[3]
    lat_float = []
    long_float = []
    try:
        for index in range(3):
            lat_float.append(float(latitude[index]))
            long_float.append(float(longitude[index]))
        if check_dms_bounds(lat_float, long_float):
            new_lat = lat_float[0] + (lat_float[1]/60) + (lat_float[2]/3600)
            new_long = long_float[0] + (long_float[1]/60) + (long_float[2]/3600)
            final_lat = float(convert_suffix("{value}{suffix}".format(value=new_lat, suffix=lat_suffix), suffixes))
            final_long = float(convert_suffix("{value}{suffix}".format(value=new_long, suffix=long_suffix), suffixes))
            return [final_lat, final_long]
        return None
    except ValueError:
        return None


def convert_suffix(string, suffix_list):
    for suffix in suffix_list:
        if suffix_list and string.endswith(suffix):
            if suffix == "S":
                string = "-" + string
            elif suffix == "W":
                string = "-" + string
            return string[:-len(suffix)]
    return string


def get_coordinates(msg):
    coordinates = []
    for index, word in enumerate(msg):
        if index == len(msg) - 1:
            break
        # Removes characters such as ( or [
        new_word = re.sub("[^0-9a-zA-Z.\-\u00b0'\"]", "", word)
        next_word = re.sub("[^0-9a-zA-Z.\-\u00b0'\"]", "", msg[index + 1])
        try:
            lat = float(convert_suffix(new_word, suffixes))
            long = float(convert_suffix(next_word, suffixes))
            if lat < -90 or lat > 90:
                pass
            elif lat < -180 or long > 180:
                pass
            else:
                coordinates.append([lat, long])
                print("Coordinates found: ({lat}, {long})".format(lat=lat, long=long))
        except ValueError:
            # Check if selection is a possible Decimal Degrees Minutes Seconds coordinate
            r_lat = re.compile("[0-9]+\u00b0[0-9]+'[0-9]+\.?[0-9]*\"[NS]")
            r_long = re.compile("[0-9]+\u00b0[0-9]+'[0-9]+\.?[0-9]*\"[EW]")
            if r_lat.match(new_word) is not None and r_long.match(next_word) is not None:
                coordinate = convert_ddms(new_word, next_word)
                if coordinate is not None:
                    coordinates.append(coordinate)
                    print("Coordinates found: ({lat}, {long})".format(lat=coordinate[0], long=coordinate[1]))
            pass
    return coordinates


