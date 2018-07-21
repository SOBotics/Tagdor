import codecs
import csv
import inflect

import requests
from flask import Flask, jsonify

app = Flask(__name__)
p = inflect.engine()


@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return return_data("failure", "message", "route does not exist"), 404


@app.route("/tags/<string:tag_name>")
def get_if_burned(tag_name):
    url = 'https://raw.githubusercontent.com/SOBotics/Tagdor/master/StatusCompletedBurninateRequests.csv'
    r = requests.get(url)
    tag_name = tag_name.lower()
    pluralized_tag_name = p.plural(tag_name)
    singularized_tag_name = p.singular_noun(tag_name)
    singularized_tag_name = singularized_tag_name if singularized_tag_name else tag_name
    stripped_tag_name = tag_name.replace("-", "").replace(".", "")

    reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=',', quotechar='"')
    next(reader, None)
    for line in reader:
        burned_tags = [tag.strip().lower() for tag in line[1].strip("[]").split()]
        burned_tags_pluralized = [p.plural(tag) for tag in burned_tags]
        burned_tags_singularized = [p.singular_noun(tag) if p.singular_noun(tag) else tag for tag in burned_tags]
        burned_tags_stripped = [tag.replace("-", "").replace(".", "") for tag in burned_tags]

        all_burned_tags = burned_tags + burned_tags_pluralized + burned_tags_singularized + burned_tags_stripped
        if any(i in all_burned_tags for i in (tag_name, pluralized_tag_name, singularized_tag_name, stripped_tag_name)):
            return return_data("success", "burninated", True, meta_post=line[0])

    return return_data("success", "burninated", False)


def return_data(status, dtype, payload, **kwargs):
    result = {"status": status, dtype: payload}
    result.update(kwargs)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
