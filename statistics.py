import pymongo

mclient = pymongo.MongoClient()
mcollacs = mclient.aif.aircraft


def aggregate():
    # aggregate mdl statistic
    mcollacs.aggregate([
        {'$group': {
                '_id': '$mdl',
                'count': {'$sum': 1},
                'icaos': {'$push': '$icao'}
        }},
        {'$out': 'stat_mdl'}
    ])

    # aggregate operator statistic
    mcollacs.aggregate([
        {'$group': {
                '_id': '$operator',
                'count': {'$sum': 1},
                'icaos': {'$push': '$icao'},
                'mdls': {'$push': '$mdl'},
                'types': {'$push': '$type'}
        }},
        {'$out': 'stat_operator'}
    ])

    # aggregate operator statistic
    mcollacs.aggregate([
        {'$group': {
                '_id': '$type',
                'count': {'$sum': 1},
                'icaos': {'$push': '$icao'},
                'mdl': {'$first': '$mdl'}
        }},
        {'$out': 'stat_type'}
    ])


def mdls():
    mcoll = mclient.aif.stat_mdl
    data = list(
        mcoll.find({}, {'icaos': False}).sort('_id')
    )
    return data


def operators():
    mcoll = mclient.aif.stat_operator
    data = list(
        mcoll.find({}, {'icaos': False}).sort('_id')
    )
    return data


def types():
    mcoll = mclient.aif.stat_type
    data = list(
        mcoll.find({}, {'icaos': False}).sort('_id')
    )
    return data
