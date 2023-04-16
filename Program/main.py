import osmnx as ox
import geopandas as gpd
import pyclip
import re
import shapely
import matplotlib.pyplot as plt
from collections import defaultdict
import webbrowser
from DataBuildings import *
from SocialBuilding import SocialBuilding
import time
import cProfile


def show_color_bar():
    colors = []
    for num in range(101):
        colors.append(num_to_color(num / 50))

    fig, ax = plt.subplots()

    for i in range(len(colors)):
        rect = plt.Rectangle((i, 0), 1, 1, color=colors[i])
        ax.add_patch(rect)

    plt.xlim([0, len(colors)])
    plt.ylim([0, 1])
    plt.axis('off')


def num_to_color(num):
    if num < 0 or num > 2:
        if num < 0:
            num = 0
        if num > 2:
            num = 2
    if num <= 1:
        green = int(num * 255)
        blue = int((1 - num) * 255)
        return "#{:02x}{:02x}{:02x}".format(0, green, blue)
    else:
        red = int((num - 1) * 255)
        green = int((2 - num) * 255)
        return "#{:02x}{:02x}{:02x}".format(red, green, 0)


def show_map(buildings):
    gdf_buildings = gpd.GeoDataFrame(buildings)
    # отображаем геометрии зданий на карте
    gdf_buildings.plot(color='red')
    # задаем границы карты
    offset = 0.001
    plt.xlim(west - offset, east + offset)
    plt.ylim(north - offset, south + offset)
    plt.show()


def set_preferences(settings):
    def get_choices(options, unique_option=''):
        choices = {}
        for i, option in enumerate(options, start=1):
            key = str(i)
            choices[key] = option
            print(f"{key} - {choices[key]}")
        if unique_option:
            print(f"0 - {unique_option}")

        return choices

    def input_is_correct(error_message, *args):
        while True:
            choice = input().split()
            if any(func(choice) for func in args):
                return choice

            print(error_message)

    preferences = settings.copy()
    print("Выберите режим:")
    print("1 - Быстрая настройка")
    print("2 - Расширенная настройка")
    while True:
        choice = input_is_correct("Введите 1 или 2",
                                  lambda choice: len(choice) == 1 and choice[0] in "12")
        if choice[0] == "1":
            print("В режиме быстрой настройки все расчеты будут произведены только для одного типа учреждений")
            print("Выберите тип учреждения")
            current_settings = "target"
            choices = get_choices(settings[current_settings])

            choice = input_is_correct("Выберите корректный тип",
                                      lambda choice: len(choice) == 1 and choice[0] in choices)
            preferences[current_settings] = {type_: settings[current_settings][type_] for key, type_ in
                                             choices.items() if choice[0] == "0" or key in choice}
        elif choice[0] == "2":
            options_settings = list(settings.keys())

            print("В режиме расширенной настройки можно оценить загруженность нескольких типов учреждений одновременно")
            print("Учтите, что если здание не обслуживается хотя бы одним из выбранных таргетов, "
                  "то оно будет помечено как 'вне обслуживания'")
            print("Укажите через пробел типы учреждений")
            current_settings = options_settings.pop(0)
            choices = get_choices(settings[current_settings], "выбрать все")

            choice = input_is_correct("Выберите корректный тип",
                                      lambda choice: all(choices.get(key, False) for key in choice),
                                      lambda choice: len(choice) == 1 and choice[0] == "0")
            preferences[current_settings] = {type_: settings[current_settings][type_] for key, type_ in
                                             choices.items() if choice[0] == "0" or key in choice}

            print("Укажите типы зданий, из которых будут учитываться люди для расчетов загруженности")
            print("Укажите через пробел типы зданий")
            current_settings = options_settings.pop(0)
            choices = get_choices(settings[current_settings], "выбрать все")
            choice = input_is_correct("Выберите корректный тип",
                                      lambda choice: all(choices.get(key, False) for key in choice),
                                      lambda choice: len(choice) == 1 and choice[0] == "0")
            preferences[current_settings] = {type_: settings[current_settings][type_] for key, type_ in
                                             choices.items() if choice[0] == "0" or key in choice}

            current_settings = options_settings.pop(0)
            print("Ограниченная зона - здания по краям карты могут помечаться, как 'вне обслуживания,",
                  "хотя возможно их обслуживают выбранные таргеты, просто они находятся за выбранной территорией.",
                  "Ограниченная зона устанавливает, "
                  "с какого растояния от края карты здание будет проверяться на 'вне обслуживания'",
                  "Укажите растояние в метрах, вещественное число, разделитель '.'",
                  f"Рекомендуемое растояние: {settings[current_settings]}",
                  sep="\n")

            choice = input_is_correct("Укажите растояние в метрах, вещественное число, разделитель '.'",
                                      lambda choice: len(choice) == 1 and str.isdigit(choice[0].replace(".", '', 1)))
            preferences[current_settings] = float(choice[0])

        print("Данные OSM не всегда содержат информацию о типе здания")
        print("Укажите, до какой сумарной площади, здания неопределнного типа будут помечаться как - 'частный дом'")
        print("Укажите площадь в метрах квадратных, вещественное число, разделитель '.'")
        print(f"Рекомендуемое значение: {settings['yes_to_produce_for_area_less']}")
        choice = input_is_correct("Укажите растояние в метрах, вещественное число, разделитель '.'",
                                  lambda choice: len(choice) == 1 and str.isdigit(choice[0].replace(".", '', 1)))
        preferences["yes_to_produce_for_area_less"] = float(choice[0])

        print("Вы хотите открыть новую вкладку для выбора территории?")
        print("1 - да")
        print("2 - нет")
        choice = input_is_correct("Введите 1 или 2",
                                  lambda choice: len(choice) == 1 and choice[0] in "12")
        preferences["create_new_tab"] = choice[0] == "1"

        try:
            if re.fullmatch("\d+\.\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+", pyclip.paste().decode("utf-8")):
                print("В буфере находятся коректные координаты, хотите их использовать ?")
                print("1 - да")
                print("2 - нет")
                choice = input_is_correct("Введите 1 или 2",
                                          lambda choice_: len(choice) == 1 and choice[0] in "12")
                if choice[0] == "1":
                    print("Использованы координаты из буфера")
                else:
                    pyclip.copy('')
                    print("Поместите координаты в буфер в системе EPSG:4326, в формате 'w s e n'")
            else:
                print("Поместите координаты в буфер в системе EPSG:4326, в формате 'w s e n'")
        except:
            print("Ошибка обработки буфера, буфер отчищен")
            print("Поместите координаты в буфер в системе EPSG:4326, в формате 'w s e n'")
            pyclip.copy('')

        return preferences


