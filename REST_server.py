from flask import Flask, json, Response, request
from PASS import main as pass_main
from PASS import matches

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello world!'


@app.route('/get_demo')
def get_demo():
    print('PASS starting...')
    data = pass_main(['/Users/stasiuz/PASS/InfoXMLs/ACH_FCD_19122015_goal.xml', 'y'])
    print('PASS done!')

    print('Returning data...')
    return json_response(data)


@app.route('/get_matches')
def get_matches():
    print('Getting all available matches...')
    data = matches()

    print('Returning data...')
    return json_response(data)


@app.route('/get_summary')
def get_summary():
    file = request.args.get('file')
    data = pass_main(['/Users/stasiuz/PASS/InfoXMLs/' + file, 'y'])

    return json_response(data)


def json_response(data):
    response = Response(
        response=json.dumps(data),
        status=200,
        mimetype='application/json',
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == '__main__':
    print('REST service is starting...')
    app.run()
