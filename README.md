# Weather

A weather forecasting application. The user enters the name of a city and a country/state, and the program gives a visual hourly forecast of the weather for that city.

Currently available weather data includes daily high/low temperatures and hourly temperatures, weather descriptions, and chances of precipitation. Additional API data remains available but unused in the program.

This program is limited by its API ([wttr.in](https://github.com/chubin/wttr.in)). Only three days of forecasting data are available at a time. The program may not function properly closer to the end of the day as the service occasionally reaches a request limit. Weather data is relatively rough for rural areas and tends to be concentrated around urban centers.

To run, clone the repo and run `python3 main.py`. The `aiohttp` external library is required.