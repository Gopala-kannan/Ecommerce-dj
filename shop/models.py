from django.db import models
from django.contrib.auth.models import User
import datetime
import os 

def getFileName(request, filename):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
    # new_filename = '%s%s'(now_time, filename) its not work
    new_filename = f"{now_time}_{filename}"
    return os.path.join('uploads', new_filename)

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True)
    image = models.ImageField(upload_to=getFileName, null=True, blank=True)
    description = models.TextField(max_length=200, null=False, blank=False)
    status = models.BooleanField(default=False, help_text= "0-show, 1-Hidden")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=True)
    vendor = models.CharField(max_length=100, null=False, blank=True)
    product_image = models.ImageField(upload_to=getFileName, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False)
    original_price = models.FloatField(null=False, blank=False)
    selling_price = models.FloatField(null=False, blank=False)
    description = models.TextField(max_length=200, null=False, blank=False)
    status = models.BooleanField(default=False, help_text= "0-show, 1-Hidden")
    trending = models.BooleanField(default=False, help_text= "0-show, 1-Trending")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_qyt = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_price(self):
        return self.product_qyt*self.product.selling_price
    
class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    