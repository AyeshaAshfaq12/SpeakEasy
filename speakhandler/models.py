from django.db import models

# Create your models here.

class RoomMember(models.Model):
    """
    Represents a member in a room with specific language preferences.
    """

    name = models.CharField(max_length=200, verbose_name="Full Name")
    lang = models.CharField(max_length=50, verbose_name="Language")
    uid = models.CharField(max_length=200, verbose_name="User ID")
    room_name = models.CharField(max_length=200, verbose_name="Room Name")

    class Meta:
        verbose_name = "Room Member"
        verbose_name_plural = "Room Members"

    def __str__(self):
        return f"{self.name} ({self.lang}) in room '{self.room_name}'"
