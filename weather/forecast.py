from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

from aiohttp import ClientSession

from .exceptions import UnknownLocation


API_ENDPOINT = "https://wttr.in/{}?format=j1"
STATE_CODES = {
    "alabama": "al",
    "alaska": "ak",
    "american samoa": "as",
    "arizona": "az",
    "arkansas": "ar",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "district of columbia": "dc",
    "federated states of micronesia": "fm",
    "florida": "fl",
    "georgia": "ga",
    "guam": "gu",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "marshall islands": "mh",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "north carolina": "nc",
    "north dakota": "nd",
    "northern mariana islands": "mp",
    "ohio": "oh",
    "oklahoma": "ok",
    "oregon": "or",
    "palau": "pw",
    "pennsylvania": "pa",
    "puerto rico": "pr",
    "rhode island": "ri",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virgin islands": "vi",
    "virginia": "va",
    "washington": "wa",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy"
}

ALL_STATES = STATE_CODES.keys()
ALL_STATE_CODES = STATE_CODES.values()


class HourlyForecast:
    def __init__(self, data: dict, celsius: bool):
        self._data = data
        self.time = datetime.strptime(data["time"].zfill(4), "%H%M")  # time datetime
        self.weather_desc = data["weatherDesc"][0]["value"]  # description of weather conditions
        self.precip_chance = max(int(data["chanceofrain"]), int(data["chanceofsnow"]))  # chance of precipitation

        if celsius:
            # celsius hourly data
            self.temperature = int(data["tempC"])
            self.wind_speed = data["windspeedKmph"] + " kmph"
            self.wind_chill = int(data["WindChillC"])
            self.feels_like = int(data["FeelsLikeC"])
        else:
            # fahrenheit hourly data
            self.temperature = int(data["tempF"])
            self.wind_speed = data["windspeedMiles"] + " mph"
            self.wind_chill = int(data["WindChillF"])
            self.feels_like = int(data["FeelsLikeF"])


class DayForecast:
    def __init__(self, data: dict, celsius: bool):
        self._data = data
        self.date = datetime.strptime(data["date"], "%Y-%m-%d")  # formatted date

        # astronomy data
        astronomy = data["astronomy"][0]
        self.moon_phase = astronomy["moon_phase"]
        self.moonrise = astronomy["moonrise"]
        self.moonset = astronomy["moonset"]
        self.sunrise = astronomy["sunrise"]
        self.sunset = astronomy["sunset"]

        # temperature
        if celsius:
            # celsius
            self.avg_temp = int(data["avgtempC"])
            self.max_temp = int(data["maxtempC"])
            self.min_temp = int(data["mintempC"])
        else:
            # fahrenheit
            self.avg_temp = int(data["avgtempF"])
            self.max_temp = int(data["maxtempF"])
            self.min_temp = int(data["mintempF"])

        self.hourly = [HourlyForecast(d, celsius) for d in data["hourly"]]

    def print_temperature_summary(self):
        last_desc = None
        for hour in self.hourly:
            t = str((hour.time.hour - 1) % 12 + 1) + hour.time.strftime("%p")  # short time hour form with AM/PM
            if hour.weather_desc == last_desc:
                # don't reuse same description; use ellipsis to indicate continuation
                shown_desc = "..."
            else:
                shown_desc = last_desc = hour.weather_desc
            if hour.precip_chance:
                # add precipitation chance if applicable
                shown_desc += f" ({hour.precip_chance}%)"

            # print formatted hour line
            print(f" -- {t:>4} | {hour.temperature:>2}° | {shown_desc}")


class Forecast:
    def __init__(self, data: dict, celsius: bool):
        self._data = data
        self.days = [DayForecast(d, celsius) for d in data["weather"]]  # forecast for every day
        self.city = data["nearest_area"][0]["areaName"][0]["value"]  # name of city
        self.region = data["nearest_area"][0]["country"][0]["value"]  # name of region (country or state)
        if self.region == "United States of America":
            # if the location is in the US, region will reflect the state as well
            self.region = data["nearest_area"][0]["region"][0]["value"] + ", USA"

    @classmethod
    async def load(cls, city: str, region: Optional[str] = None, celsius: Optional[bool] = True) -> "Forecast":
        if region:
            # normalize region
            region = region.lower()
            if region in ALL_STATES:
                # if region is a state code, change it to a state name
                region = STATE_CODES[region]

        city = quote_plus(city)
        location = f"{city}+{region}" if region else city
        url = API_ENDPOINT.format(location).lower()  # build API url

        async with ClientSession(read_timeout=5) as conn:
            req = await conn.get(url)  # make request to API
            res = await req.text()
            if res.startswith("Unknown location"):
                # API returned unknown location
                raise UnknownLocation
            return cls(await req.json(), celsius)  # load data into class
