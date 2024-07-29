# import requests
# from metar_taf_parser.parser.parser import TAFParser
# from metar_taf_parser.commons.i18n import _

# def fetch_metar_taf_data(icao_code):
    # """
    # Fetch METAR and TAF data from aviationweather.gov for a given ICAO code.
    # """
    # url = f'https://aviationweather.gov/cgi-bin/data/metar.php?ids={icao_code}&hours=0&sep=true&taf=true'
    # response = requests.get(url)
    # if response.status_code == 200:
        # return response.text
    # else:
        # raise Exception(f"Failed to fetch data: {response.status_code}")

# def parse_metar_taf(raw_data):
    # """
    # Parse raw METAR and TAF data into separate METAR and TAF strings.
    # """
    # try:
        # raw_metar, raw_taf = raw_data.split('\n\n')[:2]
    # except ValueError:
        # raise ValueError("The raw data does not contain the expected METAR and TAF sections.")
    
    # return raw_metar, raw_taf

# def format_wind(wind):
    # """
    # Format the wind data into a readable string.
    # """
    # if not wind:
        # return "Not specified"
    
    # direction = wind.direction if wind.direction != 'VRB' else 'Variable'
    # degrees = f"{wind.degrees}°" if wind.direction != 'VRB' else ""
    # return f"Speed: {wind.speed} {wind.unit} | Direction: {direction} | {degrees}"
    
# def format_gust(wind):
    # """
    # Format the gust wind data into a readable string.
    # """
    # if not wind:
        # return ""
        
    # gust_knots = wind.gust
    # gust_unit = wind.unit

    # # Add a condition to check if gust exceeds 30 knots
    # return f"Gust: {gust_knots} {gust_unit}\n" if gust_knots else ""

# def format_visibility(visibility):
    # """
    # Format the visibility data into a readable string.
    # """
    # return f"{visibility.distance} meters" if visibility else "Not specified"

# def format_clouds(clouds):
    # """
    # Format cloud data into a readable string.
    # """
    # if not clouds:
        # return "No clouds"
    
    # cloud_descriptions = []
    # for cloud in clouds:
        # cloud_quantity = cloud.quantity.__repr__() if cloud.quantity else ""
        # cloud_type = cloud.type.__repr__() if cloud.type else "layer"
        # cloud_height = f"at {cloud.height}ft" if cloud.height else ""
        # #cloud_desc = 
        # cloud_descriptions.append(f"{cloud_quantity} {cloud_type} {cloud_height}")
    
    # return ", ".join(filter(None, cloud_descriptions))

# def format_weather_conditions(conditions):
    # """
    # Format weather conditions into a readable string.
    # """
    # if not conditions:
        # return "No significant weather"
    
    # weather_conditions = []
    # for condition in conditions:
        # intens = str(condition.intensity.__repr__()) if condition.intensity else ""
        # desc = str(condition.descriptive.__repr__()) if condition.descriptive else ""
        # phenomenons = [str(phenomenon.__repr__()) for phenomenon in condition.phenomenons]
        
        # weather_condition = " ".join(filter(None, [intens, desc] + phenomenons))
        # weather_conditions.append(weather_condition)
    
    # return ", ".join(weather_conditions) if weather_conditions else "No significant weather"

# def format_trend(trend):
    # """
    # Format the trend information into a readable string.
    # """
    # start_day = trend.validity.start_day
    # start_hour = trend.validity.start_hour
    # end_day = trend.validity.end_day
    # end_hour = trend.validity.end_hour

    # wind_info = format_wind(trend.wind)
    # gust_info = format_gust(trend.wind)
    # visibility_info = format_visibility(trend.visibility)
    # weather_conditions = format_weather_conditions(trend.weather_conditions)
    
    # return (
        # f"Type of trend: {str(trend.type.__repr__())}\n"
        # f"Validity: From day {start_day} at {start_hour:02d} to day {end_day} at {end_hour:02d}\n"
        # f"Wind: {wind_info}\n"
        # f"{gust_info}"
        # f"Visibility: {visibility_info}\n"
        # f"Clouds: {format_clouds(trend.clouds)}\n"
        # f"Weather Conditions: {weather_conditions}"
    # )

