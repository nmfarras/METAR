import json
from metar_taf_parser.parser.parser import MetarParser, TAFParser
class WeatherParser:
    
    

        
    @staticmethod
    def metar_to_dict(metar):
        """
        Convert a Metar object to a dictionary.
        """
    
        
        return {
            "station": metar.station,
            "day": metar.day,
            "time": metar.time.strftime('%H:%M:%S'),
            "message": metar.message,
            "wind": {
                "speed": metar.wind.speed,
                "direction": metar.wind.direction,
                "gust": metar.wind.gust,
                "degrees": metar.wind.degrees,
                "unit": metar.wind.unit
            },
            "visibility": {
                "distance": metar.visibility.distance
            },
            "clouds": [
                {
                    "height": cloud.height,
                    "quantity": str(cloud.quantity),
                    "type": str(cloud.type)
                } for cloud in metar.clouds
            ],
            "weather_conditions": [
                {
                    "intensity": str(condition.intensity),
                    "descriptive": str(condition.descriptive),
                    "phenomenons": [str(p) for p in condition.phenomenons]
                } for condition in metar.weather_conditions
            ],
            "temperature": None if metar.temperature is None else metar.temperature,
            "dew_point": None if metar.dew_point is None else metar.dew_point,
            "altimeter": metar.altimeter,
            "nosig": metar.nosig
        }
    
    @staticmethod
    def taf_to_dict(taf):
        """
        Convert a TAF object to a dictionary.
        """
        def wind_to_dict(wind):
            if wind is None:
                return None
            return {
                "speed": wind.speed,
                "direction": wind.direction,
                "gust": wind.gust,
                "degrees": wind.degrees,
                "unit": wind.unit
            }
            
        def temperature_to_dict(temperatures):
            if temperatures is None:
                return None
            return {
                "temperature": temperatures.temperature if temperatures else None,
                "day": temperatures.day if temperatures else None,
                "hour": temperatures.hour if temperatures else None
            }
        
        return {
            "station": taf.station,
            "day": taf.day,
            "time": taf.time.strftime('%H:%M:%S'),
            "message": taf.message,
            "validity": {
                "start_day": taf.validity.start_day,
                "start_hour": taf.validity.start_hour,
                "end_day": taf.validity.end_day,
                "end_hour": taf.validity.end_hour
            },
            "wind": wind_to_dict(taf.wind),
            "visibility": {
                "distance": taf.visibility.distance
            },
            "clouds": [
                {
                    "height": cloud.height,
                    "quantity": str(cloud.quantity),
                    "type": str(cloud.type)
                } for cloud in taf.clouds
            ],
            "weather_conditions": [
                {
                    "intensity": str(condition.intensity),
                    "descriptive": str(condition.descriptive),
                    "phenomenons": [str(p) for p in condition.phenomenons]
                } for condition in taf.weather_conditions
            ],
            "trends": [
                {
                    "type": str(trend.type),
                    "validity": {
                        "start_day": trend.validity.start_day,
                        "start_hour": trend.validity.start_hour,
                        "end_day": trend.validity.end_day,
                        "end_hour": trend.validity.end_hour
                    },
                    "wind": wind_to_dict(trend.wind),
                    "visibility": {
                        "distance": trend.visibility.distance if trend.visibility else None
                    },
                    "clouds": [
                        {
                            "height": cloud.height,
                            "quantity": str(cloud.quantity),
                            "type": str(cloud.type)
                        } for cloud in trend.clouds
                    ],
                    "weather_conditions": [
                        {
                            "intensity": str(condition.intensity),
                            "descriptive": str(condition.descriptive),
                            "phenomenons": [str(p) for p in condition.phenomenons]
                        } for condition in trend.weather_conditions
                    ]
                } for trend in taf.trends
            ],
            "flags": list(taf.flags),
            "max_temperature": temperature_to_dict(taf.max_temperature),
            "min_temperature": temperature_to_dict(taf.min_temperature)
        }