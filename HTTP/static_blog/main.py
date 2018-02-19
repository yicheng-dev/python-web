
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        a = request.form['left']
        b = request.form['right']
        c = int(a) + int(b)        
        return render_template('index.html', RESULT = str(c))
    return render_template('index.html')

if __name__ == "__main__":
    app.run(port = 8080)