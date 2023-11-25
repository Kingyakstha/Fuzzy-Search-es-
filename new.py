from flask import Flask, request,render_template
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=["http://127.0.0.1:9200"])


app = Flask(__name__)

MAX_SIZE = 15

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/searchs")
def search_autocomplete():
    query = request.args["q"].lower()
    tokens = query.split(" ")
    print(tokens)

    clauses = [
        {
            "span_multi": {
                "match": {"fuzzy": {"desc": {"value": i, "fuzziness": "AUTO"}}}
            }
        }
        for i in tokens
    ]

    payload = {
        "bool": {
            "must": [{"span_near": {"clauses": clauses, "slop": 0, "in_order": False}}]
        }
    }

    resp = es.search(index="updated_qp", query=payload, size=MAX_SIZE)
    return [result["_source"]["desc"] for result in resp["hits"]["hits"]]


if __name__ == "__main__":
    app.run(debug=True)