# def print_taf_report(taf_report, taf):
    # """
    # Print formatted TAF report details.
    # """
    # # Header
    # print(f"TAF message:\n{taf_report}\n")
    
    # # Delivery and validity
    # print(f"TAF delivered for the day {taf.day} of the month at {taf.time}\n")
    # print(f"TAF valid from the day {taf.validity.start_day} at {taf.validity.start_hour} to day {taf.validity.end_day} at {taf.validity.end_hour}.\n")
    
    # # Wind, visibility, and clouds
    # print(f"Wind: {format_wind(taf.wind)}")
    # if taf.wind.gust:
        # print(f"Gust: {taf.wind.gust} {taf.wind.unit}")
    # print(f"Visibility: {format_visibility(taf.visibility)}")
    # print(f"Clouds: {format_clouds(taf.clouds)}\n")
    
    # # Trends
    # print("Trends:")
    # for trend in taf.trends:
        # print(format_trend(trend))
        # print()

# def main():
    # # icao_code = input("Enter ICAO code: ").strip().upper()
    # icao_code = "WIII"
    # raw_data = fetch_metar_taf_data(icao_code)
    
    # raw_data = """WIII 010400Z 22003KT 8000 -RA SCT020 27/27 Q1010

# TAF WIII 282300Z 2900/3006 20005KT 8000 FEW020 SCT021
  # BECMG 2904/2906 02010KT BECMG 2916/2918 16005KT 5000 VCTS +DZ SNHZ
  # BECMG 2923/3001 VRB02KT 8000 NSW"""
  
    # raw_data = """WIII 150500Z 1506/1612 17005KT 6000 SCT012

# TAF WIII 150500Z 2900/3006 20005KT 8000 FEW020 SCT021
  # TEMPO 1506/1509 3000 BR BKN006 PROB40
  # TEMPO 1506/1508 0400 BCFG BKN002 PROB40 
  # TEMPO 1512/1516 4000 -SHRA FEW030TCU BKN040 
  # BECMG 1520/1522 CAVOK 
  # TEMPO 1603/1608 3000 BR BKN006 PROB40 
  # TEMPO 1604/1607 0400 BCFG BKN002 TX17/1512Z TN07/1605Z"""
  
    # # raw_data = """WATT 011330Z AUTO 10012KT 9999 NCD 29/26 Q1013

# # TAF WATT 010500Z 0106/0206 10012KT 9999 SCT018
    # # TEMPO 0107/0110 12015G25KT"""
    
    # raw_metar, raw_taf = parse_metar_taf(raw_data)
    
    # # Initialize TAF parser
    # taf_parser = TAFParser()
    # taf = taf_parser.parse(raw_taf)
    
    # print("METAR Data:")
    # print(raw_metar)
    # print("\nTAF Data:")
    # print(raw_taf)
    
    # print("\nFormatted TAF Report:")
    # print_taf_report(raw_taf, taf)

# if __name__ == "__main__":
    # main()

import json
from metar_taf_parser.parser.parser import MetarParser, TAFParser
from weather_parsers import WeatherParser

# def wind_to_dict(wind):
    # if wind is None:
        # return None
    # return {
        # "speed": wind.speed,
        # "direction": wind.direction,
        # "gust": wind.gust,
        # "degrees": wind.degrees,
        # "unit": wind.unit
    # }
        
# def temperature_to_dict(temperatures):
    # if temperatures is None:
        # return None
    # return {
        # "temperature": temperatures.temperature if temperatures else None,
        # "day": temperatures.day if temperatures else None,
        # "hour": temperatures.hour if temperatures else None
    # }
        
# def metar_to_dict(metar):
    # """
    # Convert a Metar object to a dictionary.
    # """
    
        
    # return {
        # "station": metar.station,
        # "day": metar.day,
        # "time": metar.time.strftime('%H:%M:%S'),
        # "message": metar.message,
        # "wind": {
            # "speed": metar.wind.speed,
            # "direction": metar.wind.direction,
            # "gust": metar.wind.gust,
            # "degrees": metar.wind.degrees,
            # "unit": metar.wind.unit
        # },
        # "visibility": {
            # "distance": metar.visibility.distance
        # },
        # "clouds": [
            # {
                # "height": cloud.height,
                # "quantity": str(cloud.quantity),
                # "type": str(cloud.type)
            # } for cloud in metar.clouds
        # ],
        # "weather_conditions": [
            # {
                # "intensity": str(condition.intensity),
                # "descriptive": str(condition.descriptive),
                # "phenomenons": [str(p) for p in condition.phenomenons]
            # } for condition in metar.weather_conditions
        # ],
        # "temperature": None if metar.temperature is None else metar.temperature,
        # "dew_point": None if metar.dew_point is None else metar.dew_point,
        # "altimeter": metar.altimeter,
        # "nosig": metar.nosig
    # }

