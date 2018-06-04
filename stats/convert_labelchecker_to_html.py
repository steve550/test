#convert label_checker output (json) to html
import os, sys
import argparse
import json

import numpy as np
import cv2
import operator

from dominate import document
from dominate.tags import *
from dominate.util import text

import re

def get_severity_score(severity_score):
    tuples_of_severity_score = severity_score.items()
    severity_score_sorted = sorted(tuples_of_severity_score, key=operator.itemgetter(1))
    return severity_score_sorted


#def get_result_in_html(file1, file2, final_result, severity_score, sequence, html_files, is_semantic):
def get_result_in_html(img_path, file1, file2, ground_truth, predicted, final_result, severity_score, is_semantic, summary, is_polygon, html_files, sequence, wrong_label):
    severity_score = get_severity_score(severity_score)

    low_priority_result = []  # related to background, print in last

    if(is_polygon):
        original_file = img_path + file2
    else:
        original_file = img_path + file1

    #file1 = file1.split("/")
    #file2 = file2.split("/")

    filename = "Results_" + file1 + file2

    missing_image = ""
    extraBB_image = ""

    if(len(html_files) > 0):
        previous = ""
        next = ""
        # link to next and previous files
        if (sequence > 0):
            previous = html_files[sequence - 1] + ".html"
        if (len(html_files) > sequence + 1):
            next = html_files[sequence + 1] + ".html"


    with document(title=filename) as doc:
        if not (previous == ""):
            a('Previous', href=previous)
        if not (next == ""):
            a('Next', href=next)

        h1("file1:" + file1)
        if(file2 != ""):
            h1("file2:" + file2)
        h4("______________________________________________________________________")
        h4("Original image")
        div(img(src=original_file), _class='photo')

        h4("_______________________________________________________________________")
        h4("Summary")
        # print summary here
        list = ul()
        for keys in summary:
            if (keys == 'wrong id' and not (is_polygon)):
                list += li("wrong label" + ' = ', summary[keys])

            elif(keys == 'missing bounding box'):
                list += li("wrong bounding box size" + ' = ', summary[keys])

            else:
                list += li(keys + ' = ', summary[keys])

        h4("________________________________________________________________________")
        h4("Results")
        for keys, values in severity_score:
            if (is_semantic and (":" not in keys)):
                low_priority_result.append(keys)

            else:
                h4(keys + " - " + final_result[keys])
                if(values != ''):
                    human_readible_score = (1 - values) * 100

                    h4("severity score: " + str(round(human_readible_score, 1)) + "%")
                key = keys.split(":")
                text("Labeled output")
                if(is_polygon):
                    check_metric(original_file, ground_truth[keys], predicted[keys], keys, False)
                    div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                    text("Expected output")
                    div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                else:
                    visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                    div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                    text("Expected output")
                    div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')

        for keys, values in final_result.items():
            if(is_polygon):
                if (values == "missing polygon"):
                    h4(keys + " - " + values)
                    key = keys.split(":")
                    if (is_semantic and (":" not in keys)):
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, is_semantic)
                        text("Labeled output")
                        div(img(src='groundtruth' + keys + '_' + str(sequence) + '.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                    else:
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, False)
                        #keys = keys.split(":")
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) + '.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) + '.jpg'), _class='photo')

            elif(values == "missing bounding box"):
                h4(keys + " - " + "wrong bounding box size")
                key = keys.split(":")
                visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                text("Labeled output")
                div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) + '.jpg'), _class='photo')
                text("Expected output")
                div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) + '.jpg'), _class='photo')


        for keys, values in final_result.items():
            if (values == "wrong id"):
                key = keys.split(":")
                if (is_polygon):
                    h4(keys + " - " + values)
                    if (is_semantic and (":" not in keys)):
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, is_semantic)
                        text("Labeled output")
                        div(img(src='groundtruth' + keys + '_' + str(sequence) + '.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                    else:
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, False)
                        #keys = keys.split(":")
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                else:
                    h4(keys + " - " + "wrong label")
                    if(keys in wrong_label):
                        h5("Labeler labeled: " + keys)
                        h5("Algorithm labeled: " + wrong_label[keys])

                        visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                    else:
                        visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) + '.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')

            if (values == "unclassified"):
                if (is_polygon):
                    h4(keys + " - " + values)
                    key = keys.split(":")
                    if (is_semantic and (":" not in keys)):
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, is_semantic)
                        text("Labeled output")
                        div(img(src='groundtruth' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                    else:
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, False)
                        #keys = keys.split(":")
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                else:
                    if(len(ground_truth[keys]) != 0 and predicted[keys] != 0):
                        h4(keys + " - " + values)
                        visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                    #div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                    #text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
            #===============testing > start
            '''
            if (values == "labeled correctly"):
                h4(keys + " - " + values)
                key = keys.split(":")
                if (is_polygon):
                    if (is_semantic and (":" not in keys)):
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, is_semantic)
                        div(img(src='groundtruth' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                        div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                    else:
                        check_metric(original_file, ground_truth[keys], predicted[keys], keys, False)
                        #keys = keys.split(":")
                        text("Labeled output")
                        div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                        text("Expected output")
                        div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                else:
                    visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                    div(img(src='groundtruth' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
                    text("Expected output")
                    div(img(src='predicted' + key[0] + key[1] + '_' + str(sequence) +'.jpg'), _class='photo')
            '''
            #===============================testing > end

            #for missing object and extra bounding box
            if (not (is_polygon) and (values == "missing object" or values == "extra bounding box")):
                if(values == "missing object"):
                    if(missing_image == ""):
                        missing_image = cv2.imread(original_file)

                    missing_image = visualize_BB_for_missing_object_and_extra_BB(missing_image, predicted[keys])
                elif(values == "extra bounding box"):
                    if(extraBB_image == ""):
                        extraBB_image = cv2.imread(original_file)

                    extraBB_image = visualize_BB_for_missing_object_and_extra_BB(extraBB_image, ground_truth[keys])

            elif(is_polygon and values == "missing object"):
                if(missing_image == ""):
                    missing_image = cv2.imread(original_file)

                if(keys in ground_truth):
                    missing_image = draw_missing_object_polygon(missing_image, ground_truth[keys])
                elif(keys in predicted):
                    missing_image = draw_missing_object_polygon(missing_image, predicted[keys])
                #cv2.imshow("img", missing_image)
                #cv2.waitKey()
                #cv2.destroyAllWindows()

        if(missing_image != ""):
            h4("Missing objects")
            cv2.imwrite('missing_object_'+ str(sequence) + '_.jpg', missing_image)
            div(img(src='missing_object_' + str(sequence) + '_.jpg'), _class='photo')
        if (extraBB_image != ""):
            h4("Extra bounding boxes")
            cv2.imwrite('extra_BB_' + str(sequence) + '_.jpg', extraBB_image)
            div(img(src='extra_BB_' + str(sequence) + '_.jpg'), _class='photo')

        '''
        # all low priority results
        severity_score = dict(severity_score)
        for keys in low_priority_result:
            h4(keys + " - " + final_result[keys])
            human_readible_score = (1 - float(severity_score[keys])) * 100
            h4("severity score: " + str(round(human_readible_score, 1)) + "%")

            if(is_polygon):
                check_metric(original_file, ground_truth[keys], predicted[keys], keys, is_semantic)
                text("Labeled output")
                div(img(src='groundtruth' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
                text("Expected output")
                div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
            else:
                visualize_BB(original_file, ground_truth[keys], predicted[keys], keys)
                text("Labeled output")
                div(img(src='groundtruth' + keys + '_' + str(sequence) + '.jpg'), _class='photo')
                text("Expected output")
                div(img(src='predicted' + keys + '_' + str(sequence) +'.jpg'), _class='photo')
        '''
    with open(filename + '.html', 'w') as f:
        f.write(doc.render())
"""
"""
def draw_missing_object_polygon(img, polygons1):
    opacity = 0.7

    cv2.fillPoly(img, np.array([polygons1], dtype=np.int32), (255, 0, 0))
    return img

"""
"""
def check_metric(img, polygons1, polygons2, name, is_semantic):
    img = cv2.imread(img)
    overlay1 = img.copy()
    overlay2 = img.copy()
    opacity = 0.7

    img2 = img.copy()
    #canvas1 = np.zeros(shape, dtype=np.uint8)
    #canvas2 = np.zeros(shape, dtype=np.uint8)

    if (is_semantic):
        for polygon in polygons1:
            cv2.fillPoly(overlay1, np.array([polygon], dtype=np.int32), (0, 255, 0))
        cv2.addWeighted(overlay1, opacity, img, 1 - opacity, 0, img)

        for polygon in polygons2:
            cv2.fillPoly(overlay2, np.array([polygon], dtype=np.int32), (0, 0, 255))
        cv2.addWeighted(overlay2, opacity, img2, 1 - opacity, 0, img2)

        cv2.imwrite('groundtruth' + name + '_' + str(sequence) + '.jpg', img)
        cv2.imwrite('predicted' + name + '_' + str(sequence) + '.jpg', img2)
    else:
        # for polygon in polygons1:
        cv2.fillPoly(overlay1, np.array([polygons1], dtype=np.int32), (0, 255, 0))
        cv2.addWeighted(overlay1, opacity, img, 1 - opacity, 0, img)
        # for polygon in polygons2:
        cv2.fillPoly(overlay2, np.array([polygons2], dtype=np.int32), (0, 0, 255))
        cv2.addWeighted(overlay2, opacity, img2, 1 - opacity, 0, img2)

        name = name.split(":")
        cv2.imwrite('groundtruth' + name[0] + name[1] + '_' + str(sequence) +'.jpg', img)
        cv2.imwrite('predicted' + name[0] + name[1] + '_' + str(sequence) +'.jpg', img2)


def visualize_BB(img, boxT, boxP, name):
    if(os.path.exists(img.encode("utf8"))):
        img1 = cv2.imread(img.encode("utf8"))
        img2 = img1.copy()

        name = name.split(":")

        if(boxT != '' and len(boxT) != 0):
            cv2.rectangle(img1, (int(boxT[0]), int(boxT[1])), (int(boxT[2]) + int(boxT[0]), int(boxT[3]) + int(boxT[1])), (0, 255, 0), 2)
            cv2.imwrite('groundtruth' + name[0] + name[1] +  '_' + str(sequence) + '.jpg', img1)
        if(boxP != '' and len(boxP) != 0):
            cv2.rectangle(img2, (int(boxP[0]), int(boxP[1])), (int(boxP[2]) + int(boxP[0]), int(boxP[3]) + int(boxP[1])), (255, 255, 0), 2)
            cv2.imwrite('predicted' + name[0] + name[1] + '_' + str(sequence) + '.jpg', img2)
    return

def visualize_BB_for_missing_object_and_extra_BB(img, boxT):
    if (boxT != '' and len(boxT) != 0):
        cv2.rectangle(img, (int(boxT[0]), int(boxT[1])), (int(boxT[2]) + int(boxT[0]), int(boxT[3]) + int(boxT[1])), (255, 0, 0), 2)
    return img

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]

