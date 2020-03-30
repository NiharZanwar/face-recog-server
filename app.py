from flask import Flask, request
import os
from datetime import datetime
import time
import face_recognition
import numpy
import json
import pymysql.cursors
import uuid
import configparser

app = Flask(__name__)

json_obj = {
    "duplicate": False,
    "face_id": "",
    "encoded": True,
    "time_taken": 0.0,
    "face_detected": True,
    "error_code": 0
}
# some more data

cwd = os.getcwd()
UPLOAD_FOLDER = cwd + '/temp_pool'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
format_allowed = ['jpg', 'jpeg']
pool_dir = cwd + '/pool'


def sql_connection():

    try:
        connection = pymysql.connect(host=db_ip,
                                     user=db_uname,
                                     password=db_pass,
                                     db=db_name,
                                     port=int(db_port))
        return connection
    except pymysql.Error as e:
        print(e)
        return 0


def sql_faceid(face_id, camera_id, pool_id, type, person_id, date_time):
    connection = sql_connection()
    if connection == 0:
        print("could not connect to sql server")
        return 0
    else:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO `temple_face`.`face_table` (`face_id`, `pool_id`, `camera_id`, `type`, `person_id`,"
                       " `date_time`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(str(face_id), str(pool_id),
                                                                                          str(camera_id), str(type),
                                                                                          str(person_id), str(date_time)))
            connection.commit()
            connection.close()
            # print("sql faceid registered - " + str(face_id))
            return 1
        except:
            print("error while adding to face_table")
            return 0


def sql_transaction(face_id, camera_id, pool_id, type, person_id, duplicate, date_time):
    connection = sql_connection()
    if connection == 0:
        return 0
    else:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO `temple_face`.`txn_table` (`date_time`, `pool_id`, `camera_id`, `type`, `person_id`,"
                       " `face_id`, `duplicate`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(str(date_time), str(pool_id),
                                                                                          str(camera_id), str(type),
                                                                                          str(person_id), str(face_id),
                                                                                        str(duplicate)))
            connection.commit()
            # print("sql txn registered - " + str(face_id) + "duplicate:" + str(duplicate))
            connection.close()
            return 1
        except:
            print("error while adding to txn_table")
            return 0


def enroll_face(filename, pool_id, camera_id, face_detected, type, date_time):
    response = json_obj

    image = face_recognition.load_image_file(UPLOAD_FOLDER + '/' + filename)

    if face_detected == '0':

        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1)

        if len(face_locations) == 0:
            try:
                os.remove(UPLOAD_FOLDER + '/' + filename)
                response['face_detected'] = False
                return response
            except:
                return response

    try:
        encoding = face_recognition.face_encodings(image, num_jitters=1)[0]
    except:
        os.remove(UPLOAD_FOLDER + '/' + filename)
        response['encoded'] = False
        return response

    numpy_dir = pool_dir + '/' + str(pool_id) + '/encodings'
    numpy_dir_list = os.listdir(numpy_dir)
    faces_dir = pool_dir + '/' + str(pool_id) + '/faces'

    for i in range(0, len(numpy_dir_list)):
        old_encoding = [numpy.load(numpy_dir + '/' + numpy_dir_list[i])]
        result = face_recognition.compare_faces(old_encoding, encoding, tolerance=0.6)

        if result[0]:
            os.remove(UPLOAD_FOLDER + '/' + filename)
            response['duplicate'] = True
            response['face_id'] = numpy_dir_list[i].split('.')[0]
            sql_transaction(numpy_dir_list[i].split('.')[0], camera_id, pool_id, type, '', 1, date_time)
            return response

    numpy.save(numpy_dir + '/' + filename.split('.')[0], encoding)
    response['face_id'] = filename.split('.')[0]
    os.rename(UPLOAD_FOLDER + '/' + filename, faces_dir + '/' + filename)
    sql_transaction(filename.split('.')[0], camera_id, pool_id, type, '', 0, date_time)
    result = sql_faceid(filename.split('.')[0], camera_id, pool_id, type, '', date_time)
    return response


@app.route('/enroll_face', methods=['POST'])
def enroll():
    now = time.time()
    file = request.files['image']
    pool_id = request.args['pool_id']
    camera_id = request.args['camera_id']
    face_detected = request.args['face_detected']
    type = request.args['type']

    if file.filename.split('.')[1] not in format_allowed:
        return 'upload correct file format'

    if pool_id not in os.listdir(pool_dir):
        return 'pool_id does not exist'

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # file.filename = str(int(time.time()*100)) + '.jpg'
    file.filename = str(uuid.uuid4().fields[-1])[:7] + '.jpg'

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    result = enroll_face(file.filename, pool_id, camera_id, face_detected, type, date_time)
    result['time_taken'] = time.time() - now
    return json.dumps(result)


if __name__ == '__main__':
    while True:
        if 'face-server.conf' not in os.listdir(os.getcwd()):
            print("config file not present")
            time.sleep(10)
        else:
            config = configparser.ConfigParser()
            config.read("face-server.conf")
            try:

                server_ip = config["server_details"]["ip"]
                server_port = config["server_details"]["port"]
                break
            except Exception as e:
                print("Error while parsing config file.")

    while True:
        config.read("face-server.conf")
        db_ip = config["mysql"]["ip"]
        db_port = config["mysql"]["port"]
        db_uname = config["mysql"]["username"]
        db_pass = config["mysql"]["password"]
        db_name = config["mysql"]["database"]

        if sql_connection() == 0:
            time.sleep(5)
        else:
            print("mySQL connection success")
            break

    app.run(host='0.0.0.0', port=server_port, debug=True)


