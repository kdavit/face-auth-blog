import pickle
import time

import face_recognition
import cv2
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm


model_path = 'blog/recognize/models/knn/model.clf'


def face_auth(request):

    with open(model_path, 'rb') as f:
        knn_clf = pickle.load(f)

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Initialize some variables
    username = ''
    probability = 0
    process_this_frame = True

    start = time.time()

    # runs for 5 seconds
    while time.time() < start + 5:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if face_locations and face_encodings:

                closest_distances = knn_clf.kneighbors(face_encodings, n_neighbors=1)
                are_matches = [closest_distances[0][i][0] <= 0.6 for i in range(len(face_locations))]
                # if there is a match, calculating probability
                if are_matches[0]:
                    probability = round((1 - closest_distances[0][0][0]) * 100, 2)

                username = knn_clf.predict(face_encodings)[0]
                if username and probability > 60:
                    break

        process_this_frame = not process_this_frame

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    if username != '' and probability > 60:
        user = User.objects.get(username=username)
        if user:
            u_form = UserUpdateForm(instance=user)
            p_form = ProfileUpdateForm(instance=user.profile)

            login(request, user)

            context = {
                "user": user,
                "u_form": u_form,
                "p_form": p_form,
            }

            return render(request, 'profile.html', context)
        else:
            return redirect('/log-in')
    else:
        return redirect('/log-in')
