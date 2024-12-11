from django.db import models

# Create your models here.
class Bouquet(models.Model):
    name = models.CharField('Название букета', max_length=100)
    price = models.IntegerField('Цена')
    image = models.ImageField(upload_to='images/')

    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def __str__(self):
        return self.name
