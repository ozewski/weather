import asyncio

from weather import Forecast, UnknownLocation

DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


async def main():
    city_name = input("City >> ")  # grab city and state name
    state = input("Country or state >> ") or None
    print("Finding nearest available forecast... ")

    try:
        # attempt to load forecast
        forecast = await Forecast.load(city_name, state, celsius=False)
    except TimeoutError:
        # connection timed out
        return print("\nError: Could not connect to the weather server.")
    except UnknownLocation:
        # API returned "unknown location"
        return print("\nError: Unknown location. Double-check your spelling or try a nearby large city.")

    print(f"\n-----\n\nSHOWING WEATHER FOR: {forecast.city}, {forecast.region}")

    i = 0  # keep track of number of days exhausted
    for day in forecast.days:
        print("\n-----")
        weekday = day.date.strftime("%A").upper() if i > 0 else "TODAY"  # name of day
        print(f"\n{weekday} (high {day.max_temp}°, low {day.min_temp}°)\n")  # print temperature details
        day.print_temperature_summary()  # print out summary of hourly temperatures
        input("\n... (press ENTER)")  # let user move forward at their own pace
        i += 1


asyncio.run(main())
