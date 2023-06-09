
class SettingsBuild:
    default_level = 2
    meters_per_person = 20


class SettingsTargetBuild(SettingsBuild):
    def __init__(self):
        self.default_level = 3
        self.meters_per_person = 5
        self.matching_coeff = 0.5
        self.service_radius = 1000
        self.maximize_service_radius = 3000


class School(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.2
        self.service_radius = 1000
        self.meters_per_person = 3
        self.default_level = 3
        self.maximize_service_radius = 4000

class Kindergarten(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.10
        self.service_radius = 500
        self.meters_per_person = 3
        self.maximize_service_radius = 3000


class Hospital(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.05
        self.service_radius = 6000
        self.meters_per_person = 6
        self.default_level = 6
        self.maximize_service_radius = 10000

class Stadium(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.05
        self.service_radius = 5000
        self.meters_per_person = 3
        self.default_level = 1
        self.maximize_service_radius = 10000

class Apartments(SettingsBuild):
    def __init__(self):
        self.default_level = 8
        self.meters_per_person = 30


class House(SettingsBuild):
    def __init__(self):
        self.default_level = 2
        self.meters_per_person = 25


class Detached(SettingsBuild):
    def __init__(self):
        self.default_level = 1
        self.meters_per_person = 30


class Residential(SettingsBuild):
    def __init__(self):
        self.default_level = 4
        self.meters_per_person = 35


class Barracks(SettingsBuild):
    def __init__(self):
        self.default_level = 2
        self.meters_per_person = 10


class Bungalow(SettingsBuild):
    def __init__(self):
        self.default_level = 1
        self.meters_per_person = 25


class Dormitory(SettingsBuild):
    def __init__(self):
        self.default_level = 6
        self.meters_per_person = 15


class Farm(SettingsBuild):
    def __init__(self):
        self.default_level = 1
        self.meters_per_person = 35

class Hotel(SettingsBuild):
    def __init__(self):
        self.default_level = 5
        self.meters_per_person = 25

