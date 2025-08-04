from django.contrib import admin
from .models import Favorite

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'vehicle__brand', 'vehicle__model')
    date_hierarchy = 'added_at'