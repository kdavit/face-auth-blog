from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Profile
from .recognize import train

ENCODINGS_PATH = 'recognize/encodings/enc.clf'
MODEL_SAVE_PATH_KNN = 'blog/recognize/models/knn/model.clf'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


# if user is deleted, delete its encodings
@receiver(pre_delete, sender=User)
def delete_user_encodings(sender, instance, **kwargs):
    encodings, persons = train.read_encodings()

    length = len(persons)
    i = 0
    while i < length:
        if persons[i] == instance.username:
            encodings.pop(i)
            persons.pop(i)
            length -= 1
        else:
            i += 1

    # retrain knn
    path = MODEL_SAVE_PATH_KNN
    train.train_knn(encodings, persons, path)

    encodings.append(persons)
    train.save_encodings(encodings)
