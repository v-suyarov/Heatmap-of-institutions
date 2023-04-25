from BuildingsClass import *
import math
import pyproj

class DataDataBuildingsError(Exception):
    pass


class AreaError(DataDataBuildingsError):
    pass


class DataBuildings:
    preferences = {}
    __crs4326 = pyproj.CRS('EPSG:4326')
    __crs32638 = pyproj.CRS('EPSG:32638')
    __transformer = pyproj.Transformer.from_crs(__crs32638, __crs4326)
    def __init__(self, geo_data_frame, key_build):
        levels_list = str(geo_data_frame["building:levels"])
        self.type_build = geo_data_frame["building"]  # тип здания
        if levels_list == 'nan':
            self.levels = float('nan')
        else:
            try:
                levels_list = list(map(float, levels_list.split(';')))
                self.levels = sum(levels_list) / len(levels_list)
            except:
                self.levels = self.preferences[key_build][self.type_build].default_level

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

        self.polygon_epsg4326 = self.get_polygon_epsg4326(self.geometry)
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
    def get_polygon_epsg4326(cls, geometry_4326):
        boundary = geometry_4326.exterior
        coords = list(boundary.coords)
        new_points = cls.__transformer.transform(*zip(*coords))
        return new_points[::-1]
    @classmethod
    def init(cls, preferences):
        cls.preferences = preferences

    @classmethod
    def to_epsg4326(cls, point):
        new_point = cls.__transformer.transform(point[0], point[1])
        return new_point
