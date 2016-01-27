import pymongo
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
import spider
import reverse_geocode
import numpy as np

mclient = pymongo.MongoClient()
mCollAC = mclient.adb.aircraft
mCollStatMdl = mclient.adb.stat_mdl
mCollStatOperator = mclient.adb.stat_operator
mCollStatType = mclient.adb.stat_type


def top_mdl(num=20):
    mdls = list(
        mCollStatMdl.find({}, {'icaos': False}).sort('count', -1).limit(num)
    )

    data = {
        'mdl': [],
        'type': [],
        'count': [],
    }

    for mdl in mdls:
        types = list(
            mCollStatType.find(
                {'mdl': mdl['_id']},
                {'icaos': False, 'mdl': False}
            )
            .sort('count', -1).limit(4)
        )

        rest = mdl['count']

        for t in types:
            data['mdl'].append(mdl['_id'].upper())
            data['type'].append(encode_utf8(t['_id']))
            data['count'].append(t['count'])
            rest -= t['count']

        data['mdl'].append(mdl['_id'].upper())
        data['type'].append('Others')
        data['count'].append(rest)

    palette = ['#fdd0a2', '#fdae6b', '#fd8d3c', '#e6550d', '#a63603']
    palette.reverse()

    bar = Bar(
        data,
        values='count',
        label=cat('mdl', sort=False),
        stack=cat('type', sort=False),
        xlabel='Model',
        ylabel='Number of aircraft',
        color=color(columns=('mdl', 'type'), palette=palette, sort=False),
        tooltips=[('Type', '@type'), ('Model', '@mdl')],
        title="Aircraft Models Statistic",
        plot_width=800
    )

    script, div = components(bar)
    return script, div


def top_operator(num=20):
    opeartors = list(
        mCollStatOperator.find({}, {'icaos': False})
                         .sort('count', -1).limit(num)
    )

    data = {
        'operator': [],
        'mdl': [],
        'count': [],
    }

    for op in opeartors:
        models = {}
        for m in op['mdls']:
            # data['operator'].append(op['_id'])
            # data['mdl'].append(m)
            if m in models:
                models[m] += 1
            else:
                models[m] = 0

        for m, c in models.iteritems():
            data['operator'].append(op['_id'])
            data['mdl'].append(m)
            data['count'].append(c)

    # palette = ['#fdd0a2', '#fdae6b', '#fd8d3c', '#e6550d', '#a63603']
    # palette.reverse()

    bar = Bar(
        data,
        values='count',
        label=cat('operator', sort=False),
        stack='mdl',
        xlabel='Airlines',
        ylabel='Number of aircraft',
        color='#31a354',
        tooltips=[('Model', '@mdl'), ('Operator', '@operator')],
        title="Aircraft Operator Statistic",
        plot_width=800
    )

    script, div = components(bar)
    return script, div


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


def realtime_geo_histo(flag=None):
    acs = spider.fetch_all_acs(withpos=True)
    coordinates = [(i['lat'], i['lon']) for i in acs]

    geos = reverse_geocode.search(coordinates)

    countries = {}
    for g in geos:
        c = g['country']
        if c in countries:
            countries[c] += 1
        else:
            countries[c] = 1

    data = []
    data.append(['Country', 'Air traffic density'])
    for c, cnt in countries.iteritems():
        if flag == 'norm':
            data.append([c, np.log(cnt)])
        else:
            data.append([c, cnt])

    return data


def realtime_traffic():
    acs = spider.fetch_all_acs(withpos=True, withspd=True)
    data = [(i['lat'], i['lon'], i['spd'], np.radians(i['hdg'])) for i in acs]
    return data


def realtime_density_plot():
    import os
    import numpy as np
    import scipy.stats
    from matplotlib import pyplot as plt
    dirpath = os.path.dirname(os.path.abspath(__file__))

    acs = spider.fetch_all_acs(withpos=True, withspd=True)
    data = [(i['lat'], i['lon']) for i in acs]
    datanp = np.array(data)

    x1 = np.array(datanp[:, 1])
    y1 = np.array(datanp[:, 0])

    xmin = x1.min()
    xmax = x1.max()
    ymin = y1.min()
    ymax = y1.max()

    X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x1, y1])
    kernel = scipy.stats.gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, X.shape)

    plt.figure(figsize=(12, 5))
    im = plt.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
                    extent=[xmin, xmax, ymin, ymax], aspect='auto')
    plt.scatter(x1, y1, c='k', marker='.', s=1, lw=0)
    plt.contour(X, Y, Z, linewidths=0.5)
    # cbar1 = plt.colorbar(shrink=0.8)
    # cbar1.ax.tick_params(labelsize=10)
    cbar2 = plt.colorbar(im)
    cbar2.ax.tick_params(labelsize=10)
    plt.xlim([X.min(), X.max()])
    plt.ylim([Y.min(), Y.max()])
    plt.grid()
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.savefig(dirpath+"/static/density_plot.png", bbox_inches='tight')
    return


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

if __name__ == '__main__':
    df = realtime_density_plot()