def sort_wrt_numbers(list):
    list.sort(key=natural_keys)
    return list

if __name__ == '__main__':
    # parsing arguments from command terminal
    parser = argparse.ArgumentParser(description='Labeling Checker')

    parser.add_argument('-i1',
                        '--img1',
                        dest='img1_file',
                        default = '',
                        help='Enter input image 1')

    parser.add_argument('-i2',
                        '--img2',
                        dest='img2_file',
                        default = '',
                        help='Enter input image 2')

    parser.add_argument('-j',
                        '--json_response',
                        metavar='FILE',
                        dest='json_response',
                        # action = 'store_true',
                        help='Enter json output of label_checker')

    parser.add_argument('-sj',
                        '--summary_json',
                        dest='summary_json',
                        metavar='FILE',
                        default = '',
                        # action = 'store_true',
                        help='Enter json summary of label_checker')

    parser.add_argument('--polygon_enabled', dest='polygon_enabled', action='store_true')
    parser.add_argument('--polygon_disabled', dest='polygon_enabled', action='store_false')
    parser.set_defaults(polygon_enabled=False)

    parser.add_argument('--is_semantic', dest='is_semantic', action='store_true')
    parser.add_argument('--not_semantic', dest='is_semantic', action='store_false')
    parser.set_defaults(is_semantic=False)

