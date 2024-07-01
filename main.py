import requests
import re
from datetime import datetime

def fetch_metar_taf_data(icao_code):
    url = f'https://aviationweather.gov/cgi-bin/data/metar.php?ids={icao_code}&hours=0&sep=true&taf=true'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def get_date_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    elif day % 10 == 1:
        return 'st'
    elif day % 10 == 2:
        return 'nd'
    elif day % 10 == 3:
        return 'rd'
    else:
        return 'th'

def parse_cloud_condition(cloud_code):
    cloud_map = {
        "FEW": "few clouds",
        "SCT": "scattered clouds",
        "BKN": "broken clouds",
        "OVC": "overcast",
        "CLR": "clear skies",
        "SKC": "sky clear",
        "NCD": "no significant cloud detected",
        "NSC": "no significant cloud"
    }
    altitude = int(cloud_code[3:6]) * 100
    cloud_type = cloud_code[:3]
    if 'CB' in cloud_code:
        return f"{cloud_map.get(cloud_type, cloud_type)} with cumulonimbus at {altitude} feet AGL"
    elif 'TCU' in cloud_code:
        return f"{cloud_map.get(cloud_type, cloud_type)} with towering cumulus at {altitude} feet AGL"
    else:
        return f"{cloud_map.get(cloud_type, cloud_type)} at {altitude} feet AGL"

