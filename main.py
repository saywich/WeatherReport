import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class WeatherData:
    city: str
    temperature_c: float
    country: str


def format_temp(temp: float) -> str:
    rounded = round(temp)
    sign = "+" if rounded > 0 else ""
    return f"{sign}{rounded} °C"


def load_cities_from_file(file_path: str) -> list[str]:
    cities = []
    
    with open(file_path, mode="r", encoding="utf-8") as file:
        for line in file:
            city_name = line.strip()
            if city_name:
                cities.append(city_name)

    return cities


def fetch_weather(city: str) -> WeatherData | None:
    encoded_city = urllib.parse.quote(city)
    url = f"https://wttr.in/{encoded_city}?format=j1"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "curl/7.68.0", "Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_content = response.read().decode("utf-8")
            data = json.loads(raw_content)


        current_temp = float(data["current_condition"][0]["temp_C"])
        country_name = data["nearest_area"][0]["country"][0]["value"]
        resolved_city = data["nearest_area"][0]["areaName"][0]["value"]

        return WeatherData(
            city=resolved_city,
            temperature_c=current_temp,
            country=country_name,
        )

    except (
        urllib.error.URLError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
    ) as e:
        print(f"Ошибка при получении данных для города '{city}': {e}")
        return None


def main():
    file_path = "cities.txt"

    all_cities = load_cities_from_file(file_path)

    unique_cities = list(dict.fromkeys(all_cities))

    weather_list: list[WeatherData] = []

    print("--- Данные по каждому городу ---")
    for city in unique_cities:
        weather = fetch_weather(city)
        if weather:
            weather_list.append(weather)
            temp_str = format_temp(weather.temperature_c)

            print(f"{weather.city}, {weather.country} {temp_str}")

        time.sleep(0.5)

    grouped_by_country = defaultdict(list)
    for item in weather_list:
        grouped_by_country[item.country].append(item.temperature_c)

    print("\n--- Статистика по странам ---")
    for country, temps in grouped_by_country.items():
        city_count = len(temps)
        avg_temp = sum(temps) / city_count
        min_temp = min(temps)
        max_temp = max(temps)

        cities_label = "city" if city_count == 1 else "cities"
        print(
            f"{country} — {city_count} {cities_label}, "
            f"avg: {format_temp(avg_temp)}, "
            f"min: {format_temp(min_temp)}, "
            f"max: {format_temp(max_temp)}"
        )


if __name__ == "__main__":
    main()