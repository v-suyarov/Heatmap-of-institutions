import math
from DataBuildings import *


class SocialBuilding(DataBuildings):
    serviced_buildings = None
    occupancy_ratio = None
    fact_people = None
    service_radius = None

    def __init__(self, data_buildings: DataBuildings, settings_target_build: SettingsTargetBuild, **kwargs):
        self.service_radius = settings_target_build.service_radius
        self.levels = data_buildings.levels
        self.people = data_buildings.people
        self.area = data_buildings.area
        self.type_build = data_buildings.type_build
        self.addr_housenumber = data_buildings.addr_housenumber
        self.addr_street = data_buildings.addr_street
        self.position = data_buildings.position
        self.geometry = data_buildings.geometry
        self.default_level = data_buildings.default_level
        self.meters_per_person = data_buildings.meters_per_person
        self.serviced_buildings = [building for key, items in kwargs.items() for building in items if
                                   self.position.distance(building.position) <= self.service_radius]
        self.fact_people = sum(
            [building.people for building in self.serviced_buildings]) * settings_target_build.matching_coeff

        if self.people == 0:
            self.occupancy_ratio = None
        else:
            self.occupancy_ratio = round(self.fact_people / self.people, 2)

    def print(self, end="\n"):
        print(f"Service_radius: {self.service_radius}", end=" ")
        print(f"Occupancy_ratio: {self.occupancy_ratio}", end=" ")
        print(f"Fact_people: {self.fact_people}", end=" ")
        super().print("\n")
        #print(f"Serviced_buildings: {self.serviced_buildings}", end=end)