def parse_metar(raw_metar):
    metar_pattern = re.compile(
        r'(?P<station>\w{4})\s'
        r'(?P<datetime>\d{6}Z)\s'
        r'(AUTO\s)?'
        r'(?P<wind>(\d{3}\d{2}(G\d{2})?KT|VRB\d{2}KT|00000KT|\d{3}\d{3}(G\d{2})?KT))\s'
        r'((?P<variable_wind>\d{3}V\d{3})\s)?'
        r'(?P<visibility>\d{4})\s'
        r'(?P<weather>(([-+]?)(\w{2})|([-+]?)(\w{4})))?\s*'
        r'(?P<clouds>(CLR|SKC|NCD|NSC|FEW\d{3}(CB|TCU)?|SCT\d{3}(CB|TCU)?|BKN\d{3}(CB|TCU)?|OVC\d{3}(CB|TCU)?)\s*)*'
        r'(?P<temperature>\d{2}/\d{2})\s'
        r'(?P<pressure>Q\d{4})\s*'
        r'(?P<remarks>.*)'
    )
    match = metar_pattern.match(raw_metar)
    
    # print (raw_metar, match)
    if match:
        groups = match.groupdict()
        wind = groups['wind']
        
        if wind.startswith('VRB'):
            wind_info = f"Variable at {int(wind[3:5])} knots"
        elif wind == '00000KT':
            wind_info = "Calm wind"
        else:
            if len(wind)<8:
                wind_info = f"From {wind[:3]}° at {int(wind[3:5])} knots"
                # print(wind_info)
            else:
                wind_info = f"From {wind[:3]}° at {int(wind[3:6])} knots"
            if 'G' in wind:
                gust_speed = int(wind[wind.index('G')+1:wind.index('KT')])
                wind_info += f", gusting to {gust_speed} knots"
        
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().strftime('%B')
        
        day = int(groups['datetime'][:2])
        date_suffix = get_date_suffix(day)
        
        cloud_layers = groups['clouds'].split()
        clouds_info = ', '.join([parse_cloud_condition(cloud) for cloud in cloud_layers])
        
        # print(clouds_info)
        
        # print(groups['pressure'][1:])
        
        weather_map = {
            "BC": "Patches",
            "BL": "Blowing",
            "BR": "Mist",
            "DR": "Low drifting",
            "DS": "Duststorm",
            "DU": "Dust",
            "DZ": "Drizzle",
            "FC": "Funnel cloud or tornado",
            "FG": "Fog",
            "FU": "Smoke",
            "FZ": "Freezing",
            "GR": "Hail",
            "GS": "Small hail or snow pellets",
            "HZ": "Haze",
            "IC": "Ice crystals",
            "MI": "Shallow",
            "PL": "Ice pellets",
            "PO": "Dust or sand whirls",
            "PY": "Spray",
            "RA": "Rain",
            "SA": "Sand",
            "SG": "Snow grains",
            "SH": "Showers",
            "SN": "Snow",
            "SQ": "Squalls",
            "SS": "Sandstorm",
            "TS": "Thunderstorm",
            "UP": "Unknown precipitation",
            "VA": "Volcanic ash",
            "VC": "Vicinity",
        }
        
        weather = groups['weather']
        
        # print(weather)
        
        pattern = "|".join(sorted(weather_map.keys(), key=len, reverse=True))
        single_regex = re.compile(rf"\b([+-]?)({pattern})\b")
        
        combo_regex = re.compile(rf"\b([+-]?)((?:{'|'.join(weather_map.keys())}){{2,}})\b")
        
        try:
            single_weather = single_regex.search(weather)
            
            combo_weather = combo_regex.search(weather)
            
            if single_weather:
                single_weather = single_regex.search(weather)
                start, end = single_weather.span()
                
                intensity, code = weather[:start],single_weather.group()
                intensity_desc = "Light " if intensity == "-" else "Heavy " if intensity == "+" else ""
                
                weather_desc = f"{intensity_desc}{weather_map[code]}"
            elif combo_weather:
                combo_weather = combo_regex.search(weather)
                start, end = combo_weather.span()

                print(start, end)

                intensity, code = weather[:start],combo_weather.group()
            
            
                print(intensity)
            
                parts = [code[i:i+2] for i in range(0, len(code), 2)]
                descriptions = " with ".join(weather_map[part] for part in parts)
                intensity_desc = "Light " if intensity == "-" else "Heavy " if intensity == "+" else ""
            
                print(groups['weather'])
                print(len(groups['weather']))
        
        except Exception as e:
            # print(f"Error parsing METAR data: {e}")
            pass
        weather_info = weather_desc if groups['weather'] and len(groups['weather'])<4 else f"{intensity_desc}{descriptions}" if groups['weather'] and len(groups['weather'])>3 else 'No significant weather'
        
        
        result = {
            'Location': groups['station'],
            'Time': f"{groups['datetime'][2:4]}:{groups['datetime'][4:6]} UTC {day}{date_suffix} of {current_month} {current_year}",
            'Wind': wind_info,
            'Visibility': f"{int(groups['visibility'])} meters (10+ km)" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Weather': weather_info,
            'Clouds': clouds_info,
            'Temperature': f"{groups['temperature'].split('/')[0]}.0°C",
            'Dewpoint': f"{groups['temperature'].split('/')[1]}.0°C",
            'Pressure': f"{groups['pressure'][1:]} mbar",
            'Remarks': parse_remarks(groups.get('remarks', 'NOSIG'))
        }
        if groups['variable_wind']:
            result['Variable Wind'] = f"Between {groups['variable_wind'][:3]}° and {groups['variable_wind'][4:]}°"
            # print(result['Variable Wind'])
        return result
    else:
        raise Exception("Failed to parse METAR data")

def parse_remarks(remarks):
    remark_codes = {
        "NOSIG": "No significant changes expected",
        "TEMPO": "Temporary changes expected",
        "BECMG": "Becoming",
        "NSW": "No significant weather",
        "RMK": "Remark",
        "FM": "From",
        "TL": "Until",
        "AT": "At",
        "RA": "Rain",
        "TSRA": "Thunderstorms with Rain",
        "SN": "Snow",
        "DZ": "Drizzle",
        "GR": "Hail",
        "BR": "Mist",
        "FG": "Fog",
        "HZ": "Haze",
        "SQ": "Squall"
    }
    parsed_remarks = []
    for remark in remarks.split():
        if remark in remark_codes:
            parsed_remarks.append(remark_codes[remark])
        elif re.match(r'^\d{4}$', remark):
            parsed_remarks.append(f"at {remark[:2]}:{remark[2:]} UTC")
        else:
            parsed_remarks.append(remark)
    return " ".join(parsed_remarks)

