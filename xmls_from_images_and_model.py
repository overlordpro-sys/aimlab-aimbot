import xml.etree.cElementTree as ET
import tensorflow as tf
import numpy as np
from PIL import Image
import glob
import cv2
import os

# Make an XML file for an image
def generate_xml(box_array, num_detections, im_width, im_height, inferred_class, file_path):
    file_name = (file_path.split("\\")[1]).split(".")[0]
    try:
        annotation = ET.Element('annotation')
        ET.SubElement(annotation, 'filename').text = file_name + '.png'
        size = ET.SubElement(annotation, 'size')
        ET.SubElement(size, 'width').text = str(im_width)
        ET.SubElement(size, 'height').text = str(im_height)
        ET.SubElement(size, 'depth').text = '3'

        for box in box_array:
            objectBox = ET.SubElement(annotation, 'object')
            ET.SubElement(objectBox, 'name').text = inferred_class
            ET.SubElement(objectBox, 'pose').text = 'Unspecified'
            ET.SubElement(objectBox, 'truncated').text = '0'
            ET.SubElement(objectBox, 'difficult').text = '0'
            bndBox = ET.SubElement(objectBox, 'bndbox')
            ET.SubElement(bndBox, 'xmin').text = str(round(box[1]))
            ET.SubElement(bndBox, 'ymin').text = str(round(box[0]))
            ET.SubElement(bndBox, 'xmax').text = str(round(box[3]))
            ET.SubElement(bndBox, 'ymax').text = str(round(box[2]))

        tree = ET.ElementTree(annotation)

        #If all three targets are not detected, place in separate folder for closer inspection
        if num_detections<3:
            tree.write('./xmls/!three_box/' + file_name + '.xml')
            os.replace(file_path, './images/!three_box_images/' + file_name + '.png')
            print(file_name+'.xml generated with less than three boxes')
        else:
            tree.write('./xmls/three_box/' + file_name + '.xml')
            os.replace(file_path, './images/three_box_images/' + file_name + '.png')
            print(file_name+'.xml generated with all three boxes')
    except Exception as e:
        print('Error to generate XML for image '+file_name)
        print(e)


#make directories
if not os.path.exists('images'):
    os.mkdir('images')
    os.mkdir('images/three_box_images')
    os.mkdir('images/!three_box_images')
if not os.path.exists('xmls'):
    os.mkdir('xmls')
    os.mkdir('xmls/three_box')
    os.mkdir('xmls/!three_box')

#path of folder of trained model
detect_fn = tf.saved_model.load("saved_model")
image_list = glob.glob('images/*.png')

if len(image_list)==0:
    print("Place png files in images folder. Change all instances of .png in script to preferred image file type if needed")
    quit()

for file_path in image_list:
    img = cv2.imread(file_path)
    image_np = np.array(img)
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = detect_fn(input_tensor)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    if (num_detections>0):
        temp = Image.open(file_path)
        width, height = temp.size
        temp.close()

        for box in detections['detection_boxes']:
            y1, x1, y2, x2 = box
            box[0] = round(y1*height)
            box[1] = round(x1*width)
            box[2] = round(y2*height)
            box[3] = round(x2*width)
        generate_xml(detections['detection_boxes'], num_detections, width, height, "target", file_path)
    else:
        #If there are no targets detected at all in the file, place in separate folder
        os.replace(file_path, './images/!three_box_images/' + file_name + '.png')