settings_program = {"target": {"school": School(),
                               "kindergarten": Kindergarten(),
                               "hospital": Hospital(),
                               "stadium": Stadium(),
                               },
                    "produce": {"apartments": Apartments(),
                                "house": House(),
                                "detached": Detached(),
                                "residential": Residential(),
                                "barracks": Barracks(),
                                "bungalow": Bungalow(),
                                "dormitory": Dormitory(),
                                "farm": Farm(),
                                "hotel": Hotel(),
                                "yes": Detached()
                                },
                    "restricted_zone": 0,
                    "create_new_tab": True,

                    "yes_to_produce_for_area_less": 350,
                    }

non_residential_building_tags = ["amenity", "shop", "historic", "tourism", "office", "leisure"]
preferences = set_preferences(settings_program)

if preferences["create_new_tab"]:
    # n and s = lat, e and w = log
    pyclip.copy('')
    # получение координат выборки
    webbrowser.open(
        'http://prochitecture.com/blender-osm/extent/?blender_version=2.76&addon=blender-osm&addon_version=2.3.3',
        new=0)

while not re.fullmatch("\d+\.\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+", pyclip.paste().decode("utf-8")):
    pass
else:
    west, north, east, south, = list(map(float, str(pyclip.paste())[2:-1].split(',')))
    coords = {"w": west,
              "n": north,
              "e": east,
              "s": south}

print("Получить граф дорожной сети и все здания в заданном боксе")

geometries = ox.geometries_from_bbox(north, south, east, west, tags={'building': True})

print("Отфильтровать полученные геометрии, чтобы получить только здания")

buildings = geometries[geometries['building'].notnull()]

# перевод ситемы координат, чтобы площадь зданий посчиталсь в м квадратных,
# узнать текущее что то там - print(buildings.crs)
buildings = buildings.to_crs(epsg=32638)

