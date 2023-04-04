from BuildingsClass import *
import math

class DataBuildings:
    meters_per_person = None
    position = None
    area = None
    people = None

    levels = None
    geometry = None
    addr_housenumber = None
    addr_street = None
    type_build = None

    default_level = None

    def __init__(self, geo_data_frame, settings_build: SettingsBuild):
        levels_list = str(geo_data_frame["building:levels"])
        if levels_list == 'nan':
            self.levels = float('nan')
        else:
            levels_list = list(map(float, levels_list.split(';')))
            self.levels = sum(levels_list)/len(levels_list)

        self.default_level = settings_build.default_level
        if math.isnan(self.levels):
            self.levels = self.default_level
        else:
            self.levels = int(self.levels)
        self.geometry = geo_data_frame["geometry"]
        self.addr_housenumber = geo_data_frame["addr:housenumber"]
        self.addr_street = geo_data_frame["addr:street"]
        self.type_build = geo_data_frame["building"]  # тип здания
        self.area = self.geometry.area * self.levels
        self.position = self.geometry.centroid
        self.meters_per_person = settings_build.meters_per_person
        self.people = self.area / self.meters_per_person

    def print(self, end="\n"):
        print(f"Type: {self.type_build}", end=" ")
        print(f"Area: {self.area}", end=" ")
        print(f"People: {self.people}", end=" ")
        print(f"Levels: {self.levels}", end=" ")
        print(f"Meters_per_person: {self.meters_per_person}", end=" ")
        print(f"Addr_street: {self.addr_street}", end=" ")
        print(f"Addr_housenumber: {self.addr_housenumber}", end=" ")
        print(f"Position: {self.position}", end=" ")
        print(f"Polygon: {self.geometry}", end=end)