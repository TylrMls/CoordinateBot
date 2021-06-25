import re

suffixes = ["N", "E", "S", "W"]


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
        new_word = re.sub("[^0-9a-zA-Z.-]", "", word)
        next_word = re.sub("[^0-9a-zA-Z.-]", "", msg[index + 1])
        try:
            lat = float(convert_suffix(new_word, suffixes))
            long = float(convert_suffix(next_word, suffixes))
            if not lat >= -90 and not lat <= 90:
                pass
            elif not long >=-180 and not long <= 180:
                pass
            else:
                coordinates.append([lat, long])
                print("Coordinates found: ({lat}, {long})".format(lat=lat, long=long))
        except ValueError:
            pass
    return coordinates


