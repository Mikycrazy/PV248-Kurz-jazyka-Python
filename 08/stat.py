import pandas as pd
import numpy as np
import sys
import json

sys.argv[1] = "08/points.csv"
sys.argv[2] = "exercises"

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_

def get_stats(df, mode):
    if mode == 'dates':
        column = ['date']
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    elif mode == 'deadlines':
        column = ['variable']
    elif mode == 'exercises':
        column = ['exercise']

    data = df.groupby(column)['score'].agg([pd.np.mean, pd.np.median, percentile(25), percentile(75)])  
    data['passed'] =  df[df['score'] > 0].groupby(column)['score'].count()
    data = data.rename(index=str, columns={"percentile_25": "first", "percentile_75": "last"})
    return data.to_dict('index')

   
if len(sys.argv) < 3:
    exit("Too less arguments calling script")

file_name = sys.argv[1]
mode = sys.argv[2]

df = pd.read_csv(file_name, delimiter=',', encoding='latin1')
keys = list(df)[1:]
data = pd.melt(df, id_vars='student', value_vars=keys, value_name='score')
data[['date','exercise']] = data.variable.str.split('/', n=1, expand=True)
data['date'] =  pd.to_datetime(data['date'], format='%Y-%m-%d')
print(json.dumps(get_stats(data, mode), sort_keys=False, indent=2, ensure_ascii=True))