def parse_taf(raw_taf):
    taf_lines = raw_taf.split('\n')
    taf_pattern = re.compile(
        r'TAF\s(?P<station>\w{4})\s'
        r'(?P<datetime>\d{6}Z)\s'
        r'(?P<validity>\d{4}/\d{4})\s'
        r'(?P<wind>\d{5}KT)\s'
        r'(?P<visibility>\d{4})\s'
        r'(?P<clouds>FEW\d{3}|SCT\d{3}|BKN\d{3}|OVC\d{3})'
    )
    becmg_pattern = re.compile(
        r'BECMG\s(?P<change_time>\d{4}/\d{4})\s*'
        r'(?P<change_wind>\d{5}KT)?\s*'
        r'(?P<change_visibility>\d{4})?\s*'
        r'(?P<change_clouds>FEW\d{3}|SCT\d{3}|BKN\d{3}|OVC\d{3})?\s*'
        r'(?P<change_weather>NSW)?'
    )
    tempo_pattern = re.compile(
        r'TEMPO\s(?P<tempo_time>\d{4}/\d{4})\s*'
        r'(?P<tempo_wind>\d{5}KT)?\s*'
        r'(?P<tempo_visibility>\d{4})?\s*'
        r'(?P<tempo_weather>([-+]?)(\w{2}))?\s*'
        r'(?P<tempo_clouds>FEW\d{3}|SCT\d{3}|BKN\d{3}|OVC\d{3})?'
    )
    
    current_year = datetime.utcnow().year
    current_month = datetime.utcnow().strftime('%B')
    
    match = taf_pattern.match(taf_lines[0])
    if match:
        groups = match.groupdict()
        wind = groups['wind']
        taf_info = {
            'Location': groups['station'],
            'Issue Time': f"{groups['datetime'][:2]}{get_date_suffix(int(groups['datetime'][:2]))} of {current_month} {current_year} at {groups['datetime'][2:4]}:{groups['datetime'][4:6]} UTC",
            'Forecast Validity': f"From {groups['validity'][:2]}{get_date_suffix(int(groups['validity'][:2]))} at {groups['validity'][2:4]}00 UTC to {groups['validity'][5:7]}{get_date_suffix(int(groups['validity'][5:7]))} at {groups['validity'][7:]}00 UTC" if int(groups['validity'][7:]) < 24 else f"From {groups['validity'][:2]}{get_date_suffix(int(groups['validity'][:2]))} at {groups['validity'][2:4]}00 UTC to {int(groups['validity'][5:7])+1}{get_date_suffix(int(groups['validity'][5:7])+1)} at 0000 UTC",
            'Wind': f"From {int(wind[:3])}° at {int(wind[3:5])} knots",
            'Visibility': f"{int(groups['visibility'])} meters (10+ km)" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Clouds': parse_cloud_condition(groups['clouds']),
            'Becoming': []
        }
        changes = []
        for line in taf_lines[1:]:
            change_match = becmg_pattern.match(line) or tempo_pattern.match(line)
            if change_match:
                change_groups = change_match.groupdict()
                change = {
                    'Timeframe': f"{change_groups['change_time'][:2]}{get_date_suffix(int(change_groups['change_time'][:2]))} to {change_groups['change_time'][5:7]}{get_date_suffix(int(change_groups['change_time'][5:7]))}" if change_groups['change_time'] else f"{change_groups['tempo_time'][:2]}{get_date_suffix(int(change_groups['tempo_time'][:2]))} to {change_groups['tempo_time'][5:7]}{get_date_suffix(int(change_groups['tempo_time'][5:7]))}",
                    'Wind': f"From {change_groups['change_wind'][:3]}° at {int(change_groups['change_wind'][3:5])} knots" if change_groups['change_wind'] else f"From {change_groups['tempo_wind'][:3]}° at {int(change_groups['tempo_wind'][3:5])} knots" if change_groups['tempo_wind'] else None,
                    'Visibility': f"{int(change_groups['change_visibility'])} meters (10+ km)" if change_groups['change_visibility'] == '9999' else f"{int(change_groups['change_visibility'])} meters" if change_groups['change_visibility'] else f"{int(change_groups['tempo_visibility'])} meters (10+ km)" if change_groups['tempo_visibility'] == '9999' else f"{int(change_groups['tempo_visibility'])} meters" if change_groups['tempo_visibility'] else None,
                    'Clouds': parse_cloud_condition(change_groups['change_clouds']) if change_groups['change_clouds'] else parse_cloud_condition(change_groups['tempo_clouds']) if change_groups['tempo_clouds'] else None,
                    'Weather': weather_map.get(change_groups['change_weather'], change_groups['change_weather']) if change_groups['change_weather'] else weather_map.get(change_groups['tempo_weather'], change_groups['tempo_weather']) if change_groups['tempo_weather'] else None
                }
                changes.append(change)
        taf_info['Becoming'] = changes
        return taf_info
    else:
        raise Exception("Failed to parse TAF data")

