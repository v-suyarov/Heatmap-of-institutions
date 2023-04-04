import geopandas.geodataframe
import osmnx as ox
import geopandas as gpd
import pyclip
import re
import math
import shapely
import matplotlib.pyplot as plt
from collections import defaultdict
import webbrowser
from functools import reduce
from BuildingsClass import *
from DataBuildings import DataBuildings
from SocialBuilding import SocialBuilding


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
        # Calculate green and blue values based on the input number
        green = int(num * 255)
        blue = int((1 - num) * 255)
        return "#{:02x}{:02x}{:02x}".format(0, green, blue)
    else:
        # Calculate red and green values based on the input number
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


settings_build = {"target": {"school": School(),
                             "kindergarten": Kindergarten(),
                             "hospital": Hospital(),
                             "stadium": Stadium(),
                             },
                  "produce": {"building": Building(),
                              "apartments": Apartments(),
                              "house": House(),
                              "detached": Detached(),
                              "residential": Residential()
                              }
                  }

# n and s = lat, e and w = log

plt.show()
# получение координат выборки
webbrowser.open(
    'http://prochitecture.com/blender-osm/extent/?blender_version=2.76&addon=blender-osm&addon_version=2.3.3', new=0)
pyclip.copy('')
while not re.fullmatch("\d+\.\d+,\d+\.\d+,\d+\.\d+,\d+\.\d+", pyclip.paste().decode("utf-8")):
    pass
else:
    west, north, east, south, = list(map(float, str(pyclip.paste())[2:-1].split(',')))


print("Получить граф дорожной сети и все здания в заданном боксе")

geometries = ox.geometries_from_bbox(north, south, east, west, tags={'building': True})

print("Отфильтровать полученные геометрии, чтобы получить только здания")

buildings = geometries[geometries['building'].notnull()]

# перевод чего-то там, чтобы площадь зданий посчиталсь в м квадратных, узнать текущее что то там - print(buildings.crs)
buildings = buildings.to_crs(epsg=32638)

print("Получение данных о зданиях")

# Создать словарь, где ключ - тип здания, а значение - список зданий данного типа
building_dict = defaultdict(list)
for _, row in buildings.iterrows():
    building_type = row['building']
    building_dict[building_type].append(row)

print("Словарь зданий, из которых будем учитывать людей")

residential_buildings = {}
for key in filter(lambda tag: tag in settings_build["produce"].keys(), building_dict.keys()):
    single_type = []
    for item in building_dict[key]:
        single_type.append(DataBuildings(item, settings_build["produce"][key]))
    residential_buildings[key] = single_type

# for key, items in residential_buildings.items():
#     for item in items:
#         item.print()

print("Словарь зданий, для которых будем высчитывать индекс и отрисовывать")

target_buildings = {}
for key in filter(lambda tag: tag in settings_build["target"].keys(), building_dict.keys()):
    single_type = []
    for item in building_dict[key]:
        single_type.append(
            SocialBuilding(DataBuildings(item, settings_build["target"][key]), settings_build['target'][key],
                           **residential_buildings))
    target_buildings[key] = single_type

for key, items in target_buildings.items():
    for item in items:
        item.print()

print("Отрисовка данных")

target_view = [[key, item.occupancy_ratio, item.geometry] for key, items in target_buildings.items() for item in items if type(item.geometry) == shapely.Polygon]
residential_polygons = [item.geometry for key, items in residential_buildings.items() for item in items if type(item.geometry) == shapely.Polygon]
# Создайте рисунок и ось
fig, ax = plt.subplots()

print("Отрисовка геометрий таргетных зданий")

colors = {0: ""}
# Переберите каждый полигон и добавьте его на ось
for key, occupancy_ratio, geometry in target_view:
    x, y = geometry.exterior.xy
    a = num_to_color(0.7)
    ax.fill(x, y, fc=num_to_color(occupancy_ratio), ec='none')

print("Отрисовка геометрий зданий продуцентов")

for poly in residential_polygons:
    x, y = poly.exterior.xy
    # Рисуем контуры полигонов синим цветом
    ax.fill(x, y, alpha=1, fc='#4c1852', ec='none')

show_color_bar()
# Отображение графика
plt.show()
#алгоритм для решения проблемы детских садов которые находятся рядом
#создать словарь, ключ - тип таргета, значение - спискок зданий с количеством людей таргетного типа
#заполнять таргетные здания последовательно и удалять людей из зданий по мере вмещения их в таргетное здание, если дом опустеет то удалить дом
#список общи для всех, поэтому опусташенный дом уже не засчитается в других таргетах, так как его не бу дет в списке
#после заполнения всех таргетов, могут остаться дома с людьми, в таком случаее происходит дозаполнение таргетов, как это делать - нужно продумать
#в итоге поличи результат в котором человек А может одновременно быть клиентом только одного детского сада