from flask import Flask
from flask_bootstrap import Bootstrap
from stream import *
import json

app = Flask(__name__)
bootstarp = Bootstrap(app)

#router
from flask import render_template, redirect, request

@app.route('/', methods = ['GET'])
def index():
    data = None
    return render_template('index.html', key_word = '', title = 'Pixiv')

@app.route('/search/<info>', methods = ['GET'])
def search(info):
    key = json.loads(info)
    data = StreamUpdate(key['key'], page = key['page'])
    print(data)
    return render_template('result.html', page_list = data['page_list'], current_page = data['current_page'], data = data)


if __name__ == '__main__':
    app.run(debug = True)
