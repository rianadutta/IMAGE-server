# Copyright (c) 2021 IMAGE Project, Shared Reality Lab, McGill University
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# and our Additional Terms along with this program.
# If not, see
# <https://github.com/Shared-Reality-Lab/IMAGE-server/blob/main/LICENSE>.

from flask import Flask, request, jsonify
import os
import requests
import json
import time
import logging
from math import sqrt
import cv2
import base64
import numpy as np
from deepface import DeepFace
import logging
import os
import cv2
#from predictors.DetectronModels import Predictor



app = Flask(__name__)
logging.basicConfig(level=logging.NOTSET)
# this function determines the size of bounding box



def calculate_diagonal(x1, y1, x2, y2):
    diag = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return diag


@app.route("/preprocessor", methods=['POST', 'GET'])
def readImage():
    logging.debug("Received request")
    object_type = []
    dimensions = []
    area = []
    # loading schemas to check of the received and returned outputs are correct
    # with open('./schemas/preprocessors/sorting.schema.json') as jsonfile:
    #     data_schema = json.load(jsonfile)
    # with open('./schemas/preprocessor-response.schema.json') as jsonfile:
    #     schema = json.load(jsonfile)
    # with open('./schemas/definitions.json') as jsonfile:
    #     definition_schema = json.load(jsonfile)
    # with open('./schemas/request.schema.json') as jsonfile:
    #     first_schema = json.load(jsonfile)
    # # Following 6 lines of code are refered from
    # # https://stackoverflow.com/questions/42159346/jsonschema-refresolver-to-resolve-multiple-refs-in-python
    # schema_store = {
    #     schema['$id']: schema,
    #     definition_schema['$id']: definition_schema
    # }
    # resolver = jsonschema.RefResolver.from_schema(
    #     schema, store=schema_store)
    content = request.get_json()
    # # check if received input is correct
    # try:
    #     validator = jsonschema.Draft7Validator(first_schema, resolver=resolver)
    #     validator.validate(content)
    # except jsonschema.exceptions.ValidationError as e:
    #     logging.error(e)
    #     return jsonify("Invalid Preprocessor JSON format"), 400
    preprocessor = content["preprocessors"]
#    logging.info(preprocessor)
    if "ca.mcgill.a11y.image.preprocessor.objectDetection" \
            not in preprocessor:
        logging.info("Object detection output not "
                     "available. Skipping...")
        return "", 204
    oDpreprocessor = \
        preprocessor["ca.mcgill.a11y.image.preprocessor.objectDetection"]
    objects = oDpreprocessor["objects"]
    image_b64 = content["graphic"].split(",")[1]
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    pil_image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    img_original = np.array(pil_image)
    height, width, channels = img_original.shape
    print(img_original.shape, flush=True)
#    logging.debug("in here")
    final_data = []
    for i in range(len(objects)):
        #print(objects[i]["type"])
        
        if("person" in objects[i]["type"]):
            object_type.append(objects[i]["type"])
            dimensions.append(objects[i]["dimensions"])
            area.append(objects[i]["area"])
            dimx = int(objects[i]["dimensions"][0] * width)
            dimx1 = int(objects[i]["dimensions"][2] * width)
            dimy = int(objects[i]["dimensions"][1] * height)
            dimy1 = int(objects[i]["dimensions"][3] * height)
            img = img_original[dimy:dimy1,dimx:dimx1]
            try:
                obj = DeepFace.analyze(img, actions = ['emotion'])

            except:
                obj = []
            print(obj)
            if(len(obj)==0):
                data = {
                "personID" : objects[i]["ID"],
                "emotion":"None",
                "gender" : None,
                "confidence":None,
                 }
            else:
                data = {
                "personID" : objects[i]["ID"],
                "emotion":obj[0]['dominant_emotion'],
                #"gender" : obj["gender"],
                "confidence":obj[0]["emotion"][obj[0]["dominant_emotion"]],
                }
            final_data.append(data)

    # "data": [{
    #     "id" : objects[i]["ID"],
    #             "emotion":obj['dominant_emotion'],
    #             "gender" : obj["gender"]
    # }]
    #cv2.imwrite('test1.png', img_original)
#    return "ok"
    # create 3 lists for 3 sortings(refer readme for finding the type of
    # sorting)
    # for i in range(len(objects)):
    #     left2right.append([objects[i]["ID"], dimensions[i][2]])
    #     top2bottom.append([objects[i]["ID"], dimensions[i][1]])
    #     small2big.append([objects[i]["ID"], area[i]])
    # # sort the lists
    # top2bottom = sorted(top2bottom, key=lambda x: x[1])
    # left2right = sorted(left2right, key=lambda x: x[1])
    # small2big = sorted(small2big, key=lambda x: x[1])
    # # just get the sorted IDs and dump everything else
    # for i in range(len(top2bottom)):
    #     top_id.append(top2bottom[i][0])
    #     left_id.append(left2right[i][0])
    #     small_id.append(small2big[i][0])
    request_uuid = content["request_uuid"]
    timestamp = time.time()
    name = "ca.mcgill.a11y.image.preprocessor.emotion"
    data = {"data":final_data}
    logging.info(data)
    # data = {"leftToRight": left_id,
    #         "topToBottom": top_id, "smallToBig": small_id}
    # # verify the output format
    # try:
    #     validator = jsonschema.Draft7Validator(data_schema)
    #     validator.validate(data)
    # except jsonschema.exceptions.ValidationError as e:
    #     logging.error(e)
    #     return jsonify("Invalid Preprocessor JSON format"), 500
    response = {
        "request_uuid": request_uuid,
        "timestamp": int(timestamp),
        "name": name,
        "data": data
    }
    # try:
    #     validator = jsonschema.Draft7Validator(
    #         schema, resolver=resolver)
    #     validator.validate(response)
    # except jsonschema.exceptions.ValidationError as e:
    #     logging.error(e)
    #     return jsonify("Invalid Preprocessor JSON format"), 500
    # logging.debug("Sending response")
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