#================For batch processing===================================================

    parser.add_argument('--batch_processing', dest='is_batch', action='store_true')
    parser.add_argument('--not_batch_processing', dest='is_batch', action='store_false')
    parser.set_defaults(is_batch=True)

    parser.add_argument('-n',
                        '--image_count',
                        dest='image_count',
                        metavar='N',
                        type=int,
                        help='Enter total number of images')

    parser.add_argument('-p_im',
                        '--path_img',
                        dest='path_img',
                        help='Enter image path')

    args = parser.parse_args()

    if not(args.json_response == ''):
        with open(args.json_response) as json_file:
            json_data = json.load(json_file)

        severity_score = {}
        final_result = {}
        ground_truth = {}
        predicted = {}
        wrong_label = {}

        if not (args.is_batch):
            #calculate severity score
            for type in json_data:
                for object in json_data[type]:
                    if(json_data[type][object] != {}):
                        if(json_data[type][object]['ground truth'] != ''):
                            ground_truth[object] = json_data[type][object]['ground truth']
                        if(json_data[type][object]['predicted']):
                            predicted[object] = json_data[type][object]['predicted']
                        if(json_data[type][object]['severity score'] != ''):
                            severity_score[object] = json_data[type][object]['severity score']
                        if (json_data[type][object]['wrong label'] != ''):
                            wrong_label[object] = json_data[type][object]['wrong label']
                        final_result[object] = type

        else:
            sequence_results = {}
            img_list = []
            for filename in json_data:
                for i in filename:
                    img_list.append(i)
                    sequence_results[i] = filename[i] # img, results

            sorted_image_list = sort_wrt_numbers(img_list)

    else:
        raise "Please insert json_response file"

    html_files = []

    if(args.polygon_enabled):
        for f in sorted_image_list:
            get_ext = args.img1_file.split(".")
            files = f.split("_")
            #file1 = files[0].split(".")
            #file2 = files[1].split(".")
            filename = "Results_" + files[0] + files[-1]
            html_files.append(filename)
    else:
        for f in sorted_image_list[0:]:
            file = f.split(".")
            get_ext = args.img1_file.split(".")
            file = file[0].split("_")
            filename = "Results_" + file[-1] + "." + get_ext[1]
            html_files.append(filename)

    summary = {}
    # parsing summary
    if not(args.summary_json == ''):
        with open(args.summary_json) as json_file:
            json_data = json.load(json_file)

        if(args.is_batch):
            number_of_files = 0
            for type in json_data:
                for files in json_data[number_of_files]:
                    summary[files] = json_data[number_of_files][files]
                    number_of_files += 1

        else:
            for type in json_data:
                summary[type] = json_data[type]
    else:
        raise "Please insert json_summary file"

    # parsing batch file (json_response)
    if(args.is_batch):
        sequence = 0
        for img_json in sorted_image_list:
            img_name = img_json.rsplit(".", 1)
            img_name = img_name[0].split("_")
            img_path = args.path_img + img_name[-1]
            print("---- Working on ", img_path, " ----")

            ground_truth = {}
            predicted = {}
            severity_score = {}
            final_result = {}
            wrong_label = {}

            if(args.polygon_enabled):
                file2 = img_json.split("_")
                img_path = args.path_img + file2[-1]

            if(os.path.exists(img_path)):
                img_results = sequence_results[img_json]
                for type in img_results:
                    if (img_results[type] != {}):
                        for objects in img_results[type]:
                            final_result[objects] = type

                            if (img_results[type][objects] != {}):
                                if (img_results[type][objects]['ground truth'] != ''):
                                    ground_truth[objects.encode("utf8")] = img_results[type][objects]['ground truth']
                                if (img_results[type][objects]['predicted']):
                                    predicted[objects.encode("utf8")] = img_results[type][objects]['predicted']
                                if (img_results[type][objects]['severity score'] != ''):
                                    severity_score[objects.encode("utf8")] = img_results[type][objects]['severity score']
                                if (img_results[type][objects]['wrong label'] != ''):
                                    wrong_label[objects.encode("utf8")] = img_results[type][objects]['wrong label']

            #print("GG", len(ground_truth))
            #print("PP", len(predicted))
            #print("SS", summary[img_json])

            if(args.polygon_enabled): #for polygon
                files = img_json.split("_")
                get_result_in_html(args.path_img, files[0], files[-1], ground_truth, predicted, final_result, severity_score, args.is_semantic,
                                   summary[img_json], args.polygon_enabled, html_files, sequence, wrong_label)
            else: # for BB
                name_of_img = img_json.split(".")
                get_ext = args.img1_file.split(".")
                name_of_img = name_of_img[0] + "." + get_ext[1]
                name_of_img = name_of_img.split("_")

                get_result_in_html(args.path_img, name_of_img[-1], '', ground_truth, predicted, final_result, severity_score,
                                   args.is_semantic, summary[img_json], args.polygon_enabled, html_files, sequence, wrong_label)

            sequence += 1

    else:
        file1_img_without_ext = args.img1_file.split("/")

        if(args.img2_file != ''): #polygon
            file2_img_without_ext = args.img2_file.split("/")
            get_result_in_html('', file1_img_without_ext[-1], file2_img_without_ext[-1], ground_truth, predicted,
                               final_result, severity_score, args.is_semantic, summary, args.polygon_enabled, html_files, 0, wrong_label)
        else: # bb
            get_result_in_html('', file1_img_without_ext[-1], '', ground_truth, predicted, final_result,
                               severity_score, args.is_semantic, summary, args.polygon_enabled, html_files, 0, wrong_label)

    print(">> Completed")