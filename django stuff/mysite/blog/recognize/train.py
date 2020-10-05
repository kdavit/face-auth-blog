import math
from sklearn import neighbors
import os
import os.path
import pickle
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder


TRAIN_DIR = '../../media/profile_pics'
MODEL_SAVE_PATH_KNN = 'blog/recognize/models/knn/'
ENCODINGS_PATH = 'blog/recognize/encodings/enc.clf'
IMAGE_PATH = 'media/profile_pics/'


def get_encodings():
    encodings = []
    persons = []

    # Loop through each person in the training set
    for class_dir in os.listdir(TRAIN_DIR):
        if not os.path.isdir(os.path.join(TRAIN_DIR, class_dir)):
            continue

        # Loop through each training image for the current person
        for img_path in image_files_in_folder(os.path.join(TRAIN_DIR, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)

            # Checking if image contains one face
            if len(face_bounding_boxes) == 1:
                encodings.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                persons.append(class_dir)

    # encodings.append(persons)
    # if ENCODINGS_PATH is not None:
    #     with open(ENCODINGS_PATH, 'wb') as f:
    #         pickle.dump(encodings, f)

    return encodings, persons


def train_knn(encodings, persons, path, knn_algo='ball_tree'):

    # Determine how many neighbors to use for weighting in the KNN classifier
    n_neighbors = int(round(math.sqrt(len(encodings))))

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(encodings, persons)

    if path is not None:
        with open(path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


def save_clf(clf, clf_name):

    if clf_name == 'knn':
        path = MODEL_SAVE_PATH_KNN + 'model.clf'

    if path is not None:
        with open(path, 'wb') as f:
            pickle.dump(clf, f)
    return clf


def save_encodings(encodings):
    path = ENCODINGS_PATH

    if path is not None:
        with open(path, 'wb') as f:
            pickle.dump(encodings, f)
    return encodings


def read_encodings():
    with open(ENCODINGS_PATH, 'rb') as f:
        encodings = pickle.load(f)
        persons = encodings[-1]
        encodings = encodings[:-1]

        return encodings, persons


def delete_enc(encodings, persons, person):
    # delete person from persons and also its encodings
    p_index = persons.index(person)
    encodings.pop(p_index)
    persons.pop(p_index)

    # also delete images
    # for file in os.listdir(IMAGE_PATH + person):
    #     if file != str(img_path):
    #         os.remove(IMAGE_PATH + person + '/' + file)

    return encodings, persons


def retrain(img_path, person, knn_algo='ball_tree'):
    encodings, persons = read_encodings()

    # if user has more than 10 images delete rest of them
    if persons.count(person) + 1 >= 10:
        encodings, persons = delete_enc(encodings, persons, person)

    # train for new picture
    if img_path:
        image = face_recognition.load_image_file(img_path)
        face_bounding_boxes = face_recognition.face_locations(image)

        # Checking if image contains one face
        if len(face_bounding_boxes) == 1:
            encodings.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
            persons.append(person)

    # Determine how many neighbors to use for weighting in the KNN classifier
    n_neighbors = int(round(math.sqrt(len(encodings))))

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(encodings, persons)

    save_clf(knn_clf, 'knn')

    encodings.append(persons)
    save_encodings(encodings)

    return knn_clf
