from django.contrib import admin
from climate import views, ai
from django.urls import path, include


urlpatterns = [
    path('', views.home_view, name='home'),
    path('template/tables', views.template_tables, name='home'),

    #mokhtar api
    path('api/', include('predictions.urls')),

    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),


    # path('weather/', views.fetch_weather_data, name='weather'),
    path('weather/', views.fetch_weather_data, name='fetch_weather_data'),
    path('ai/', ai.ai, name='ai'),


    #fields
    path('fields/create/', views.create_field, name='create_field'),
    path('fields/', views.field_list, name='field_list'),
    path('fields/<int:field_id>/delete/', views.field_delete, name='field_delete'),
    path('fields/<int:field_id>/update/', views.field_update, name='field_update'),  # Update URL
    
    
    
    #crop 
    path('crop/create/', views.create_crop, name='create_crop'),
    path('crops/', views.crop_list, name='crop_list'),
    path('update-crop/<int:crop_id>/', views.crop_update, name='crop_update'),
    path('delete-crop/<int:crop_id>/', views.delete_crop, name='crop_delete'),



    #fertilization
    path('fertilization-schedules/create/', views.create_fertilization, name='create_fertilization'),
    path('fertilization-schedules/', views.fertilization_list, name='fertilization_list'),
    path('fertilization-schedules/update/<int:fertilization_id>/', views.update_fertilization, name='update_fertilization'),
    path('fertilization-schedules/delete/<int:schedule_id>/', views.delete_fertilization, name='delete_fertilization'),

    path('predict-fertilization/', views.predict_fertilization, name='predict_fertilization'),


]

