#!/usr/bin/python
import sys
import csv

import GeoIP

gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
gc = GeoIP.open("/usr/share/GeoIP/GeoLiteCity.dat",GeoIP.GEOIP_STANDARD)


def geo_access():
    ip_buffer = {}
    processed_records = 0
    for line in sys.stdin.readlines():
        key = (line.replace('\n', ''))
        ip_buffer[key] = ip_buffer.get(key, 0) + 1
        processed_records += 1

    geo_country = {}
    for key,value in ip_buffer.items():
        country = gi.country_name_by_addr(key)
        if country == None:
            country = 'None'
        key = (country)
        geo_country[key] = geo_country.get(key, 0) + value

    geo_buffer = {}
    for key,value in ip_buffer.items():
        country = gi.country_name_by_addr(key)
        if country == None:
            country = 'None'
        city = gc.record_by_addr(key)
        if city == None:
            city = 'None'
        else:
            city = city['city'] if 'city' in city and city['city'] != None else 'None'
        key = (country, city)
        geo_buffer[key] = geo_buffer.get(key, 0) + value

    outfile = open('Country_city_geo_access.csv', 'w')
    writer = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='`')
    for key,value in sorted(geo_buffer.items()):
        data = []
        data.append(' '.join(key))
        data.append(str(round((float(value)/float(processed_records))*100, 7)).replace('.', ','))
        writer.writerow(data)
    outfile.close()

    outfile = open('Country_geo_access.csv', 'w')
    writer = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='`')
    for key,value in sorted(geo_country.items()):
        data = []
        data.append(key)
        data.append(str(round((float(value)/float(processed_records))*100, 7)).replace('.', ','))
        writer.writerow(data)
    outfile.close()




if __name__ == '__main__':
    geo_access()
