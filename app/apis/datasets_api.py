from flask import Blueprint, jsonify, request
from sqlalchemy import func, distinct
from importlib import import_module
from inflection import singularize
from app import cache
from app.helpers.cache_helper import api_cache_key

blueprint = Blueprint('api', __name__, url_prefix='/')

@blueprint.route('<dataset>/<path:path>/')
@cache.cached(key_prefix=api_cache_key('dataset'))
def api(dataset, path):
    global Model
    class_name = ''.join([x.title() for x in dataset.split('_')])
    Model = getattr(import_module('app.models.' + dataset), class_name)
    
    dimensions = map(singularize, path.split('/'))
    if invalid_dimension(dimensions):
        return 'Error', 403

    filters = {k: v for k, v in request.args.to_dict().iteritems() if k in Model.dimensions()}
    counts = [c for c in map(singularize, request.args.getlist('count')) if c in Model.dimensions()]

    values = get_values(request)

    group_columns = get_columns(dimensions)
    count_columns = get_columns(counts)
    aggregated_values = [Model.aggregate(v) for v in values]

    headers = get_headers(group_columns) + get_headers(count_columns, '_count') + values
    entities = group_columns + map(lambda x: func.count(distinct(x)), count_columns) + aggregated_values
    query = Model.query.with_entities(*entities).filter_by(**filters).group_by(*group_columns)

    direction = request.args.get('direction', '')
    order = request.args.get('order', None)
    if order:
        if order in Model.dimensions():
            order_by = getattr(Model, order)
        else:
            order_by = Model.aggregate(order)

        if direction.lower() == 'desc':
            order_by = order_by.desc()

        query = query.order_by(order_by)

    limit = request.args.get('limit', None)
    if limit:
        query = query.limit(limit)

    return jsonify(data=query.all(), headers=headers)

def get_values(request):
    values = [v for v in request.args.getlist('value') if v in Model.values()]
    return values if len(values) else Model.values()

def get_headers(columns, suffix=''):
    return map(lambda x: x.key + suffix, columns)

def get_columns(dimensions):
    return [getattr(Model, dimension) for dimension in dimensions]

def invalid_dimension(dimensions):
    return not set(dimensions).issubset(set(Model.dimensions()))
