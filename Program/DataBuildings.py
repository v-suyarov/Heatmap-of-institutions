from BuildingsClass import *
import math


class DataDataBuildingsError(Exception):
    pass


class AreaError(DataDataBuildingsError):
    pass


class DataBuildings:
    preferences = {}
    def __init__(self, geo_data_frame, key_build):
        levels_list = str(geo_data_frame["building:levels"])
        if levels_list == 'nan':
            self.levels = float('nan')
        else:
            levels_list = list(map(float, levels_list.split(';')))
            self.levels = sum(levels_list) / len(levels_list)
        self.type_build = geo_data_frame["building"]  # тип здания
        self.default_level = self.preferences[key_build][self.type_build].default_level
        if math.isnan(self.levels):
            self.levels = self.default_level
        else:
            self.levels = int(self.levels)
        self.geometry = geo_data_frame["geometry"]
        self.addr_housenumber = geo_data_frame["addr:housenumber"]
        self.addr_street = geo_data_frame["addr:street"]

        if self.geometry.area < 1:
            raise AreaError
        self.area = self.geometry.area * self.levels
        self.position = self.geometry.centroid
        self.meters_per_person = self.preferences[key_build][self.type_build].meters_per_person
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

    @classmethod
    def init(cls, preferences):
        cls.preferences = preferences