# def taf_to_dict(taf):
    # """
    # Convert a TAF object to a dictionary.
    # """
        
    # return {
        # "station": taf.station,
        # "day": taf.day,
        # "time": taf.time.strftime('%H:%M:%S'),
        # "message": taf.message,
        # "validity": {
            # "start_day": taf.validity.start_day,
            # "start_hour": taf.validity.start_hour,
            # "end_day": taf.validity.end_day,
            # "end_hour": taf.validity.end_hour
        # },
        # "wind": wind_to_dict(taf.wind),
        # "visibility": {
            # "distance": taf.visibility.distance
        # },
        # "clouds": [
            # {
                # "height": cloud.height,
                # "quantity": str(cloud.quantity),
                # "type": str(cloud.type)
            # } for cloud in taf.clouds
        # ],
        # "weather_conditions": [
            # {
                # "intensity": str(condition.intensity),
                # "descriptive": str(condition.descriptive),
                # "phenomenons": [str(p) for p in condition.phenomenons]
            # } for condition in taf.weather_conditions
        # ],
        # "trends": [
            # {
                # "type": str(trend.type),
                # "validity": {
                    # "start_day": trend.validity.start_day,
                    # "start_hour": trend.validity.start_hour,
                    # "end_day": trend.validity.end_day,
                    # "end_hour": trend.validity.end_hour
                # },
                # "wind": wind_to_dict(trend.wind),
                # "visibility": {
                    # "distance": trend.visibility.distance if trend.visibility else None
                # },
                # "clouds": [
                    # {
                        # "height": cloud.height,
                        # "quantity": str(cloud.quantity),
                        # "type": str(cloud.type)
                    # } for cloud in trend.clouds
                # ],
                # "weather_conditions": [
                    # {
                        # "intensity": str(condition.intensity),
                        # "descriptive": str(condition.descriptive),
                        # "phenomenons": [str(p) for p in condition.phenomenons]
                    # } for condition in trend.weather_conditions
                # ]
            # } for trend in taf.trends
        # ],
        # "flags": list(taf.flags),
        # "max_temperature": temperature_to_dict(taf.max_temperature),
        # "min_temperature": temperature_to_dict(taf.min_temperature)
    # }

def main():
    raw_data = """WIII 150500Z 1506/1612 17005KT 6000 SCT012

TAF WIII 150500Z 2900/3006 20005KT 8000 FEW020 SCT021
  TEMPO 1506/1509 3000 BR BKN006 PROB40
  TEMPO 1506/1508 0400 BCFG BKN002 PROB40 
  TEMPO 1512/1516 4000 -SHRA FEW030TCU BKN040 
  BECMG 1520/1522 CAVOK 
  TEMPO 1603/1608 3000 BR BKN006 PROB40 
  TEMPO 1604/1607 0400 BCFG BKN002 TX17/1512Z TN07/1605Z"""
  
    # raw_data = """WIII 010400Z 22003KT 8000 -RA SCT020 27/27 Q1010

# TAF WIII 282300Z 2900/3006 20005KT 8000 FEW020 SCT021
  # BECMG 2904/2906 02010KT BECMG 2916/2918 16005KT 5000 VCTS +DZ SNHZ
  # BECMG 2923/3001 VRB02KT 8000 NSW"""
  
    raw_data = """WATT 011330Z AUTO 10012KT 9999 NCD 29/26 Q1013

TAF WATT 010500Z 0106/0206 10012KT 9999 SCT018
    TEMPO 0107/0110 12015G25KT"""

    raw_metar, raw_taf = raw_data.split('\n\n')[:2]

    metar = MetarParser().parse(raw_metar)
    taf = TAFParser().parse(raw_taf)
    
    #print(metar)
    #print('\n',taf)

    metar_dict = WeatherParser.metar_to_dict(metar)
    taf_dict = WeatherParser.taf_to_dict(taf)

    print("METAR Data (JSON):")
    print(json.dumps(metar_dict, indent=4))

    print("\nTAF Data (JSON):")
    print(json.dumps(taf_dict, indent=4))

if __name__ == "__main__":
    main()
