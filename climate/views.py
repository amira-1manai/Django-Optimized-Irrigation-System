from django.conf import settings
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Field, IrrigationPlan, WaterSource, WaterUsage
import pickle
from django.shortcuts import render
import datetime
import pandas as pd
from django.shortcuts import render
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from django.shortcuts import render

import pickle
def index(request):
    api_key = 'b698494103add4361a716425d3c81fca'
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'

    city = request.GET.get('city')

    if not city:
        return JsonResponse({'error': 'City parameter is missing'})

    weather_data, daily_forecasts = fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url)

    return JsonResponse({
        'weather_data': weather_data,
        'daily_forecasts': daily_forecasts,
    })

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()

    print("Current weather response:", response)

    if 'coord' not in response:
        return {'error': f"City '{city}' not found or API error."}, []

    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    print("Forecast response:", forecast_response)

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    daily_forecasts = []
    if 'daily' in forecast_response:
        for daily_data in forecast_response['daily'][:5]:
            daily_forecasts.append({
                'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
                'min_temp': round(daily_data['temp']['min'] - 273.15, 2),
                'max_temp': round(daily_data['temp']['max'] - 273.15, 2),
                'description': daily_data['weather'][0]['description'],
                'icon': daily_data['weather'][0]['icon'],
            })
    else:
        return {'error': 'Forecast data not available.'}, []

    return weather_data, daily_forecasts

def home_view(request):
    return render(request, 'frontoffice/layout/app.html')

def template_tables(request):
    return render(request, 'frontoffice/template/tables.html')

# fields
def create_field(request):
    if request.method == 'POST':
        size = request.POST.get('size')
        location = request.POST.get('location')
        crop_type = request.POST.get('crop_type')
        soil_type = request.POST.get('soil_type')

        errors = {}
        if not size or not location or not crop_type or not soil_type:
            errors['field'] = 'All fields are required.'

        if not errors:
            Field.objects.create(size=size, location=location, crop_type=crop_type, soil_type=soil_type)
            return redirect('field_list')

        return render(request, 'frontoffice/create_field.html', {'errors': errors})

    return render(request, 'frontoffice/field/create_field.html')

def field_list(request):
    fields = Field.objects.all()
    return render(request, 'frontoffice/field/field_list.html', {'fields': fields})

