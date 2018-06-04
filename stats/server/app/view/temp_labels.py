# Copyright (c) 2017 Deepen.AI Inc.
#
# Confidential and Proprietary Information of Deepen.AI, Inc.
# Use, disclosure, or reproduction is prohibited without
# written permission from Deepen.AI, Inc.

import logging

UNLABELED = {'color': [0, 0, 0], 'text': 'unlabeled', 'category': 'void', 'client_ids': ["zippy"], 'depth_type': "background"}
EGO_VEHICLE = {'color': [0, 0, 0], 'text': 'ego vehicle', 'category': 'void'}
RECTIFICATION_BORDER = {'color': [0, 0, 0], 'text': 'rectification border', 'category': 'void'}
OUT_OF_ROI = {'color': [0, 0, 0], 'text': 'out of roi', 'category': 'void'}
STATIC = {'color': [0, 0, 0], 'text': 'static', 'category': 'void'}
DYNAMIC = {'color': [0, 74, 111], 'text': 'dynamic', 'category': 'void'}
GROUND = {'color': [81, 0, 81], 'text': 'ground', 'category': 'void'}
ROAD = {'color': [128, 64, 128], 'text': 'road', 'category': 'flat',
        'client_ids': ["samsung", "autox"], 'depth_type': "background"}
SPEEDBUMP = {'color': [0, 64, 128], 'text': 'speed bump', 'category': 'flat'}
SIDEWALK = {
    'color': [232, 35, 244], 'text': 'sidewalk', 'category': 'flat',
    'client_ids': ["zippy", "deepscale"], 'depth_type': "background",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}
