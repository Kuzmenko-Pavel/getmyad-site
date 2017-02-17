# encoding: utf-8
# Скрипт анализирует файл с логами mongostat и определяет, сколько времени база данных бездействовала
# (меньше 10 запросов в секунду). На данный момент один запрос к показу рекламы GetMyAd должен
# производить один запрос к mongodb, так что это фактически показатель работоспособности GetMyAd 
 
import sys

if len(sys.argv) < 2:
    print 'Analyze mongostat log.  Usage: mongostat-analyzer.py logfilename [--verbose]'
    exit()

try:
    log = open(sys.argv[1])
except IOError:
    print 'Error opening log file!'
    exit()

try:
    verbose = (sys.argv[2] == '--verbose')
except:
    verbose = False
    
downtime = 0
total = 0

for row in log:
    if row[0] <> ' ':
        continue
    total += 1
    val = [x for x in row.split(' ') if x]
    if int(val[1]) < 5:
        if verbose:
            print row,
        downtime += 1

print 'Total minutes:    ', total / 60
print 'Downtime minutes: ', downtime / 60
print 'Uptime rate:      ', 100 - (float(downtime) / total) * 100.0
    