def generate_report(metar_info, taf_info):
    metar_report = f"""
METAR Report for {metar_info['Location']}:
-----------------------------------------
Time: {metar_info['Time']}
Wind: {metar_info['Wind']}
Visibility: {metar_info['Visibility']}
Weather: {metar_info['Weather']}
Clouds: {metar_info['Clouds']}
Temperature: {metar_info['Temperature']}
Dewpoint: {metar_info['Dewpoint']}
Pressure: {metar_info['Pressure']}
Remarks: {metar_info['Remarks']}
"""
    print(metar_report)

    if taf_info:
        taf_report = f"""
TAF Report for {taf_info['Location']}:
-------------------------------------
Issue Time: {taf_info['Issue Time']}
Forecast Validity: {taf_info['Forecast Validity']}
Wind: {taf_info['Wind']}
Visibility: {taf_info['Visibility']}
Clouds: {taf_info['Clouds']}
"""
        if 'Becoming' in taf_info and taf_info['Becoming']:
            taf_report += "Becoming:\n"
            for change in taf_info['Becoming']:
                taf_report += f"  - Timeframe: {change['Timeframe']}\n"
                if change['Wind']:
                    taf_report += f"    - Wind: {change['Wind']}\n"
                if change['Visibility']:
                    taf_report += f"    - Visibility: {change['Visibility']}\n"
                if change['Clouds']:
                    taf_report += f"    - Clouds: {change['Clouds']}\n"
                if change['Weather']:
                    taf_report += f"    - Weather: {change['Weather']}\n"
        print(taf_report)

def main():
    icao_code = input("Enter ICAO code: ").strip().upper()
    raw_data = fetch_metar_taf_data(icao_code)
    
    # raw_data = """WALL 010400Z 22003KT 8000 -RA SCT020 27/27 Q1010

# TAF WALL 302300Z 0100/0206 27005KT 9999 FEW020
  # TEMPO 0102/0106 3500 TSRA SCT017CB"""
  
    # raw_data = """WATT 220530Z 30008KT 240V330 9999 BKN017 33/25 Q1011 NOSIG

# TAF WATT 220500Z 2206/2306 08016KT 9999 FEW018
    # BECMG 2210/2212 10006KT"""
    
    ### Still not working per 2024-07-01 (either metar and taf or taf only)
    # raw_data = """WATT 011330Z AUTO 10012KT 9999 NCD 29/26 Q1013

# TAF WATT 010500Z 0106/0206 10012KT 9999 SCT018
    # TEMPO 0107/0110 12015G25KT"""
    
    # raw_data = """WALL 011330Z 27004KT 9000 SCT020 27/26 Q1010 NOSIG

# TAF COR WALL 011100Z 0112/0218 22005KT 9000 SCT020
    # TEMPO 0119/0123 4000 TSRA FEW018CB"""
    
    print(raw_data)
    
    raw_metar, raw_taf = raw_data.split('\n\n')[:2]
    
    try:
        metar_info = parse_metar(raw_metar)
    except Exception as e:
        # print(f"Error parsing METAR data: {e}")
        return

    try:
        taf_info = parse_taf(raw_taf)
    except Exception as e:
        # print(f"Error parsing TAF data: {e}")
        taf_info = None

    generate_report(metar_info, taf_info)

if __name__ == "__main__":
    main()
