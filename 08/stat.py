import pandas as pd
import numpy as np
import sys
import json

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_

def get_stats(df, mode):
    if mode == 'dates':
        column = ['date']
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        data = df.groupby(['student', 'date'])['score'].sum().reset_index()
    elif mode == 'deadlines':
        column = ['variable']
        data = df
    elif mode == 'exercises':
        column = ['exercise']
        data = df.groupby(['student', 'exercise'])['score'].sum().reset_index()

    agg_data = data.groupby(column)['score'].agg([pd.np.mean, pd.np.median, percentile(25), percentile(75)])  
    agg_data['passed'] = data[data['score'] > 0].groupby(column)['score'].count()
    agg_data = agg_data.rename(index=str, columns={"percentile_25": "first", "percentile_75": "last"})
    agg_data.fillna(0, inplace=True)
    return agg_data.to_dict('index')

   
if len(sys.argv) < 3:
    exit("Too less arguments calling script")

file_name = sys.argv[1]
mode = sys.argv[2]

df = pd.read_csv(file_name, delimiter=',', encoding='latin1')
keys = [x for x in list(df) if x != 'student']
data = pd.melt(df, id_vars='student', value_vars=keys, value_name='score')
data[['date','exercise']] = data.variable.str.split('/', n=1, expand=True)
data['date'] =  pd.to_datetime(data['date'], format='%Y-%m-%d')
d = get_stats(data, mode)
print(json.dumps(d, sort_keys=False, indent=2, ensure_ascii=False))
