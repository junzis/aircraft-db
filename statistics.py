import pymongo

mclient = pymongo.MongoClient()
mCollAC = mclient.adb.aircraft
mCollStatMdl = mclient.adb.stat_mdl
mCollStatOperator = mclient.adb.stat_operator
mCollStatType = mclient.adb.stat_type


def treemaps():
    data1 = []
    data1.append(['Global', None, 0])

    opeartors = mCollStatOperator.find(
        {'count': {'$gt': 50}},
        {'icaos': False}
    ).sort('count', -1)

    for op in opeartors:
        opname = op['_id']
        data1.append([opname, 'Global', op['count']])

        mdls = {}

        for m in op['mdls']:
            M = m.upper()+' - ('+opname+')'
            if M in mdls:
                mdls[M] += 1
            else:
                mdls[M] = 1

        for m, c in mdls.iteritems():
            data1.append([m, opname, c])

    data2 = []
    data2.append(['All', None, 0])

    types = mCollStatType.find(
        {'count': {'$gt': 50}},
        {'icaos': False}
    ).sort('count', -1)

    mdls2 = {}

    for t in types:
        M = t['mdl'].strip().upper()
        data2.append([t['_id'], M, t['count']])

        if M in mdls2:
            mdls2[M] += t['count']
        else:
            mdls2[M] = t['count']

    for m, c in mdls2.iteritems():
        data2.append([m, 'All', c])

    return data1, data2


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
        {'$match': {
            'operator': {'$nin': ['Private owner', 'Private Owner', None]}
        }},
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
