from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
import face_recognition

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    img_path = instance.profile.image
    image = face_recognition.load_image_file(img_path)
    face_bounding_boxes = face_recognition.face_locations(image)
    # print(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
    instance.profile.save()