def field_delete(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    if request.method == 'POST':
        field.delete()
        messages.success(request, 'Field deleted successfully.')
        return redirect('field_list')
    return redirect('field_list')

def field_update(request, field_id):
    field = get_object_or_404(Field, id=field_id)

    if request.method == 'POST':
        field.size = request.POST['size']
        field.location = request.POST['location']
        field.crop_type = request.POST['crop_type']
        field.soil_type = request.POST['soil_type']
        field.save()
        return redirect('field_list')

    return render(request, 'frontoffice/field/update_field.html', {'field': field})

# Create a new water source
def create_water_source(request):
    if request.method == 'POST':
        type_ = request.POST.get('type')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')

        errors = {}
        if not type_ or not location or not capacity:
            errors['field'] = 'All fields are required.'

        if not errors:
            WaterSource.objects.create(type=type_, location=location, capacity=capacity)
            return redirect('water_source_list')

        return render(request, 'frontoffice/water_sources/create_water_source.html', {'errors': errors})

    return render(request, 'frontoffice/water_sources/create_water_source.html')

# List all water sources
def water_source_list(request):
    water_sources = WaterSource.objects.all()
    return render(request, 'frontoffice/water_sources/water_source_list.html', {'water_sources': water_sources})

# Delete a water source
def water_source_delete(request, water_source_id):
    water_source = get_object_or_404(WaterSource, id=water_source_id)
    if request.method == 'POST':
        water_source.delete()
        messages.success(request, 'Water source deleted successfully.')
        return redirect('water_source_list')
    return redirect('water_source_list')

# Update a water source
def water_source_update(request, water_source_id):
    water_source = get_object_or_404(WaterSource, id=water_source_id)

    if request.method == 'POST':
        water_source.type = request.POST['type']
        water_source.location = request.POST['location']
        water_source.capacity = request.POST['capacity']
        water_source.save()
        return redirect('water_source_list')

    return render(request, 'frontoffice/water_sources/update_water_source.html', {'water_source': water_source})

# Create a new water usage
def create_water_usage(request):
    if request.method == 'POST':
        irrigation_plan_id = request.POST.get('irrigation_plan')
        water_source_id = request.POST.get('water_source')
        amount_used = request.POST.get('amount_used')

        errors = {}
        if not irrigation_plan_id or not water_source_id or not amount_used:
            errors['field'] = 'All fields are required.'

        if not errors:
            WaterUsage.objects.create(
                irrigation_plan_id=irrigation_plan_id,
                water_source_id=water_source_id,
                amount_used=amount_used
            )
            messages.success(request, 'L\'utilisation de l\'eau a été créée avec succès.')
            return redirect('water_usage_list')

        return render(request, 'frontoffice/water_usages/create_water_usage.html', {
            'errors': errors,
            'irrigation_plans': IrrigationPlan.objects.all(),
            'water_sources': WaterSource.objects.all()
        })

    # GET request
    return render(request, 'frontoffice/water_usages/create_water_usage.html', {
        'irrigation_plans': IrrigationPlan.objects.all(),
        'water_sources': WaterSource.objects.all()
    })
# Update a water usage
def water_usage_update(request, water_usage_id):
    water_usage = get_object_or_404(WaterUsage, id=water_usage_id)

    if request.method == 'POST':
        water_usage.irrigation_plan_id = request.POST['irrigation_plan']
        water_usage.water_source_id = request.POST['water_source']
        water_usage.amount_used = request.POST['amount_used']
        water_usage.save()
        messages.success(request, 'Water usage updated successfully.')
        return redirect('water_usage_list')

    return render(request, 'frontoffice/water_usages/update_water_usage.html', {
        'water_usage': water_usage,
        'irrigation_plans': IrrigationPlan.objects.all(),
        'water_sources': WaterSource.objects.all()
    })
# Delete a water usage
def water_usage_delete(request, water_usage_id):
    water_usage = get_object_or_404(WaterUsage, id=water_usage_id)
    if request.method == 'POST':
        water_usage.delete()
        messages.success(request, 'Water usage deleted successfully.')
        return redirect('water_usage_list')
    return redirect('water_usage_list')  # Redirect if method is not POST
# List all water usages
def water_usage_list(request):
    water_usages = WaterUsage.objects.all()
    return render(request, 'frontoffice/water_usages/water_usage_list.html', {
        'water_usages': water_usages
    })
#
def train_and_predict(request):
    # Récupérer les données de WaterUsage
    data = pd.DataFrame(list(WaterUsage.objects.all().values()))

    # Ajoute ceci pour inspecter les données
    print(data.head())  # Affiche les 5 premières lignes du DataFrame dans la console

    if data.empty:
        return render(request, 'frontoffice/water_usages/predict.html', {'error': 'No data available for training.'})

    # Assurez-vous que les noms de colonnes correspondent à ceux dans le DataFrame
    if 'irrigation_plan_id' not in data.columns or 'water_source_id' not in data.columns:
        return render(request, 'frontoffice/water_usages/predict.html', {'error': 'Expected columns not found in data.'})

    # Encodage des variables catégorielles
    label_encoder = LabelEncoder()
    data['irrigation_plan'] = label_encoder.fit_transform(data['irrigation_plan_id'])
    data['water_source'] = label_encoder.fit_transform(data['water_source_id'])

    # Séparation des features et de la target
    X = data[['irrigation_plan', 'water_source']]
    y = data['amount_used']

    # Division en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Création du modèle
    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    # Prédictions
    predictions = model.predict(X_test)

    # Convertir les prédictions en une liste pour le template
    predictions_list = predictions.tolist()

    # Renvoie le résultat au template
    return render(request, 'frontoffice/water_usages/predict.html', {'predictions': predictions_list})



def predict_water_usage(request):
    predicted_usage = None
    water_sources = WaterSource.objects.all()  # Fetch all water sources for the dropdown

    if request.method == 'POST':
        water_source_id = request.POST.get('water_source_id')
        water_source = get_object_or_404(WaterSource, id=water_source_id)

        # Load the trained model
        with open('climate/water_optimization_model.pkl', 'rb') as f:
            model = pickle.load(f)

        # Make a prediction using the capacity of the selected water source
        predicted_usage = model.predict([[water_source.capacity]])[0]

    return render(request, 'frontoffice/water_usages/predict_water_usage.html', {
        'predicted_usage': predicted_usage,
        'water_sources': water_sources,
    })

# Function to load your pre-trained model
def load_model():
    with open('climate/water_quality_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

# View function for predicting water quality
def predict_water_quality_view(request):
    result = None  # Initialize result to None

    if request.method == 'POST':
        # Extracting values from the submitted form
        try:
            electrical_conductivity = float(request.POST.get('electrical_conductivity'))
            ph = float(request.POST.get('ph'))
            sar = float(request.POST.get('sar'))
            turbidity = float(request.POST.get('turbidity'))
            hardness = float(request.POST.get('hardness'))
            tds = float(request.POST.get('tds'))
            chloride = float(request.POST.get('chloride'))
            sulfate = float(request.POST.get('sulfate'))
            nitrate = float(request.POST.get('nitrate'))

            # Call the prediction function
            result = predict_water_quality(electrical_conductivity, ph, sar, turbidity, hardness, tds, chloride, sulfate, nitrate) # type: ignore

        except ValueError:
            result = "Please ensure all input values are valid numbers."

    return render(request, 'frontoffice/water_sources/water_quality_form.html', {'result': result})

# Prediction function
def predict_water_quality_view(request):
    result = None  # Initialize result to None

    if request.method == 'POST':
        # Extracting values from the submitted form
        try:
            electrical_conductivity = float(request.POST.get('electrical_conductivity'))
            ph = float(request.POST.get('ph'))
            sar = float(request.POST.get('sar'))
            turbidity = float(request.POST.get('turbidity'))
            hardness = float(request.POST.get('hardness'))
            tds = float(request.POST.get('tds'))
            chloride = float(request.POST.get('chloride'))
            sulfate = float(request.POST.get('sulfate'))
            nitrate = float(request.POST.get('nitrate'))

            # Load the model
            model = load_model()

            # Prepare the input data as a DataFrame
            input_data = pd.DataFrame({
                'Electrical_Conductivity_uS': [electrical_conductivity],
                'pH': [ph],
                'Sodium_Adsorption_Ratio': [sar],
                'Turbidity_NTU': [turbidity],
                'Hardness_mg_L': [hardness],
                'Total_Dissolved_Solids_mg_L': [tds],
                'Chloride_mg_L': [chloride],
                'Sulfate_mg_L': [sulfate],
                'Nitrate_mg_L': [nitrate]
            })

            # Make the prediction
            prediction = model.predict(input_data)

            # Interpret the prediction
            if prediction[0] == "Suitable":
                result = "The water quality is suitable for irrigation."
            else:
                result = "The water quality is not suitable for irrigation."

        except ValueError:
            result = "Please ensure all input values are valid numbers."

    # Render the template with the result
    return render(request, 'frontoffice/water_sources/water_quality_form.html', {'result': result})