CURB = {'color': [180, 45, 180], 'text': 'curb', 'category': 'flat',
        'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
PARKING = {'color': [160, 170, 250], 'text': 'parking', 'category': 'flat',
           'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
RAIL_TRACK = {'color': [140, 150, 230], 'text': 'rail track', 'category': 'flat',
              'client_ids': ["zippy"], 'depth_type': "background"}
BUILDING = {'color': [70, 70, 70], 'text': 'building', 'category': 'construction',
            'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
WALL = {'color': [156, 102, 102], 'text': 'wall', 'category': 'construction'}
FENCE = {'color': [153, 153, 190], 'text': 'fence', 'category': 'construction',
         'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
GUARD_RAIL = {'color': [180, 165, 180], 'text': 'guard rail', 'category': 'construction',
              'client_ids': ["zippy"], 'depth_type': "background"}
BRIDGE = {'color': [100, 100, 150], 'text': 'bridge', 'category': 'construction'}
TUNNEL = {'color': [90, 120, 150], 'text': 'tunnel', 'category': 'construction'}
POLE = {'color': [153, 153, 153], 'text': 'pole', 'category': 'object',
        'client_ids': ["zippy", "mapillary", "democlient"], 'depth_type': "foreground"}
GUTTER = {'color': [160, 120, 200], 'text': 'gutter', 'category': 'flat',
          'client_ids': ["zippy"], 'depth_type': "background"}
PARKING_LOT = {'color': [160, 170, 240], 'text': 'parking lot', 'category': 'flat',
               'client_ids': [

               ], 'depth_type': "foreground"}
POLEGROUP = {'color': [153, 153, 153], 'text': 'polegroup', 'category': 'object'}
TRAFFIC_LIGHT = {
    'color': [30, 170, 250],
    'text': 'traffic light',
    'category': 'object',
    'client_ids': ["zippy", "mapillary", "marble", "democlient"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
TRAFFIC_SIGN = {'color': [0, 220, 220], 'text': 'traffic sign', 'category': 'object',
                'client_ids': ["zippy"], 'depth_type': "foreground"}
VEGETATION = {'color': [35, 142, 107], 'text': 'vegetation', 'category': 'nature'}
TERRAIN = {'color': [152, 251, 152], 'text': 'terrain', 'category': 'nature', 'client_ids': ["democlient"]}
SKY = {'color': [180, 130, 70], 'text': 'sky', 'category': 'sky',
       'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
PERSON = {
    'color': [60, 20, 220],
    'text': 'person',
    'category': 'human',
    'client_ids': ["zippy", "marble", "democlient", "starsky"],
    'depth_type': "foreground",
    "default_label_client_ids": ["zippy", "democlient"],
    "client_config": {
        "marble": {
            "features": ["polygon"]
        },
        "starsky": {
            "features": ["box", "direction", "occlusion_state", "vehicle_view"]
        }
    }
}

REGULAR_PERSON = {'color': [65, 80, 230], 'text': 'regular person', 'category': 'human',
                  'client_ids': ["samsung"], 'depth_type': "foreground", "default_label_client_ids": ["samsung"],
                  "class": 0}
IGNORE_PERSON = {'color': [60, 80, 197], 'text': 'ignore person', 'category': 'human',
                 'client_ids': ["samsung"], 'depth_type': "foreground", "class": 0}
SITTING_PERSON = {'color': [89, 80, 197], 'text': 'sitting person', 'category': 'human',
                  'client_ids': ["samsung"], 'depth_type': "foreground", "class": 0}
GROUP_OF_PERSONS = {'color': [85, 125, 233], 'text': 'group of persons', 'category': 'human',
                    'client_ids': ["samsung"], 'depth_type': "foreground", "class": 0}
PERSON_WITH_PET = {'color': [75, 151, 233], 'text': 'person with pet', 'category': 'human',
                   'client_ids': ["samsung"], 'depth_type': "foreground", "class": 0}
RIDER = {'color': [0, 0, 255], 'text': 'rider', 'category': 'human'}
CAR = {'color': [142, 0, 0],
       'text': 'car',
       'category': 'vehicle',
       'client_ids': ["zippy", "samsung", "deepscale", "marble", "starsky", "democlient", "ponyai", "autox"],
       'depth_type': "foreground",
       "class": 1,
       "default_label_client_ids": ["deepscale", "marble", "starsky", "ponyai", "autox"],
       "client_config": {
           "starsky": {
               "features": ["box", "direction", "occlusion_state"],
               "color": [0, 255, 0]
           },
           "deepscale": {
               "features": ["box", "occlusion_percent", "location"],
           },
           "marble": {
               "features": ["polygon"]
           },
           "ponyai": {
               "features": ["box", "interpolated_boxes"]
           }

       }
       }
CAR_LARGE = {'color': [240, 0, 69], 'text': 'car large', 'category': 'vehicle',
             'client_ids': ["ponyai"], 'depth_type': "foreground", "class": 1,
             "client_config": {"ponyai": {"features": ["box", "interpolated_boxes"]}}}
TRAFFIC_CONE = {'color': [200, 100, 36], 'text': 'traffic cone', 'category': 'object',
                'client_ids': ["ponyai", "starsky"], 'depth_type': "foreground", "class": 1,
                "client_config":
                    {"ponyai": {"features": ["box", "interpolated_boxes"]},
                     "starsky": {"features": ["box", "direction", "occlusion_state"]}
                     }}
CONSTRUCTION_SIGN = {
    'color': [20, 100, 67],
    'text': 'construction sign',
    'category': 'object',
    'client_ids': ["ponyai"],
    'depth_type': "foreground",
    "class": 1,
    "client_config": {"ponyai": {"features": ["box", "interpolated_boxes"]}}}
TRUCK = {'color': [70, 0, 0],
         'text': 'truck',
         'category': 'vehicle',
         'client_ids': ["zippy", "samsung", "deepscale", "marble", "starsky", "democlient"],
         'depth_type': "foreground",
         "class": 1,
         "client_config": {
             "starsky": {
                 "features": ["box", "direction", "occlusion_state"],
                 "color": [0, 0, 255]
             },
             "deepscale": {
                 "features": ["box", "occlusion_percent", "location"],
             },
             "marble": {
                 "features": ["polygon"]
             }
         }
         }
BUS = {
    'color': [100, 60, 0],
    'text': 'bus',
    'category': 'vehicle',
    'client_ids': ["zippy", "samsung", "deepscale", "marble", "democlient"],
    'depth_type': "foreground",
    "class": 1,
    "client_config": {
        "marble": {
            "features": ["polygon"]
        },
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"],
        }
    }
}

CARAVAN = {'color': [90, 0, 0], 'text': 'caravan', 'category': 'vehicle',
           'client_ids': ["samsung"], 'depth_type': "foreground", "class": 1}
VEHICLE = {'color': [90, 60, 0], 'text': 'vehicle', 'category': 'vehicle',
           'client_ids': ["zippy", "zippynew"], 'depth_type': "foreground", "class": 1,
           'default_label_client_ids': ["zippynew"]}
IGNORE_VEHICLE = {'color': [90, 60, 24], 'text': 'ignore vehicle', 'category': 'vehicle',
                  'client_ids': ["samsung"], 'depth_type': "foreground", "class": 1}
TRAILER = {
    'color': [45, 20, 0],
    'text': 'trailer',
    'category': 'vehicle',
    'client_ids': ["deepscale"],
    'depth_type': "foreground",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}
TRAIN = {'color': [100, 80, 0], 'text': 'train', 'category': 'vehicle',
         'client_ids': ["zippy", "samsung", "democlient"], 'depth_type': "foreground", "class": 1}
MOTORCYCLE = {
    'color': [230, 0, 0],
    'text': 'motorcycle',
    'category': 'vehicle',
    'client_ids': ["zippy", "samsung", "deepscale", "marble", "democlient", "starsky"],
    'depth_type': "foreground",
    "class": 1,
    "client_config": {
        "marble": {
            "features": ["polygon"]
        },
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        },
        "starsky": {
            "features": ["box", "direction", "occlusion_state"]
        }
    }
}
BICYCLE = {
    'color': [32, 11, 119],
    'text': 'bicycle',
    'category': 'vehicle',
    'client_ids': ["zippy", "samsung", "marble", "democlient", "starsky"],
    'depth_type': "foreground",
    "class": 1,
    "client_config": {
        "marble": {
            "features": ["polygon"]
        },
        "starsky": {
            "features": ["box", "direction", "occlusion_state"]
        }
    }
}
LICENSE_PLATE = {'color': [142, 0, 0], 'text': 'license plate', 'category': 'vehicle'}
GROUP_OF_VEHICLES = {'color': [140, 85, 24], 'text': 'group of vehicles', 'category': 'vehicle',
                     'client_ids': ["samsung"], 'depth_type': "foreground", "class": 1}
PET = {'color': [112, 211, 45], 'text': 'pet', 'category': 'object',
       'client_ids': ["samsung"], 'depth_type': "foreground", "class": 0}
STROLLER = {
    'color': [68, 11, 119],
    'text': 'stroller',
    'category': 'vehicle',
    'client_ids': ["samsung", "marble"],
    'depth_type': "foreground",
    "class": 0,
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
ANIMAL = {'color': [150, 211, 45], 'text': 'animal', 'category': 'object',
          'client_ids': ["zippy", "democlient"], 'depth_type': "foreground"}
STOP_TRAFFIC_SIGN = {'color': [0, 0, 127], 'text': 'stop traffic sign', 'category': 'object',
                     'client_ids': ["zippy"], 'depth_type': "foreground"}
STOP_SIGN = {
    'color': [0, 0, 127],
    'text': 'stop sign',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
YIELD_SIGN = {
    'color': [20, 30, 127],
    'text': 'yield sign',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
OTHER_OBJECT = {
    'color': [226, 137, 25],
    'text': 'other object',
    'category': 'object',
    'client_ids': ["zippy", "starsky"],
    'depth_type': "foreground",
    "client_config": {
        "starsky": {
            "features": ["box", "direction", "occlusion_state"]
        }
    }
}
OBJECT = {'color': [37, 235, 186], 'text': 'object', 'category': 'object',
          'client_ids': ["zippynew"], 'depth_type': "foreground"}
FURNITURE = {'color': [255, 235, 186], 'text': 'furniture', 'category': 'object',
             'client_ids': ["zippy"], 'depth_type': "foreground"}
TABLE = {'color': [230, 235, 186], 'text': 'table', 'category': 'object',
         'client_ids': ["zippy"], 'depth_type': "foreground"}
CHAIR = {'color': [106, 57, 91], 'text': 'chair', 'category': 'object',
         'client_ids': ["zippy"], 'depth_type': "foreground"}
SUITCASE = {
    'color': [69, 57, 91],
    'text': 'suitcase',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
WHEELCHAIR = {
    'color': [108, 57, 91],
    'text': 'wheel chair',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}

PEOPLE = {'color': [91, 145, 24], 'text': 'people', 'category': 'human',
          'client_ids': ["zippynew"], 'depth_type': "foreground"}

ROAD_LANE = {'color': [83, 21, 238], 'text': 'road lane', 'category': 'flat',
             'client_ids': ["zippy", "democlient"], 'depth_type': "background"}
BIKE_LANE = {'color': [230, 186, 235], 'text': 'bike lane', 'category': 'flat',
             'client_ids': ["zippy"], 'depth_type': "background"}
GRASS = {'color': [0, 128, 0], 'text': 'grass', 'category': 'flat',
         'client_ids': ["zippy"], 'depth_type': "background"}
TREES = {'color': [60, 179, 113], 'text': 'trees', 'category': 'flat',
         'client_ids': ["zippy"], 'depth_type': "background"}
BUSH = {'color': [70, 190, 60], 'text': 'bush', 'category': 'flat',
        'client_ids': ["zippy"], 'depth_type': "background"}
TRAVERSABLE_SPACE = {'color': [100, 10, 63], 'text': 'traversable space', 'category': 'flat',
                     'client_ids': ["zippy", "zippynew"], 'depth_type': "background"}
UN_TRAVERSABLE_SPACE = {'color': [10, 21, 195], 'text': 'un traversable space', 'category': 'flat',
                        'client_ids': ["zippy", "zippynew"], 'depth_type': "background"}
SHOPPING_CART = {
    'color': [95, 179, 113],
    'text': 'shopping cart',
    'category': 'vehicle',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}

BILLBOARD = {'color': [140, 50, 153], 'text': 'billboard', 'category': 'object',
             'client_ids': ["mapillary"], 'depth_type': "foreground"}
UNPAVED_DRIVABLE_ROAD = {'color': [154, 64, 128], 'text': 'unpaved drivable road', 'category': 'flat',
                         'client_ids': ["mapillary"], 'depth_type': "foreground"}
CCTV_CAMERA = {'color': [56, 153, 153], 'text': 'cctv-camera', 'category': 'object',
               'client_ids': ["mapillary"], 'depth_type': "foreground"}
WATER_VALVE = {'color': [90, 165, 153], 'text': 'water valve', 'category': 'object',
               'client_ids': ["mapillary"], 'depth_type': "foreground"}
WATER = {'color': [181, 195, 200], 'text': 'water', 'category': 'object',
         'client_ids': ["zippy"], 'depth_type': "background"}
BIRD = {
    'color': [110, 211, 45],
    'text': 'bird',
    'category': 'object',
    'client_ids': ["mapillary", "marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
DOG = {
    'color': [98, 100, 45],
    'text': 'dog',
    'category': 'object',
    'client_ids': ["mapillary", "marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
LANE_MARKING_CROSSWALK = {'color': [255, 255, 255], 'text': 'lane marking-crosswalk', 'category': 'flat',
                          'client_ids': ["mapillary", "zippy"], 'depth_type': "foreground"}
LANE_MARKING_STOP_LINE = {'color': [0, 255, 255], 'text': 'lane marking-stop line', 'category': 'flat',
                          'client_ids': ["mapillary"], 'depth_type': "foreground"}
PARKING_SIGN = {'color': [174, 153, 153], 'text': 'parking sign', 'category': 'object',
                'client_ids': ["mapillary"], 'depth_type': "foreground"}

TRAFFIC_LIGHT_PEDESTRIANS = {'color': [36, 192, 250], 'text': 'traffic light-pedestrians', 'category': 'object',
                             'client_ids': ["mapillary"], 'depth_type': "foreground"}
WALK_SIGNAL = {
    'color': [165, 145, 153],
    'text': 'walk signal',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
TRAFFIC_LIGHT_CYCLISTS = {'color': [80, 170, 250], 'text': 'traffic light-cyclists', 'category': 'object',
                          'client_ids': ['mapillary'], 'depth_type': "foreground"}
PEDESTRIAN = {
    'color': [68, 20, 220], 'text': 'pedestrian', 'category': 'human',
    'client_ids': ["mapillary", "deepscale", "ponyai"], 'depth_type': "foreground",
    "default_label_client_ids": ["mapillary"],
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        },
        "ponyai": {
            "features": ["box", "interpolated_boxes"]
        }
    }
}

PEDESTRIAN_CROSSWALK_SIGN = {
    'color': [0, 128, 128],
    'text': 'pedestrian crosswalk sign',
    'category': 'object',
    'client_ids': ["marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        }
    }
}
JUNCTION_BOX = {'color': [25, 153, 153], 'text': 'junction box', 'category': 'object',
                'client_ids': ["mapillary"], 'depth_type': "foreground"}
PARKING_METER = {'color': [185, 170, 250], 'text': 'parking meter', 'category': 'flat',
                 'client_ids': ["mapillary"], 'depth_type': "background"}

PICKUP = {
    'color': [142, 45, 20], 'text': 'pickup', 'category': 'vehicle',
    'client_ids': ["deepscale"], 'depth_type': "foreground",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}
RV = {
    'color': [142, 70, 0], 'text': 'rv', 'category': 'vehicle',
    'client_ids': ["deepscale"], 'depth_type': "foreground",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}
CYCLIST = {
    'color': [65, 11, 119], 'text': 'cyclist', 'category': 'vehicle',
    'client_ids': ["deepscale", "ponyai"], 'depth_type': "foreground",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        },
        "ponyai": {
            "features": ["box", "interpolated_boxes"]
        }

    }
}
DRONE = {'color': [25, 91, 153], 'text': 'drone', 'category': 'object',
                'client_ids': ["airspace"], 'depth_type': "foreground",
         "default_label_client_ids": ["airspace"],
         "client_config": {
        "airspace": {
            "features": ["box"]}
                          }
         }
DONT_CARE = {
    'color': [145, 235, 186],
    'text': 'dont care',
    'category': 'object',
    'client_ids': ["deepscale", "marble"],
    'depth_type': "foreground",
    "client_config": {
        "marble": {
            "features": ["polygon"]
        },
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}
MULTIPLE = {
    'color': [56, 235, 186], 'text': 'multiple', 'category': 'object',
    'client_ids': ["deepscale"], 'depth_type': "foreground",
    "client_config": {
        "deepscale": {
            "features": ["box", "occlusion_percent", "location"]
        }
    }
}

LANE_WHITE_SINGLE_SOLID = {'color': [255, 255, 255], 'text': 'white single solid', 'category': 'lane',
                           'client_ids': ["samsung", "starsky", "democlient", "autox"]}
LANE_WHITE_SINGLE_BROKEN = {'color': [255, 255, 255], 'text': 'white single broken', 'category': 'lane',
                            'client_ids': ["samsung", "starsky", "democlient", "autox"]}
LANE_WHITE_DOUBLE_SOLID = {'color': [255, 255, 255], 'text': 'white double solid', 'category': 'lane',
                           'client_ids': ["samsung", "starsky", "democlient"]}
LANE_YELLOW_DOUBLE_SOLID = {'color': [0, 255, 255], 'text': 'yellow double solid', 'category': 'lane',
                            'client_ids': ["samsung", "starsky"]}
LANE_YELLOW_DOUBLE_LEFT_BROKEN = {'color': [0, 255, 255], 'text': 'yellow double left broken',
                                  'category': 'lane',
                                  'client_ids': ["samsung", "starsky"]}
LANE_YELLOW_DOUBLE_RIGHT_BROKEN = {'color': [0, 255, 255], 'text': 'yellow double right broken',
                                   'category': 'lane',
                                   'client_ids': ["samsung", "starsky"]}
LANE_YELLOW_SINGLE_SOLID = {'color': [0, 255, 255], 'text': 'yellow single solid', 'category': 'lane',
                            'client_ids': ["samsung", "starsky", "autox"]}
LANE_END_OF_LANE = {'color': [255, 255, 255], 'text': 'end of lane', 'category': 'lane',
                    'client_ids': ["samsung", "starsky"]}
LANE_YELLOW_SINGLE_BROKEN = {'color': [0, 255, 255], 'text': 'yellow single broken', 'category': 'lane',
                             'client_ids': ["starsky", "autox"]}
EDGE_OF_ROAD = {'color': [65, 75, 119], 'text': 'edge of road', 'category': 'lane',
                'client_ids': ["starsky"]}
ALL_LANE_LABELS = [LANE_WHITE_SINGLE_BROKEN,
                   LANE_WHITE_SINGLE_SOLID,
                   LANE_WHITE_DOUBLE_SOLID,
                   LANE_YELLOW_SINGLE_SOLID,
                   LANE_YELLOW_DOUBLE_SOLID,
                   LANE_YELLOW_DOUBLE_LEFT_BROKEN,
                   LANE_YELLOW_DOUBLE_RIGHT_BROKEN,
                   LANE_YELLOW_SINGLE_BROKEN,
                   LANE_END_OF_LANE,
                   LANE_MARKING_CROSSWALK,
                   LANE_MARKING_STOP_LINE, EDGE_OF_ROAD]

ALL_MASK_LABELS = [UNLABELED,  # EGO_VEHICLE, RECTIFICATION_BORDER, OUT_OF_ROI, STATIC,
                   DYNAMIC,
                   GROUND,
                   ROAD,
                   SPEEDBUMP,
                   CURB,
                   SIDEWALK,
                   PARKING,
                   RAIL_TRACK,
                   BUILDING,
                   WALL,
                   FENCE,
                   GUARD_RAIL,
                   BRIDGE,
                   TUNNEL,
                   POLE,  # POLEGROUP,
                   TRAFFIC_LIGHT,
                   TRAFFIC_SIGN,
                   VEGETATION,
                   TERRAIN,
                   SKY,
                   PERSON,
                   REGULAR_PERSON,
                   SITTING_PERSON,
                   IGNORE_PERSON,
                   GROUP_OF_PERSONS,
                   PERSON_WITH_PET,
                   RIDER,
                   CAR,
                   TRUCK,
                   BUS,
                   CARAVAN,
                   DRONE,
                   TRAILER,
                   TRAIN,
                   MOTORCYCLE,
                   IGNORE_VEHICLE,
                   BICYCLE,
                   LICENSE_PLATE, ANIMAL, STOP_TRAFFIC_SIGN, ROAD_LANE, BIKE_LANE, GRASS, TABLE, CHAIR, TREES,
                   OTHER_OBJECT, GROUP_OF_VEHICLES,
                   STROLLER, PET, BILLBOARD, UNPAVED_DRIVABLE_ROAD, CCTV_CAMERA, WATER_VALVE, BIRD, PARKING_SIGN,
                   TRAFFIC_LIGHT_PEDESTRIANS,
                   TRAFFIC_LIGHT_CYCLISTS, PEDESTRIAN, JUNCTION_BOX, PARKING_METER, PICKUP, RV, CYCLIST, DONT_CARE,
                   MULTIPLE, WHEELCHAIR,
                   SHOPPING_CART, SUITCASE, STOP_SIGN, YIELD_SIGN, PEDESTRIAN_CROSSWALK_SIGN, WALK_SIGNAL, GUTTER,
                   PARKING_LOT, WATER, BUSH, VEHICLE, TRAVERSABLE_SPACE, UN_TRAVERSABLE_SPACE, DOG,
                   CAR_LARGE, CONSTRUCTION_SIGN, TRAFFIC_CONE, OBJECT, PEOPLE]
ALL_LABELS = ALL_LANE_LABELS + ALL_MASK_LABELS


def get_label_for_text(label_text):
    all_labels = ALL_LABELS
    for label in all_labels:
        if label["text"] == label_text:
            return label
    logging.info("Not able to find label for text " + label_text)
    return None


def all_client_ids():
    client_ids = set()
    for label in ALL_LABELS:
        if label.get("client_ids") is not None:
            client_ids.update(label.get("client_ids"))
    return client_ids


def get_label_class(lebel_text):
    all_labels = ALL_LABELS
    for label in all_labels:
        if label["text"] == lebel_text:
            return label["class"]


class LabelManager(object):
    def __init__(self, file_manager, client_id):
        self.file_manager = file_manager
        self.client_id = client_id
        self.current_label = self.get_default_label(self.client_id)
        self.current_label_id = self.get_default_label_id()
        self.refresh()

    def set_current_label(self, label_text):
        self.current_label = get_label_for_text(label_text)

    def get_current_label_color(self):
        return self.get_color(self.current_label)

    def get_next_label_id(self, label_text, instance_mask=None, instance_mask2=None):
        label_ids = self.get_label_ids(instance_mask, label_text)
        label_ids.update(self.get_label_ids(instance_mask2, label_text))

        label_ids_integers = [int(x.split(":")[1]) for x in label_ids]
        if len(label_ids_integers) > 0:
            return label_text + ":" + str(max(label_ids_integers) + 1)
        else:
            return label_text + ":1"

    def set_current_label_id(self, label_id):
        self.current_label_id = label_id

    def all_labels(self):
        if self.client_id is None:
            return ALL_LABELS
        else:
            labels = []
            for label in ALL_LABELS:
                if label.get("client_ids") is not None and self.client_id in label.get("client_ids"):
                    labels.append(label)
            return labels

    def get_features(self, label=None):
        if label == None:
            label = self.current_label
        if self.client_id is not None and \
                label.get("client_config") is not None and label["client_config"].get(self.client_id) is not None \
                and label["client_config"][self.client_id].get("features") is not None:
            features = label["client_config"][self.client_id].get("features")
            return features
        if label["category"] == "lane":
            return ["lane"]
        elif label.get("depth_type") == "background":
            return ["mask", "polygon"]
        else:
            return ["mask", "box", "polygon"]

    def get_color(self, label):
        if self.client_id is not None and \
                label.get("client_config") is not None and label["client_config"].get(self.client_id) is not None \
                and label["client_config"][self.client_id].get("color") is not None:
            return label["client_config"][self.client_id].get("color")
        return label["color"]

    def is_background(self, label):
        return label["depth_type"] == "background"

    def add_label_id(self, label, label_id):
        if self.label_ids.get(label["text"]) is None:
            self.label_ids[label["text"]] = set()
        self.label_ids[label["text"]].add(label_id)

    def delete_label_id(self, label, label_id):
        if self.label_ids.get(label["text"]) is not None:
            self.label_ids[label["text"]].remove(label_id)

    def refresh(self):
        image_paths = self.file_manager.image_paths()
        all_label_texts = [x["text"] for x in self.all_labels()]
        all_instance_masks = [self.file_manager.read_instance_mask(image_path)
                              for image_path in image_paths]
        all_instance_masks = [x for x in all_instance_masks if x]
        label_ids = {}

        for label_text in all_label_texts:
            label_ids_for_label_text = set()
            label_ids_for_label_text.add("all")
            for instance_mask in all_instance_masks:
                label_ids_for_label_text.update(self.get_label_ids(instance_mask, label_text))
            label_ids[label_text] = label_ids_for_label_text
        self.label_ids = label_ids

    def get_default_label(self, unused_client_id=None):
        for label in ALL_LABELS:
            if label.get("default_label_client_ids") and self.client_id in label.get("default_label_client_ids"):
                return label
        return ROAD

    def get_all_label_ids(self, label_text=None, instance_mask=None):
        if label_text is None:
            label_text = self.current_label["text"]
        if self.label_ids.get(label_text) is None:
            self.label_ids[label_text] = set()
            self.label_ids[label_text].add("all")
        if instance_mask is not None and instance_mask.get(label_text) is not None:
            self.label_ids[label_text] = \
                self.label_ids[label_text].union(self.get_label_ids(instance_mask, label_text))
        return self.label_ids[label_text]

    def get_default_label_id(self):
        return "all"

    def validate_label(self, label_text, label_id_num):
        try:
            label_id_num = int(label_id_num)
            if label_id_num <= 0:
                return "Invalid label id number " + str(label_id_num)
        except ValueError:
            return "Invalid label id number " + str(label_id_num)

        for label in self.all_labels():
            if label_text == label['text']:
                return ""

        return "Invalid label text " + str(label_text)

    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def get_label_ids(self, instance_mask, label_text):
        label_ids = set()
        if instance_mask is not None and instance_mask.get(label_text) is not None:
            label_ids.update([x for x in instance_mask[label_text].keys()
                              if instance_mask[label_text][x]])
        return label_ids