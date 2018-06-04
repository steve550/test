#sending a json input to the server
try:
    import simplejson as json
except:
    import json

import requests

def get_data():
    # sample input for Bounding Box
    input_data = {
        'image_1': "",
        'image_2': "",
        'label_1': "instancemask__FlycaptureCamera-17302268-1197932057481579794.jpg.json",#starting from this image
        'label_2': "",
        'predicted_label': "Zippy_batch4_clip1.json",
        'segmantic_seg': 'off',
        'bounding_box': 'on',
        'image_storage':'deepenstats',
        'image_folder':'DeepScale',
        'private_key_cloud':"/home/marium/storage_key/DeepenAIMain-e00ba37028bf.json",

        'batch_script': 'on',
        'count_of_images': 100,#starting from 0.json and process first 100 images
        'instance_mask_path': "/home/marium/Zippy/outfiles/",
        'manual_labels': ""
    }

    #==========================================
    return input_data

url = 'http://127.0.0.1:8000/label_checker/home/'

headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(get_data()), headers=headers)
r.text

print(">> completed")