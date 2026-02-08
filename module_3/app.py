from flask import Flask, render_template
from query_data import run_all_queries

app = Flask(__name__)

@app.route('/')
def index():
    """Display all query results on the main page"""
    results = run_all_queries()
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
