from django.db import models
import requests
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

class Thing(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=100)   # FIXED
    desc = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.image_url and not self.image:
            image_content = requests.get(self.image_url).content
            file_name = self.image_url.split("/")[-1]
            self.image.save(file_name, ContentFile(image_content), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    thing=models.ForeignKey(Thing ,on_delete=models.CASCADE,related_name="comments")
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} on {self.text}"
    
class Vote(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = (
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    )

    thing = models.ForeignKey(Thing, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)

    class Meta:
        unique_together = ("thing", "user")

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("thing", "user")
    
    def __str__(self):
        return self.user.username 
