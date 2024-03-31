import math
import pandas as pd
def group_normalize(file):
  df = pd.read_json(file)
  df['count'] = 1
  sum_df = df.groupby(['frame']).sum()
  sum_df = sum_df.drop(columns=['character','contempt','neutral'])
  sum_df[['anger','disgust','fear','happy','sad','surprise']]=sum_df[['anger','disgust','fear','happy','sad','surprise']].div(sum_df['count'], axis=0)
  sum_df = sum_df.drop(columns=["count"])
  sub = math.ceil(len(sum_df)/10)
  sum_df = sum_df.reset_index()
  sum_df = sum_df.groupby(sum_df.index // sub).mean()
  sum_df = sum_df.drop(columns=['frame'])
  sum_df['Max'] = sum_df.idxmax(axis=1)
  return list(sum_df.Max)

def lcs(X, Y, m, n):
    if m == 0 or n == 0:
        return 0
    elif X[m-1] == Y[n-1]:
        return 1 + lcs(X, Y, m-1, n-1)
    else:
        return max(lcs(X, Y, m, n-1), lcs(X, Y, m-1, n))
