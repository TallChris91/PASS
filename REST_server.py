from flask import Flask, json
from PASS import main as pass_main

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello world!'


@app.route('/pass')
def run_main():
    print('PASS started')
    data = pass_main(['/Users/stasiuz/PASS/InfoXMLs/ACH_FCD_19122015_goal.xml', 'y'])

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    print('REST service is starting...')
    app.run()