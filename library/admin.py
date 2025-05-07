from django.contrib import admin
from .models import CustomUser, Book, BorrowRecord, Genre
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Book)
admin.site.register(BorrowRecord)
admin.site.register(Genre)