print("Получение данных о зданиях")

# Создать словарь, где ключ - тип здания, а значение - список зданий данного типа
building_dict = defaultdict(list)
for _, row in buildings.iterrows():
    if row["geometry"].geom_type == 'Polygon':
        building_type = row['building']
        building_dict[building_type].append(row)

print("Словарь зданий, из которых будем учитывать людей")

DataBuildings.init(preferences)
residential_buildings = {}
for key in filter(lambda tag: tag in preferences["produce"].keys(), building_dict.keys()):
    single_type = []
    for item in building_dict[key]:
        d_b = DataBuildings(item, key_build="produce")

        if d_b.type_build != "yes":
            single_type.append(d_b)
        elif d_b.geometry.area < preferences["yes_to_produce_for_area_less"]:
            single_type.append(d_b)

    residential_buildings[key] = single_type

# for key, items in residential_buildings.items():
#     for item in items:
#         item.print()

print("Словарь зданий, для которых будем высчитывать индекс и отрисовывать")

target_buildings = {}

start_time = time.time()
SocialBuilding.init(residential_buildings, coords, preferences)
end_time = time.time()
print(f"SocialBuilding.init() отработал за {end_time - start_time} сек")

start_time = time.time()
for key in filter(lambda tag: tag in preferences["target"].keys(), building_dict.keys()):
    single_type = []
    for item in building_dict[key]:
        target = SocialBuilding(item, key_build="target", **residential_buildings)
        single_type.append(target)

    target_buildings[key] = single_type
end_time = time.time()

print(f"Словарь зданий, для которых будем высчитывать индекс и отрисовывать,"
      f" расчитался за {end_time - start_time} сек")

# start_time = time.time()
cProfile.run('SocialBuilding.fill_buildings()')
# end_time = time.time()
# print(f"SocialBuilding.fill_buildings() отработал за {end_time - start_time} сек")


print("Отрисовка данных")

# Создайте рисунок и ось
fig, ax = plt.subplots()

total_people = 0
for key, builds in residential_buildings.items():
    total_people += sum(build.people for build in builds)

out_of_service_people = sum(build.people for build in SocialBuilding.out_of_service)

plt.title(f"Всего людей в выбранной области у выбранных типов продуцентов: {int(total_people)}\n"
          f"Всего людей в выбранных продуцентах, которые не обслуживаются таргетами: {int(out_of_service_people)}")

for _, row in buildings.iterrows():
    if row["geometry"].geom_type == 'Polygon':
        building_type = row['building']
        color = "#1a1c21"
        alpha = 0.3

        if building_type != "yes":
            color = "#04525c"

        x, y = row["geometry"].exterior.xy
        ax.fill(x, y, alpha=alpha, color=color, ec='none')

target_view = [[key, item.occupancy_ratio, item.geometry] for key, items in target_buildings.items()
               for item in items if type(item.geometry) == shapely.Polygon]
residential_polygons = [item.geometry for key, items in residential_buildings.items()
                        for item in items if type(item.geometry) == shapely.Polygon]

print("Отрисовка геометрий таргетных зданий")

for key, occupancy_ratio, geometry in target_view:
    if geometry.geom_type == 'Polygon':
        x, y = geometry.exterior.xy
        ax.fill(x, y, fc=num_to_color(occupancy_ratio), ec='none')

print("Отрисовка геометрий зданий продуцентов")

for poly in residential_polygons:
    if poly.geom_type == 'Polygon':
        x, y = poly.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='#4c1852', ec='none')

print("Отрисовка геометрий зданий продуцентов, которые не вошли в радиус обслуживания")

for poly in map(lambda d_b: d_b.geometry, SocialBuilding.out_of_service):
    if poly.geom_type == 'Polygon':
        x, y = poly.exterior.xy
        ax.fill(x, y, alpha=0.4, fc='#fa6b6b', ec='none')

print("Отрисовка геометрий зданий продуцентов, находятся в ограниченной зоне")

for poly in map(lambda d_b: d_b.geometry, SocialBuilding.building_in_restricted_zone):
    if poly.geom_type == 'Polygon':
        x, y = poly.exterior.xy
        ax.fill(x, y, alpha=1, fc='#ffbf00', ec='none')

plt.show()
