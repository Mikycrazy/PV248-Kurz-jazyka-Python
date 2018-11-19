import pandas as pd
import numpy as np
import sys
import math
from scipy import stats
import json
import datetime

sys.argv[1] = "08/points.csv"
sys.argv[2] = "111"

if len(sys.argv) < 3:
    exit("Too less arguments calling script")

file_name = sys.argv[1]
student_id = sys.argv[2]

START_DATE = np.datetime64('2018-09-17')

df = pd.read_csv(file_name, delimiter=',', encoding='latin1')
keys = list(df)[1:]
data = pd.melt(df, id_vars='student', value_vars=keys, value_name='score')
data[['date','exercise']] = data.variable.str.split('/', n=1, expand=True)
data['date'] =  pd.to_datetime(data['date'], format='%Y-%m-%d')
data['date'] = (data['date'] - START_DATE).astype('timedelta64[D]')
if student_id == 'average':
    tmp = data.groupby(['student', 'exercise', 'date']).sum().reset_index()
    tmp = tmp.groupby(['exercise', 'date'])['score'].mean().reset_index()
    date = tmp.groupby(['date'])['score'].sum().cumsum()
    tmp = tmp.groupby(['exercise'])['score'].sum()
else:
    tmp = data[data['student'] == int(student_id)]
    tmp = tmp.groupby(['exercise', 'date'])['score'].mean().reset_index()
    date = tmp.groupby(['date'])['score'].sum().cumsum()
    tmp = tmp.groupby(['exercise'])['score'].sum()

mean = tmp.mean()
median = tmp.median()
passed = tmp[tmp.gt(0)].count()
total = tmp.sum()

slope, intercept, r_value, p_value, std_err = stats.linregress(date.index, date)
xp = range(160)

reg = pd.Series(xp, [slope * x for x in xp])

date_16 = (START_DATE + np.timedelta64(math.ceil(16/slope),'D')).astype(datetime.datetime)
date_20 = (START_DATE + np.timedelta64(math.ceil(20/slope),'D')).astype(datetime.datetime)



d = {'mean': mean, 'median': median, 'passed': int(passed), 'total': total, 'regression slope': slope, 'date 16': date_16.strftime('%Y-%m-%d'), 'date 20': date_20.strftime('%Y-%m-%d')}
print(json.dumps(d, sort_keys=False, indent=2))