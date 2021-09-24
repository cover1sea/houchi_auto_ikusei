# 概要
放置少女用育成スクリプト  
機能：  
- 設定に応じた自動育成  
    - C級 or B級
    - 育成重み指定
    - 育成回数指定
- 指定回数の育成終了後のステータス増加量の計算    

# 動作確認環境
Windows 10  
Python 3  
NoxPlayer 7  
Amazon版 放置少女アプリ

# 初期設定
1. python3をインストール(未インストールの場合)  
    参考記事  
    <https://qiita.com/New_enpitsu_15/items/ee95bde0858e9f77acf0>  

2. 各種ライブラリインストール  
    ```
    python -m pip install opencv-python  
    python -m pip install pyocr  
    ```
    (多分これだけだが、足りなさそうなら適宜インストール)

3. Tesseract-OCRをインストール(未インストールの場合)  
    <https://github.com/UB-Mannheim/tesseract/wiki>

4. nox_adbのPathを通す  
    <https://www.google.com/search?q=nox+adb>

5. main.py内の変数nox_dirの内容変更  
    "F:\\Nox\bin"の部分を"自身のNoxのインストールフォルダ\bin"に変更  
    これはやらなくても動くかも


6. Noxの解像度を携帯電話、540×960に変更  
    解像度を変更したくない/できない場合は、変数preStatusxy、statusxy、tapxyを対応する座標に書き換えてください。

# つかいかた
1. 育成画面を開く  
    AUTO育成はチェックを外しておく。
2. 以下の書式でコマンド実行  
    `$python main.py c|b 筋力 敏捷 知力 体力 育成回数 `    
    サンプルとして育成方法を設定したバッチファイルをいくつか入れています。  
    (~~.batをクリックすれば実行されます。)  

育成ができない場合はPCスペック不足で表示が追いつかずにエラーが出ている可能性があります。  
その場合はtap関数の最後(38行目)のtime.sleep(1)の数値を増やしてみたりするといいかも。  

# 免責
使用は自己責任でお願いします。
