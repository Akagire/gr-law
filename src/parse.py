import os
import glob
import math
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

        # 緯度経度が未設定の場合は除外
        df = df[pd.to_numeric(df['経度_度'], errors='coerce').notnull()]
        df = df[pd.to_numeric(df['経度_分'], errors='coerce').notnull()]
        df = df[pd.to_numeric(df['緯度_度'], errors='coerce').notnull()]
        df = df[pd.to_numeric(df['緯度_分'], errors='coerce').notnull()]

        df = df[pd.to_numeric(df['経度_度'], errors='coerce').notna()]
        df = df[pd.to_numeric(df['経度_分'], errors='coerce').notna()]
        df = df[pd.to_numeric(df['緯度_度'], errors='coerce').notna()]
        df = df[pd.to_numeric(df['緯度_分'], errors='coerce').notna()]

        # 緯度経度の分に秒も含まれてるので小数点に変換
        df['経度_度'] = df['経度_度'].astype(float)
        df['経度_分'] = df['経度_分'].astype(float)
        df['経度_分'] =  df['経度_分'] / 100.0 / 60.0

        df['緯度_度'] = df['緯度_度'].astype(float)
        df['緯度_分'] = df['緯度_分'].astype(float)
        df['緯度_分'] =  df['緯度_分'] / 100.0 / 60.0

        # 緯度経度を数値変換
        df['latitude']  = df['緯度_度'] + df['緯度_分']
        df['longitude'] = df['経度_度'] + df['経度_分']

        # 対数グラフを表示したいので、最低 M 値未満の値は捨てる
        df = df[df['マグニチュード'] >= min_m]

        li.append(df)

        df = pd.concat(li, axis=0, ignore_index=True)

    # キャッシュへ書き込み
    df.to_pickle(cache_file_path);

# 準備完了

# 容量確認
print(df.info())

# a 値を計算するために、最低マグニチュードの件数を取得
min_m_cnt = df['マグニチュード'].value_counts()[min_m]

# ヒストグラムのビンの範囲を設定（4~9.2まで0.1刻み）
bins = np.arange(4, 9.2, 0.1)

# データをビンに分割して、各便の値の出現数を計算する
hist, bins = np.histogram(df['マグニチュード'], bins=bins)

# b値は実測値との調整なので、都合よく変えて良い
# b = 0.7 # 2017~2021の傾向としてはよさそう
b = 0.62
a = gr.gr_a(min_m_cnt, min_m, b)

# GR則を計算
y = gr.gr(bins, a, b)

# matplotlib の設定
# y軸を対数にする
plt.yscale('log')
plt.xlabel('Magnitude(M >= ' + str(min_m) + ')')
plt.ylabel('Events')
plt.title('Earthquake Events (1997/10 ~ 2021/12) and GR Rule')

# マグニチュードが4~9(0.1刻み)の発生件数を棒グラフでプロットする
plt.bar(bins[:-1], hist, width=0.1)

# GR則のグラフをプロットする
label = 'a=' + str(a) + ' b=' + str(b)
plt.plot(bins, y, color='red', label=label)

plt.legend()
plt.show()
