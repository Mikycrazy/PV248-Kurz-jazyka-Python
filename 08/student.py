import pandas as pd
import numpy as np
import sys
import math
from scipy import stats
import json
import datetime

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
data.to_csv('student.csv', sep=';')

if student_id == 'average':
    tmp = data.groupby(['student', 'exercise', 'date']).sum().reset_index()
else:
    tmp = data[data['student'] == int(student_id)]

tmp = tmp.groupby(['exercise', 'date'])['score'].mean().reset_index()
date = tmp.groupby(['date'])['score'].sum().cumsum()
tmp = tmp.groupby(['exercise'])['score'].sum()
mean = tmp.mean()
median = tmp.median()
passed = tmp[tmp.gt(0)].count()
total = tmp.sum()

A = np.vstack([date.index, np.ones(len(date.index))]).T
coef, _ = np.linalg.lstsq(A, date, rcond=None)[0]

# slope, intercept, r_value, p_value, std_err = stats.linregress(date.index, date)
xp = range(60, 160)
reg = pd.Series([(START_DATE + np.timedelta64(x,'D')) for x in xp], [coef * x for x in xp])
print(reg)

d = {'mean': mean, 'median': median, 'passed': int(passed), 'total': total, 'regression slope': coef}
if(coef > 0):
    date_16 = (START_DATE + np.timedelta64(int(16/coef),'D')).astype(datetime.datetime).strftime('%Y-%m-%d')
    date_20 = (START_DATE + np.timedelta64(int(20/coef),'D')).astype(datetime.datetime).strftime('%Y-%m-%d')
    d['date 16'] = date_16
    d['date 20'] = date_20

print(json.dumps(d, sort_keys=False, indent=2))