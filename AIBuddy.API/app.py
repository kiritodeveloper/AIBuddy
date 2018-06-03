# Tensorflow Wrapper
# Rodrigo Gatica
# Modelo entrenado por: Matías Villagrán

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time
import glob

import os
import sys

import requests

from flask import Flask, jsonify, request, make_response

import numpy as np
import tensorflow as tf


application = Flask(__name__)


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, 'rb') as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                input_mean=0, input_std=255):
    input_name = 'file_reader'
    output_name = 'normalized'
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3,
                                           name='png_reader')
    elif file_name.endswith('.gif'):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                      name='gif_reader'))
    elif file_name.endswith('.bmp'):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels=3,
                                            name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(
        dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@application.route('/', methods=['GET'])
def list_routes():
    output = [
        'HEAD,POST   /api/v1/upload'
    ]
    return jsonify(sorted(output))


@application.route('/api/v1/upload', methods=['POST'])
def classify():
    image_path = None

    if 'file' in request.files:
        file = request.files['file']
        file.save("static/test.jpg")
        image_path = "static/test.jpg"

    if request.headers.get("Content-Type") == 'application/json':
        if 'url' not in request.json:
            error_message = {
                'success': False,
                'message': 'No url found in the request'
            }
            return make_response(jsonify(error_message), 400)

        r = requests.get(request.json.get('url'))
        image_name = 'test.jpg'
        image_file = open(os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'static', image_name), 'wb')
        for chunk in r.iter_content(100000):
            image_file.write(chunk)
        image_file.close()

        image_path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'static', image_name)

    if image_path is None:
        error_message = {
            'success': False,
            'message': 'No file or url found in the request'
        }
        return make_response(jsonify(error_message), 400)

    t = read_tensor_from_image_file(image_path,
                                    input_height=input_height,
                                    input_width=input_width,
                                    input_mean=input_mean,
                                    input_std=input_std)

    with tf.Session(graph=graph) as sess:
        start = time.time()
        results = sess.run(output_operation.outputs[0],
                           {input_operation.outputs[0]: t})
        end = time.time()
        results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]
        labels = load_labels(label_file)

    print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))

    for i in top_k:
        print(labels[i], results[i])

    return jsonify({
        labels[0]: ('%.2f' % round(100*results[0], 2))+'%',
        labels[1]: ('%.2f' % round(100*results[1], 2))+'%'
    })


if __name__ == '__main__':
    model_file = 'retrained_graph.pb'
    label_file = 'retrained_labels.txt'
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = 'Mul'
    output_layer = 'final_result'

    graph = load_graph(model_file)

    input_name = 'import/' + input_layer
    output_name = 'import/' + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    application.run(host='0.0.0.0', port=9999, threaded = True)
