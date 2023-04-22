import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import definition
import gr

# 設定
## 計測上最低のマグニチュード
min_m = 4

# キャッシュがないか確認する
cache_file_path = '../cache/df.pickle'

if (os.path.isfile(cache_file_path)):
  print('read df from cache')
  df = pd.read_pickle(cache_file_path)
else:
  print('create df from file')
  # 読み込むファイルのパスを取得
  path = '../data/centre'
  files = glob.glob(path + '/*')

  li = []

  for file in files:
    print('file', file)
    df = pd.read_fwf(
        file,
        colspecs=definition.colspecs,
        header=None
      )

    # ヘッダー名称設定
    df.columns = definition.headerName

    # クレンジング
    # マグニチュードが未設定だったり極端に小さい数が入っている場合は除外
    df = df[pd.to_numeric(df['マグニチュード'], errors='coerce').notnull()]

    # マグニチュード 7.0 の場合 70 と格納されているので処理
    df['マグニチュード'] = df['マグニチュード'].astype(float)
    df['マグニチュード'] = df['マグニチュード'] / 10.0

    # 対数グラフを表示したいので、最低 M 値未満の値は捨てる
    df = df[df['マグニチュード'] >= min_m]

    li.append(df)

  df = pd.concat(li, axis=0, ignore_index=True)

# 準備完了

# 容量確認
print(df.info())

# a 値を計算するために、最低マグニチュードの件数を取得
min_m_cnt = df['マグニチュード'].value_counts()[min_m]

df.to_pickle(cache_file_path);

# ヒストグラムのビンの範囲を設定（4~9まで0.1刻み）
bins = np.arange(4, 9.1, 0.1)

# データをビンに分割して、各便の値の出現数を計算する
hist, bins = np.histogram(df['マグニチュード'], bins=bins)

# b値は実測値との調整なので、都合よく変えて良い
b = 0.7
a = gr.gr_a(min_m_cnt, min_m, b)

# GR則を計算
y = gr.gr(bins, a, b)

# matplotlab の設定
# y軸を対数にする
plt.yscale('log')
plt.xlabel('Magnitude')
plt.ylabel('Frequency')


# マグニチュードが4~9(0.1刻み)の発生件数を棒グラフでプロットする
plt.bar(bins[:-1], hist, width=0.1)

# GR則のグラフをプロットする
label = 'GR a=' + str(a) + ' b=' + str(b)
plt.plot(bins, y, color='red', label=label)

plt.legend()
plt.show()
