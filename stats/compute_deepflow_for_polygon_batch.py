# This code is used to preprocess deepflow for the polygon batch
import argparse
import os, sys
import cv2
from google.cloud import storage
import numpy as np

def get_access_to_cloud(private_key_location, bucket_name):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = private_key_location
    storage_client = storage.Client()

    # get the bucket
    bucket = storage_client.get_bucket(bucket_name)
    return bucket

def get_bucket_of_images(private_key_location, bucket_name, image_folder):
    bucket = get_access_to_cloud(private_key_location, bucket_name)
    blobs = bucket.list_blobs()

    image_list = []
    for folder in blobs:
        get_images = folder.name.rsplit("/", 1)
        if (get_images[0] == image_folder):
            image_list.append(get_images[1])

    return image_list

def cleanup(im1, im2):
    os.remove(im1)
    os.remove(im2)
    return

def get_images_and_convert_into_grey_scale(im1, im2):
    img1 = cv2.imread(im1)
    img2 = cv2.imread(im2)

    #compute grey scale images
    img1_grey = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_grey = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    return img1, img2, img1_grey, img2_grey


def getImages(im1, im2, private_key_location, bucket_name, image_folder):
    bucket = get_access_to_cloud(private_key_location, bucket_name)

    # get the image
    blob1 = bucket.get_blob(image_folder + '/' + im1)
    blob2 = bucket.get_blob(image_folder + '/' + im2)

    img1_file = "img1"
    img2_file = "img2"
    blob1.download_to_filename(img1_file)
    blob2.download_to_filename(img2_file)

    return img1_file, img2_file


def compute_deepflow(im_grey1, im_grey2):
  deep_flow = cv2.optflow.createOptFlow_DeepFlow()
  deepflow = deep_flow.calc(im_grey1, im_grey2, None)
  return deepflow


def write_deepflow_compressed(deepflow_results, filename, dest_folder):
    df_tmp = deepflow_results

    channel0_min = np.amin(df_tmp[:, :, 0])
    channel0_max = np.amax(df_tmp[:, :, 0])

    channel1_min = np.amin(df_tmp[:, :, 1])
    channel1_max = np.amax(df_tmp[:, :, 1])

    channel0_range = channel0_max - channel0_min
    channel1_range = channel1_max - channel1_min

    df_tmp[:, :, 0] = np.round(255.0 * (df_tmp[:, :, 0] - channel0_min) / channel0_range)
    df_tmp[:, :, 1] = np.round(255.0 * (df_tmp[:, :, 1] - channel1_min) / channel1_range)

    df_tmp = df_tmp.astype(np.uint8)

    cv2.imwrite('%s_channel0.jpg' % (dest_folder + filename), df_tmp[:, :, 0])
    cv2.imwrite('%s_channel1.jpg' % (dest_folder + filename), df_tmp[:, :, 1])

    deepflow_datastruct = [channel0_min, channel0_max, channel1_min, channel1_max]

    np.save('%s_scalingcoeff' % (dest_folder + filename), deepflow_datastruct)

def upload_results_on_gcs(path, private_key_location, bucket_name):
    print('Uploading images to GCS')
    bucket = get_access_to_cloud(private_key_location, bucket_name)

    for results in os.listdir(path):
        blob = bucket.blob(results)
        blob.upload_from_file(results)

if __name__ == '__main__':
    # parsing arguments from command terminal
    parser = argparse.ArgumentParser(description='Labeling Checker')

    '''
    parser.add_argument('-i1',
                        '--img1',
                        dest='img1_file',
                        default='',
                        help='Enter input image 1')

    parser.add_argument('-p_im',
                        '--path_img',
                        dest='path_img',
                        help='Enter image path')
    '''

    parser.add_argument('-bucket',
                        '--bucket_img',
                        dest='bucket_name',
                        required=True,
                        help='Enter bucket name of images on cloud')

    parser.add_argument('-key',
                        '--private_key_location',
                        dest='key',
                        required=True,
                        help='Enter location of private key to access cloud')

    parser.add_argument('-img_folder_cloud',
                        '--img_folder_cloud',
                        dest='img_folder_on_cloud',
                        required=True,
                        help='Enter image folder on the cloud')

    parser.add_argument('-dest_folder',
                        '--dest_folder',
                        dest='result_folder',
                        required=True,
                        help='Enter destination folder where results would be saved')

    args = parser.parse_args()

    if(args.bucket_name and args.key and args.img_folder_on_cloud):
        image_list = get_bucket_of_images(args.key, args.bucket_name, args.img_folder_on_cloud)

        # TODO change the length of the dataset
        for i in range(0, len(image_list) - 1):
            if(image_list[i] != ""):
                print('Working on image: %s - %s' %(image_list[i], image_list[i + 1]))
                image1, image2 = getImages(image_list[i], image_list[i + 1], args.key, args.bucket_name, args.img_folder_on_cloud)
                img1, img2, img_grey1, img_grey2 = get_images_and_convert_into_grey_scale(image1, image2)

                deepflow_results = compute_deepflow(img_grey1, img_grey2)

                file1 = image_list[i].encode("utf8").rsplit(".")
                file2 = image_list[i + 1].encode("utf8").rsplit(".")

                write_deepflow_compressed(deepflow_results, file1[0] + '_' + file2[0], args.result_folder)

                #write in npz file
                #flow_file_path = 'outfile_' + file1[0] + '_' + file2[0] + '.npy'
                #np.save(flow_file_path, deepflow_results.astype(np.int8))

        cleanup("img1", "img2")
        #upload_results_on_gcs(args.result_folder, args.key, args.bucket_name)

        '''
        for i in range(0, 3):
            file1 = image_list[i].encode("utf8").rsplit(".")
            file2 = image_list[i + 1].encode("utf8").rsplit(".")
            npzfile = np.load('outfile' + file1[0] + '_' + file2[0] + '.npz')
            print(npzfile.files)
            print(npzfile['deepflow'])
        '''

        print(">> completed")
