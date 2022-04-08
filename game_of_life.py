import sys
from time import time

from pymongo import MongoClient, ASCENDING

DB = "game_of_life"
COLL = "coll"
START_RATIO_ALIVE_CELLS = 0.4
SIZE_X = 50
SIZE_Y = 50
NB_GEN = 50  # nb of generation we are going to calculate.


def init_grid(coll):
    coll.delete_many({})
    coll.insert_one({})  # Create an empty doc in the collection for our init aggregation pipeline
    pipeline = [
        {
            '$set': {
                'x': {
                    '$range': [
                        0, SIZE_X
                    ]
                },
                'y': {
                    '$range': [
                        0, SIZE_Y
                    ]
                }
            }
        }, {
            '$unwind': {
                'path': '$x'
            }
        }, {
            '$unwind': {
                'path': '$y'
            }
        }, {
            '$set': {
                'alive': {
                    '$lt': [
                        {
                            '$rand': {}
                        }, START_RATIO_ALIVE_CELLS
                    ]
                }
            }
        }, {
            '$project': {
                '_id': 0
            }
        }, {
            '$out': COLL
        }
    ]
    start = time()
    coll.aggregate(pipeline)
    coll.create_index([('alive', ASCENDING), ('x', ASCENDING), ('y', ASCENDING)])
    print('Grid init done in', round(time() - start, 2), 's')


def next_generation(coll):
    pipeline = [
        {
            '$lookup': {
                'from': 'coll',
                'let': {
                    'id': '$_id',
                    'xx': '$x',
                    'yy': '$y',
                    'aa': '$alive'
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {
                                        '$ne': [
                                            '$_id', '$$id'
                                        ]
                                    }, {
                                        '$eq': [
                                            '$alive', True
                                        ]
                                    }, {
                                        '$lte': [
                                            '$x', {
                                                '$add': [
                                                    '$$xx', 1
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$lte': [
                                            '$y', {
                                                '$add': [
                                                    '$$yy', 1
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$gte': [
                                            '$x', {
                                                '$add': [
                                                    '$$xx', -1
                                                ]
                                            }
                                        ]
                                    }, {
                                        '$gte': [
                                            '$y', {
                                                '$add': [
                                                    '$$yy', -1
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }, {
                        '$count': 'nb_neighbours_alive'
                    }
                ],
                'as': 'neighbours'
            }
        }, {
            '$replaceRoot': {
                'newRoot': {
                    '$mergeObjects': [
                        {
                            '$arrayElemAt': [
                                '$neighbours', 0
                            ]
                        }, '$$ROOT'
                    ]
                }
            }
        }, {
            '$addFields': {
                'alive': {
                    '$switch': {
                        'branches': [
                            {
                                'case': {
                                    '$and': [
                                        {
                                            '$eq': [
                                                '$alive', True
                                            ]
                                        }, {
                                            '$in': [
                                                '$nb_neighbours_alive', [
                                                    2, 3
                                                ]
                                            ]
                                        }
                                    ]
                                },
                                'then': True
                            }, {
                                'case': {
                                    '$and': [
                                        {
                                            '$eq': [
                                                '$alive', False
                                            ]
                                        }, {
                                            '$eq': [
                                                '$nb_neighbours_alive', 3
                                            ]
                                        }
                                    ]
                                },
                                'then': True
                            }
                        ],
                        'default': False
                    }
                }
            }
        }, {
            '$project': {
                'neighbours': 0,
                'nb_neighbours_alive': 0,
                'x': 0,
                'y': 0
            }
        }, {
            '$merge': {
                'into': 'coll',
                'on': '_id',
                'whenMatched': 'merge',
                'whenNotMatched': 'fail'
            }
        }
    ]
    start = time()
    coll.aggregate(pipeline)
    print('New generation calculated in', round(time() - start, 2), 's')


def check_mongodb_uri():
    if len(sys.argv) != 2:
        print('MongoDB URI is missing in cmd line arg 1.')
        exit(1)


def get_mongodb_client(uri):
    return MongoClient(uri)


if __name__ == '__main__':
    check_mongodb_uri()
    client = get_mongodb_client(sys.argv[1])
    collection = client.get_database(DB).get_collection(COLL)
    init_grid(collection)
    for _ in range(NB_GEN):
        input('Hit Enter for the next generation...')
        next_generation(collection)
