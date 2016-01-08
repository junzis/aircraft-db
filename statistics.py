from webserver import mCollAC


def aggregate():
    # aggregate mdl statistic
    mCollAC.aggregate([
        {'$group': {
                '_id': '$mdl',
                'count': {'$sum': 1},
                'icaos': {'$push': '$icao'}
        }},
        {'$out': 'stat_mdl'}
    ])

    # aggregate operator statistic
    mCollAC.aggregate([
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
    mCollAC.aggregate([
        {'$group': {
                '_id': '$type',
                'count': {'$sum': 1},
                'icaos': {'$push': '$icao'},
                'mdl': {'$first': '$mdl'}
        }},
        {'$out': 'stat_type'}
    ])
