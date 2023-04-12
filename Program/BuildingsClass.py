
class SettingsBuild:
    default_level = 2
    meters_per_person = 20


class SettingsTargetBuild(SettingsBuild):
    def __init__(self):
        self.default_level = 3
        self.meters_per_person = 5
        self.matching_coeff = 0.5
        self.service_radius = 1000


class School(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.2
        self.service_radius = 1000
        self.meters_per_person = 3
        self.default_level = 3


class Kindergarten(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.1
        self.service_radius = 500
        self.meters_per_person = 3
        self.default_level = 3


class Hospital(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.05
        self.service_radius = 6000
        self.meters_per_person = 6
        self.default_level = 6


class Stadium(SettingsTargetBuild):
    def __init__(self):
        self.matching_coeff = 0.05
        self.service_radius = 5000
        self.meters_per_person = 3
        self.default_level = 1


class Building(SettingsBuild):
    def __init__(self):
        self.default_level = 2
        self.meters_per_person = 35


class Apartments(SettingsBuild):
    def __init__(self):
        self.default_level = 8
        self.meters_per_person = 30


class House(SettingsBuild):
    def __init__(self):
        self.default_level = 3
        self.meters_per_person = 40


class Detached(SettingsBuild):
    def __init__(self):
        self.default_level = 1
        self.meters_per_person = 35


class Residential(SettingsBuild):
    def __init__(self):
        self.default_level = 4
        self.meters_per_person = 35