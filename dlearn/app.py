'''
  This is a simple Flask app to test whether a tensorflow model can be served
'''
from flask import Flask, request, Response, jsonify
import os, io
import numpy as np
import tensorflow as tf

# Get the model
# A list of the actual labels
label_lines = ["healthy", "unhealthy"]

with tf.gfile.FastGFile("output_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

sess = tf.Session()
softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

# define the server and handle requests
app = Flask(__name__)

@app.route('/grade', methods=['POST'])
def grade():
    # Feed the image_data as input to the graph and get first prediction
    image_data = request.files.get('imagefile')

    """ EXTREMELY INEFFICIENT STEP: SAVING A FILE TO DISK AND THEN READING IT AGAIN """
    '''
    image_data.save('data.jpg')
    image_data = tf.gfile.FastGFile('data.jpg', 'rb').read()
    '''

    # BETTER METHOD: Convert to bytearray and then to string 
    # this is what FastGFile returns
    image_data = str(bytearray(image_data.read()))

    predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    grade_dict = {}
    for node_id in top_k:
    	human_string = label_lines[node_id]
    	score = predictions[0][node_id]
        grade_dict[human_string] = float(score)
    	# print('%s (score = %.5f)' % (human_string, score))
    return jsonify(grade_dict)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("8080"), debug=True)