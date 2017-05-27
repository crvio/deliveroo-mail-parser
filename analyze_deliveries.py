# -*- coding: latin-1 -*-
import json
import datetime 
from pprint import pprint
import argparse

parser = argparse.ArgumentParser(description='Analiza la información de entregas enviada por deliveroo... almacenada previamente en deliveries.json o en el archivo especificado')
parser.add_argument('-f','--jsonfile', help='El archivo json con la información de los correos. Default is "deliveries.json"', default='deliveries.json', required=False)
parser.add_argument('--daterange', help='El rango de fechas para el cual calcular estadísticas. Usar formato "YYmmdd-YYmmdd". Ejemplo: 20161101-20161115', required=False)
parser.add_argument('-v','--verbose', action='store_true', default=False, help='Print detailed information of days', required=False)
#parser.add_argument('-c','--concise', help='Only list the dates within the date range specified. It has no effect when no date range is specified', required=False)
args = vars(parser.parse_args())

d_delta = datetime.timedelta(days=1)
if args['daterange'] is not None:
    fnldates = args['daterange'].split("-")
    if len(fnldates) != 2:
        raise Exception('Use YYmmdd-YYmmdd format for specifying date range')
    fs_datetime = datetime.datetime.strptime(fnldates[0],'%Y%m%d')
    fs_day = fs_datetime.date()
    ls_datetime = datetime.datetime.strptime(fnldates[1],'%Y%m%d')
    ls_day = ls_datetime.date()
    ls_datetime = ls_datetime+d_delta 
    if fs_day > ls_day:
        raise Exception('First day in date range cannot be later than the last day')

f = open(args['jsonfile'], 'r')
deliveries = json.load(f)

# arreglar esto para que sea más general
max_date = datetime.datetime.today()-datetime.timedelta(days=7)
min_date = datetime.datetime.today()-datetime.timedelta(days=7)

for delivery in deliveries:
    deldate = datetime.datetime.strptime(delivery['date'],'%Y-%m-%d %H:%M:%S')
    delivery['date_obj'] = deldate
    if deldate > max_date:
        max_date = deldate
    if deldate < min_date:
        min_date = deldate

if args['daterange'] is None:

    fs_datetime = datetime.datetime(min_date.year, min_date.month, min_date.day)
    fs_day = fs_datetime.date()
    ls_datetime = datetime.datetime(max_date.year, max_date.month, max_date.day)#+d_delta
    ls_day = ls_datetime.date()
    ls_datetime = ls_datetime+d_delta 

    statstitle = "=== All-time statistics ==="
else:
    statstitle = "=== Specified period statistics ==="

deliveries_n = [delivery for delivery in deliveries if delivery['date_obj']>fs_datetime and delivery['date_obj']<ls_datetime]

deltimes_n = [int(delivery['deltime_s']) for delivery in deliveries_n] 
tip_money_n = [float(delivery['tip_cc']) for delivery in deliveries_n]

ndel_r = len(deliveries_n)

if ndel_r != 0:
    mean_delivery_time_s_n = float(sum(deltimes_n))/ndel_r
    mean_time_string = "\t\t{:.1f} s".format(mean_delivery_time_s_n) 
else:
    mean_time_string = "\t\t-"

total_tips_by_cc_n = sum(tip_money_n)

working_period_r = ls_day - fs_day

date_objs_n = [fs_day + d_delta*i for i in range(working_period_r.days+1)]
#pprint(date_objs)
dates_n = [(date.year,date.month,date.day) for date in date_objs_n]
desglose = {date_tuple:[] for date_tuple in dates_n}
fdelpd = {date_tuple:datetime.time(23,59,59) for date_tuple in dates_n}
ldelpd = {date_tuple:datetime.time(0,0,0) for date_tuple in dates_n}

for delivery in deliveries_n:
    ddate=delivery['date_obj']
    dtuple=(ddate.year,ddate.month,ddate.day)
    desglose[dtuple].append(delivery)
    if delivery['date_obj'].time() < fdelpd[dtuple]:
        fdelpd[dtuple] = delivery['date_obj'].time()
    if delivery['date_obj'].time() > ldelpd[dtuple]:
        ldelpd[dtuple] = delivery['date_obj'].time()

print("")
print(statstitle)
print("")
print("min date:\t%s" % fs_day)
print("max date:\t%s" % ls_day)
print("working period:\t%d days" % (working_period_r.days+1))
print("deliveries:\t%s" % len(deliveries_n))
print("Mean delivery time:")
print(mean_time_string)
print("Tips with creditcard:")
print("\t\t%.2f euro" % total_tips_by_cc_n)
print("")

dsotw = {1:'mon',2:'tue',3:'wed',4:'thu',5:'fri',6:'sat',7:'sun'}

if args['verbose']:
    print("    date\tdels\tmean_t\ttip_cc\ttofdel\t\ttoldel")

    for date in dates_n:
        ndel=len(desglose[date])
        dow=datetime.date(date[0],date[1],date[2]).isoweekday()
        tipmoney=sum([float(delivery['tip_cc']) for delivery in desglose[date]])
        if ndel:
            meandtime=float(sum([delivery['deltime_s'] for delivery in desglose[date]]))/ndel
            print("%s %d-%02d-%02d\t%4d\t%.2f\t%.2f\t%s\t%s" % (dsotw[dow],date[0],date[1],date[2],ndel,meandtime,tipmoney,fdelpd[date],ldelpd[date]))
        else:
            #ndel='-'
            print("%s %d-%02d-%02d\t  -\t-\t-\t-\t-" % (dsotw[dow],date[0],date[1],date[2]))
    
    print("")
