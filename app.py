from flask import Flask, request, redirect, url_for, render_template, make_response, jsonify
from io import BytesIO
import urllib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import wave
import numpy as np
import os

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['wav']) # アップロードできる形式をwavに限定

UPLOAD_DIR = 'C:/Users/dashi/Music/wave' # wavファイルのアップロード先
app.config['UPLOAD_DIR'] = UPLOAD_DIR

# アップロードされたファイルの形式が正しいか判別する
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/' ,  methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>
                波形を表示したいwaveファイルをアップロード



            </title>
        </head>
        <body>
            <h1>
                波形を表示したいwaveファイルをアップロード
            </h1>
            <form method = post enctype = multipart/form-data>
            <p><input type=file name = file>
            <input type = submit value = Upload>
            </form>
        </body>
'''

@app.route('/<filename>')
def uploaded_file(filename):
    # waveファイルを開く
    wf = wave.open(filename, 'r')
    print(wf.getparams())

    # 波形のデータを作る
    chunk_size = 1024
    amp = (2**8) ** wf.getsampwidth() / 2
    data = wf.readframes(chunk_size)
    data = np.frombuffer(data, 'int16')
    data = data / amp

    # グラフをプロットする
    fig = plt.figure()
    rate = wf.getframerate()
    size = float(chunk_size)
    x = np.arange(0, size/rate, 1.0/rate)
    plt.plot(x, data)

    # canvasにプロットした画像を出力
    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    data = png_output.getvalue()

    #HTML側に渡すレスポンスを生成する
    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content_Lengh'] = len(data)
    return response

if __name__ == "__main__":
    app.run(debug=True)