import cv2
import numpy as np
import tensorflow as tf
from object_detection.builders import model_builder
from object_detection.utils import config_util
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

configs = config_util.get_configs_from_pipeline_file('mobnet320pipeline.config')
detection_model = model_builder.build(model_config=configs['model'], is_training=False)
category_index = label_map_util.create_category_index_from_labelmap('label_map.pbtxt')

detect_fn = tf.saved_model.load("5.21.22saved_model")


def detect(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


# obs virtual camera
cam = cv2.VideoCapture(2, apiPreference=cv2.CAP_ANY, params=[
    cv2.CAP_PROP_FRAME_WIDTH, 1920,
    cv2.CAP_PROP_FRAME_HEIGHT, 1080])

while cam.isOpened():
    ret, frame = cam.read()
    image_np = np.array(frame)
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'] + label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=3,
        min_score_thresh=.05,
        agnostic_mode=False)

    cv2.imshow('object detection', cv2.resize(image_np_with_detections, (600, 400)))

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cam.release()
        cv2.destroyAllWindows()
        break

print("cam closed")
