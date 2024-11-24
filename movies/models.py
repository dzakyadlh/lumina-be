from django.db import models

class Movies(models.Model):
    movie_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    imageUrl = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    releaseYear = models.IntegerField(null=True)
    isSeries = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.title
    
class MovieDetail(models.Model):
    movie_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    imageUrl = models.CharField(max_length=255, null=True)
    casts = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    releaseYear = models.IntegerField(null=True)
    releaseDate = models.DateField(blank=True, null=True)
    isSeries = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.title