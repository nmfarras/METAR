import requests
import re

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
        r'(?P<wind>(\d{3}\d{2}(G\d{2})?KT|VRB\d{2}KT|00000KT))\s'
        r'((?P<variable_wind>\d{3}V\d{3})\s)?'
        r'(?P<visibility>\d{4})\s'
        r'(?P<clouds>(CLR|SKC|NCD|NSC|FEW\d{3}(CB|TCU)?|SCT\d{3}(CB|TCU)?|BKN\d{3}(CB|TCU)?|OVC\d{3}(CB|TCU)?)(\sCLR|\sSKC|\sNCD|\sNSC|\sFEW\d{3}(CB|TCU)?|\sSCT\d{3}(CB|TCU)?|\sBKN\d{3}(CB|TCU)?|\sOVC\d{3}(CB|TCU)?)*)\s'
        r'(?P<temperature>\d{2}/\d{2})\s'
        r'(?P<pressure>Q\d{4})\s*'
        r'(?P<forecast>(TEMPO|BECMG|PROB\d{2}|FM\d{4}|TL\d{4}|AT\d{4}|NSW)\s.*)?\s*'
        r'(?P<remarks>RMK\s.*)?'
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
            wind_info = f"From {wind[:3]}° at {int(wind[3:5])} knots"
            if 'G' in wind:
                gust_speed = int(wind[wind.index('G')+1:wind.index('KT')])
                wind_info += f", gusting to {gust_speed} knots"
        
        day = int(groups['datetime'][:2])
        date_suffix = get_date_suffix(day)
        
        cloud_layers = groups['clouds'].split()
        clouds_info = ', '.join([parse_cloud_condition(cloud) for cloud in cloud_layers])
        
        result = {
            'Location': groups['station'],
            'Time': f"{day}{date_suffix} of the current month at {groups['datetime'][2:4]}:{groups['datetime'][4:6]} UTC",
            'Wind': wind_info,
            'Visibility': f"{int(groups['visibility'])} meters (10+ km)" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Clouds': clouds_info,
            'Temperature': f"{groups['temperature'].split('/')[0]}.0°C",
            'Dewpoint': f"{groups['temperature'].split('/')[1]}.0°C",
            'Pressure': f"{groups['pressure'][1:]} hPa",
            'Remarks': parse_remarks(groups.get('remarks', 'NOSIG'))
        }
        if groups['variable_wind']:
            result['Variable Wind'] = f"Between {groups['variable_wind'][:3]}° and {groups['variable_wind'][4:]}°"
        if groups['forecast']:
            result['Forecast'] = groups['forecast']
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
    match = taf_pattern.match(taf_lines[0])
    if match:
        groups = match.groupdict()
        wind = groups['wind']
        taf_info = {
            'Location': groups['station'],
            'Issue Time': f"{groups['datetime'][:2]}{get_date_suffix(int(groups['datetime'][:2]))} of the current month at {groups['datetime'][2:4]}:{groups['datetime'][4:6]} UTC",
            'Forecast Validity': f"From {groups['validity'][:2]}{get_date_suffix(int(groups['validity'][:2]))} at {groups['validity'][2:4]} UTC to {groups['validity'][5:7]}{get_date_suffix(int(groups['validity'][5:7]))} at {groups['validity'][7:]} UTC",
            'Wind': f"From {wind[:3]}° at {int(wind[3:5])} knots",
            'Visibility': f"{int(groups['visibility'])} meters (10+ km)" if int(groups['visibility']) == 9999 else f"{int(groups['visibility'])} meters",
            'Clouds': parse_cloud_condition(groups['clouds'])
        }
        
        changes = []
        for line in taf_lines[1:]:
            match_becmg = becmg_pattern.match(line)
            if match_becmg:
                change_groups = match_becmg.groupdict()
                change = {
                    'Timeframe': f"Between {change_groups['change_time'][:2]}{get_date_suffix(int(change_groups['change_time'][:2]))} at {change_groups['change_time'][2:4]} UTC and {change_groups['change_time'][5:7]}{get_date_suffix(int(change_groups['change_time'][5:7]))} at {change_groups['change_time'][7:]} UTC",
                    'Wind': f"From {change_groups['change_wind'][:3]}° at {int(change_groups['change_wind'][3:5])} knots" if change_groups['change_wind'] else None,
                    'Visibility': f"{int(change_groups['change_visibility'])} meters (10+ km)" if change_groups['change_visibility'] and int(change_groups['change_visibility']) == 9999 else f"{int(change_groups['change_visibility'])} meters" if change_groups['change_visibility'] else None,
                    'Clouds': parse_cloud_condition(change_groups['change_clouds']) if change_groups['change_clouds'] else None,
                    'Weather': "No significant weather" if change_groups['change_weather'] == "NSW" else None
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
Clouds: {metar_info['Clouds']}
Temperature: {metar_info['Temperature']}
Dewpoint: {metar_info['Dewpoint']}
Pressure: {metar_info['Pressure']} hPa
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
    
    raw_data = """WIII 280430Z 070009KT 020V110 9000 FEW018CB SCT019 32/24 Q1010 TEMPO FM0445 4000 TSRA RMK CB TO S AND SE

TAF WIII 272300Z 2800/2906 15004KT 9999 FEW020
    BECMG 2804/2806 07012KT
	BECMG 2812/2814 19005KT
"""
    raw_data = """WATT 220530Z 30008KT 240V330 9999 BKN017 33/25 Q1011 NOSIG

TAF WATT 220500Z 2206/2306 08016KT 9999 FEW018
    BECMG 2210/2212 10006KT"""
    
    raw_data = """WALL 010400Z 22003KT 8000 -RA SCT020 27/27 Q1010

TAF WALL 302300Z 0100/0206 27005KT 9999 FEW020
  TEMPO 0102/0106 3500 -TSRA SCT017CB"""
    
    raw_metar, raw_taf = raw_data.split('\n\n')[:2]
    
    print(raw_metar)
    
    try:
        metar_info = parse_metar(raw_metar)
    except Exception as e:
        print(f"Error parsing METAR data: {e}")
        return

    try:
        taf_info = parse_taf(raw_taf)
    except Exception as e:
        print(f"Error parsing TAF data: {e}")
        taf_info = None

    generate_report(metar_info, taf_info)

if __name__ == "__main__":
    main()
