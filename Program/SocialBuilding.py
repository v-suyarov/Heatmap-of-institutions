from DataBuildings import *
import pyproj
from geopy import distance
import sys


class SocialBuilding(DataBuildings):
    residents_by_type = {}

    instances = {}
    coords = {}

    out_of_service = []
    building_in_restricted_zone = []

    def __init__(self, geo_data_frame, key_build, **kwargs):
        super().__init__(geo_data_frame, key_build)

        single_type_instances = self.instances.get(self.type_build, [])
        single_type_instances.append(self)
        self.instances[self.type_build] = single_type_instances
        self.service_radius = self.preferences["target"][self.type_build].service_radius
        self.fact_people = 0

        if self.people == 0:
            self.occupancy_ratio = None
        else:
            self.occupancy_ratio = round(self.fact_people / self.people, 2)

    def add_fact_people(self, add):
        self.fact_people += add
        if self.people == 0:
            self.occupancy_ratio = None
        else:
            self.occupancy_ratio = round(self.fact_people / self.people, 2)

    def print(self, end="\n"):
        print(f"Service_radius: {self.service_radius}", end=" ")
        print(f"Occupancy_ratio: {self.occupancy_ratio}", end=" ")
        print(f"Fact_people: {self.fact_people}", end=" ")
        super().print("\n")

    @classmethod
    def __init_residents_by_type(cls, residential_buildings, types):
        residentials = []
        for key, values in residential_buildings.items():
            residentials.extend(values)

        # для каждого типа таргетного здания уставливаем здания с жителями
        residents_by_type = {}
        for type_target in types:
            residents_by_type[type_target] = list(map(lambda data_build:
                                                      [data_build, int(data_build.people * cls.preferences["target"][
                                                          type_target].matching_coeff)],
                                                      residentials))

        cls.residents_by_type = residents_by_type

    @classmethod
    def init(cls, residential_buildings, coords, preferences):
        super().init(preferences)

        cls.__init_residents_by_type(residential_buildings, cls.preferences["target"].keys())
        w = coords["w"]
        n = coords["n"]
        e = coords["e"]
        s = coords["s"]
        coords = {}
        left_top = [w, n]
        right_bot = [e, s]

        crs4326 = pyproj.CRS('EPSG:4326')
        crs32638 = pyproj.CRS('EPSG:32638')
        transformer = pyproj.Transformer.from_crs(crs4326, crs32638)
        left_top = transformer.transform(left_top[1], left_top[0])
        right_bot = transformer.transform(right_bot[1], right_bot[0])
        coords["l_t"] = left_top
        coords["r_b"] = right_bot
        cls.coords = coords

    @classmethod
    def fill_buildings(cls):
        cls.residents_by_type = {key: items for key, items in cls.residents_by_type.items()
                                 if key in cls.instances.keys()}
        all_iteration = sum([len(items) for key, items in cls.residents_by_type.items()])
        i = 0
        for key, items in cls.residents_by_type.items():
            if len(items) > 0:

                item = items.pop(0)
                while item is not None:
                    i += 1
                    p = round((i / all_iteration)*100,2)
                    sys.stdout.write(f"\rLoading: {p}%")
                    sys.stdout.flush()
                    targets = [target for target in cls.instances[key]
                               if item[0].position.distance(target.position) <= target.service_radius]

                    if len(targets) > 0:
                        min_people = min(targets, key=lambda target: target.people).people
                        # будет содержать вложенные списки, 1 значение SocialBuildin, 2 значение коэфициент пропорции
                        # то необходимо, чтобы равномерно распределить жителей и здания по таргетам
                        if min_people < 1:
                            pass
                        targets = [[target, target.people / min_people] for target in targets]
                        sum_people = sum(list(map(lambda target: target[1], targets)))
                        unit_of_proportion = item[1] / sum_people
                        targets = [[target, int(coef * unit_of_proportion)] for target, coef in targets]
                        for target, selected_people in targets:
                            target.add_fact_people(selected_people)
                    elif cls.__included_in_restricted_zone(item[0]):
                        if item[0] not in cls.building_in_restricted_zone:
                            cls.building_in_restricted_zone.append(item[0])
                    else:
                        # print(f"Данный дом: {item[0].addr_street} {item[0].addr_housenumber}, не обслуживает не одно здание типа: {key}")
                        if item[0] not in cls.out_of_service:
                            cls.out_of_service.append(item[0])

                    if len(items) > 1:
                        item = items.pop(0)
                    else:
                        item = None
        sys.stdout.write(f"\rLoading: {100}%")
        sys.stdout.flush()
        print()
    @classmethod
    def __included_in_restricted_zone(cls, building):


        l_t = cls.coords["l_t"]
        r_b = cls.coords["r_b"]
        l = [l_t[0], building.position.y]
        r = [r_b[0], building.position.y]
        t = [building.position.x, l_t[1]]
        b = [building.position.x, r_b[1]]

        building_4326 = cls.to_epsg4326([building.position.x, building.position.y])
        res = False
        for point in (l, r, t, b):
            point_4326 = cls.to_epsg4326([point[0], point[1]])
            if distance.distance(building_4326, point_4326).m < cls.preferences["restricted_zone"]:
                res = True

        return res

    # def __identify_fact_people(self):
    #
    #     max_people = self.people
    #     total_people = 0
    #
    #     item = None
    #     i = 0
    #     if len(self.residents_by_type[self.type_build]) > 0:
    #         item = self.residents_by_type[self.type_build][0]
    #
    #     while total_people < max_people and item is not None:
    #         data_build = item[0]
    #         mod_people = item[1]
    #
    #         if self.position.distance(data_build.position) <= self.service_radius:
    #             if max_people - total_people > mod_people:
    #                 total_people += mod_people
    #                 item[1] = 0
    #             else:
    #                 add = max_people - total_people
    #                 total_people += add
    #                 item[1] -= add
    #
    #         if item[1] == 0:
    #             self.residents_by_type[self.type_build].remove(item)
    #         elif item[1] <= 0:
    #             raise TypeError("Ошибка")
    #         else:
    #             i += 1
    #
    #         if i < len(self.residents_by_type[self.type_build]):
    #             item = self.residents_by_type[self.type_build][i]
    #         else:
    #             item = None
    #
    #     return total_people
