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
        
def parse_metar(raw_metar):
    metar_pattern = re.compile(
        r'(?P<station>\w{4})\s'
        r'(?P<datetime>\d{6}Z)\s'
        r'(AUTO\s)?'
        r'(?P<wind>(\d{3}\d{2}(G\d{2})?KT|VRB\d{2}KT|00000KT))\s'
        r'((?P<variable_wind>\d{3}V\d{3})\s)?'
        r'(?P<visibility>\d{4})\s'
        r'(?P<clouds>(FEW\d{3}|SCT\d{3}|BKN\d{3}|OVC\d{3}|NCD))\s'
        r'(?P<temperature>\d{2}/\d{2})\s'
        r'(?P<pressure>Q\d{4})\s*'
        r'(?P<remarks>.*)?'
    )
    match = metar_pattern.match(raw_metar)
    if match:
        groups = match.groupdict()
        wind = groups['wind']
        
        if wind.startswith('VRB'):
            wind_info = f"Variable at {int(wind[3:5])} knots"
        elif wind == '00000KT':
            wind_info = "Calm wind"
        else:
            wind_info = f"From {int(wind[:3])}° at {int(wind[3:5])} knots"
            if 'G' in wind:
                gust_speed = int(wind[wind.index('G')+1:wind.index('KT')])
                wind_info += f", gusting to {gust_speed} knots"
        
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().strftime('%B')
        
        day = int(groups['datetime'][:2])
        date_suffix = get_date_suffix(day)
        
        result = {
            'Location': groups['station'],
            'Time': f"{groups['datetime'][2:4]}:{groups['datetime'][4:6]} UTC {day}{date_suffix} of {current_month} {current_year}",
            'Wind': wind_info,
            'Visibility': f"10+ km" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Clouds': f"Few clouds at {int(groups['clouds'][3:])}00 feet AGL" if groups['clouds'].startswith('FEW') else groups['clouds'],
            'Temperature': f"{groups['temperature'].split('/')[0]}.0°C",
            'Dewpoint': f"{groups['temperature'].split('/')[1]}.0°C",
            'Pressure': f"{groups['pressure'][1:]} mbar",
            'Remarks': parse_remarks(groups.get('remarks', 'NOSIG'))
        }
        if groups['variable_wind']:
            result['Variable Wind'] = f"Between {groups['variable_wind'][:3]}° and {groups['variable_wind'][4:]}°"
        return result
    else:
        raise Exception("Failed to parse METAR data")

def parse_remarks(remarks):
    remark_codes = {
        "NOSIG": "No significant changes expected",
        "TEMPO": "Temporary changes expected",
        "BECMG": "Becoming",
        "NSW": "No significant weather",
        "RMK": "Remark"
    }
    parsed_remarks = []
    for remark in remarks.split():
        parsed_remarks.append(remark_codes.get(remark, remark))
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
            'Visibility': f"10+ km" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Clouds': f"Few clouds at {int(groups['clouds'][3:])}00 feet AGL" if groups['clouds'].startswith('FEW') else groups['clouds']
        }
        becmg_matches = []
        for line in taf_lines[1:]:
            second_line_match = becmg_pattern.match(line.strip())
            if second_line_match:
                second_groups = second_line_match.groupdict()
                change_info = {
                    'Timeframe': f"Between {second_groups['change_time'][:2]}:00 and {second_groups['change_time'][2:4]}:00 UTC",
                    'Wind': f"From {second_groups['change_wind'][:3]}° at {int(second_groups['change_wind'][3:5])} knots" if second_groups['change_wind'] else None,
                    'Visibility': f"{int(second_groups['change_visibility'])} meters" if second_groups['change_visibility'] else None,
                    'Clouds': second_groups['change_clouds'] if second_groups['change_clouds'] else None,
                    'Weather': second_groups['change_weather'] if second_groups['change_weather'] else None
                }
                becmg_matches.append(change_info)
        taf_info['Becoming'] = becmg_matches
        return taf_info
    else:
        return None

def generate_report(metar_info, taf_info):
    metar_report = f"""
METAR Report for {metar_info['Location']}:
-----------------------------------------
Time: {metar_info['Time']}
Wind: {metar_info['Wind']}
"""
    if 'Variable Wind' in metar_info:
        metar_report += f"Variable Wind: {metar_info['Variable Wind']}\n"
    metar_report += f"""Visibility: {metar_info['Visibility']}
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
        if 'Becoming' in taf_info:
            taf_report += "\nBecoming:\n"
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
    icao_code = input("Enter ICAO code: ").upper()
    raw_data = fetch_metar_taf_data(icao_code)
    
    # raw_data = """WATT 220530Z 30008KT 240V330 9999 BKN017 33/25 Q1011 NOSIG

# TAF WATT 220500Z 2206/2306 08016KT 9999 FEW018
    # BECMG 2210/2212 10006KT"""

    raw_metar, raw_taf = raw_data.split('\n\n')[:2]
    
    try:
        metar_info = parse_metar(raw_metar)
    except Exception as e:
        print(f"Error parsing METAR data: {e}")
        return

    try:
        taf_info = parse_taf(raw_taf)
    except Exception:
        taf_info = None

    generate_report(metar_info, taf_info)

if __name__ == "__main__":
    main()
