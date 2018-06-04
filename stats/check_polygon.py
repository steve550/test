#sending a json input to the server
try:
    import simplejson as json
except:
    import json

import requests

def get_data():
    # sample input for polygon
    input_data = {
        'image_1': "FlycaptureCamera-17302268-1197932057481579794.jpg",
        'image_2': "",
        'label_1': "instancemask__FlycaptureCamera-17302268-1197932057481579794.jpg.json",
        'label_2': "",
        'predicted_label': "",
        'semantic_seg': 'on',
        'bounding_box': 'off',

        'image_storage':'deepenstats',
        'image_folder':'client_images/zippy/Zippy_batch4/Clip1',
        'private_key_cloud': '/home/marium/storage_key/DeepenAIMain-e00ba37028bf.json',

        'batch_script': 'on',
        'count_of_images': 425,
        'instance_mask_path': "/home/marium/Zippy/outfiles/",
        #'deepflow_results_path': "/home/marium/deepentools/stats/"
        'deepflow_results_path_on_cloud': 'Deepflow_results/client_images/Zippy/Batch4/Clip1'
    }
    return input_data

url = 'http://127.0.0.1:8000/label_checker/home/'

headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(get_data()), headers=headers)
r.text

print(">> completed")