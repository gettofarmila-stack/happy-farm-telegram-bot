class WeatherEvent:
    def __init__(self, name, grow_multiplier=1.0, energy_bonus=0, death_chance=0):
        self.name = name 
        self.grow_multiplier = grow_multiplier
        self.energy_bonus = energy_bonus
        self.death_chance = death_chance

rain = WeatherEvent(name='Дождь', grow_multiplier=1.5, death_chance=0.01)
drought = WeatherEvent(name='Засуха', grow_multiplier=0.5, energy_bonus=1, death_chance=0.05)
sun = WeatherEvent(name='Солнечно', energy_bonus=3)
frost = WeatherEvent(name='Заморозки', grow_multiplier=0.5, death_chance=0.03)
storm = WeatherEvent(name='Гроза', death_chance=0.1)