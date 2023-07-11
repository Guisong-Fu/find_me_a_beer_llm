from flask import Flask, render_template, request, jsonify
import json
import pure_openai_api

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_text = request.form.get('user_text')
        beer_json = pure_openai_api.find_beer(user_text)
        print(beer_json)
        beer_data = json.loads(beer_json)
        return render_template('index.html', beer=beer_data)
    else:
        return render_template('index.html', beer=None)

if __name__ == '__main__':
    app.run(debug=True)
