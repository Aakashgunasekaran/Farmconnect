from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
import pandas as pd
import os
from .models import Product, predict_crop
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Max
from .forms import RegisterForm, LoginForm
from .models import CustomUser

#from .forms import RegisterForm, LoginForm  # Ensure this is correct

#User = get_user_model()

def home(request):
    return render(request, 'crop_recommendation/index.html')

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, "Registration successful")
            return redirect('crop_recommendation:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'crop_recommendation/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Redirect to the home page (index.html)
                return redirect('crop_recommendation:farmer_dashboard')
            else:
                # If credentials are invalid, add an error message
                form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()

    return render(request, 'crop_recommendation/login.html', {'form': form})

@login_required
def recommend_crop(request):
    if request.method == 'POST':
        state_name = request.POST['state_name']
        district_name = request.POST['district_name']
        crop_year = request.POST['crop_year']
        season = request.POST['season']
        crop = request.POST['crop']
        area = float(request.POST['area'])

        csv_path = os.path.join(settings.BASE_DIR, 'crop_production.csv')
        df = pd.read_csv(csv_path).dropna(subset=['Area', 'Production'])

        X = df[['Area']]
        y = df['Production']
        model = DecisionTreeRegressor()
        model.fit(X, y)

        predicted_production = model.predict([[area]])[0]

        recommendation = {
            'state_name': state_name,
            'district_name': district_name,
            'crop_year': crop_year,
            'season': season,
            'crop': crop,
            'recommended_crop': crop,  # Placeholder
            'area': area,
            'predicted_production': round(predicted_production, 2)
        }

        return render(request, 'crop_recommendation/result.html', {
            'recommendations': [recommendation]
        })

    return render(request, 'crop_recommendation/input_form.html')
@login_required
def weather_form(request):
    crop = None
    if request.method == 'POST':
        temperature = float(request.POST['temperature'])
        humidity = float(request.POST['humidity'])
        rainfall = float(request.POST['rainfall'])
        soil_type = request.POST['soil_type']

        crop = predict_crop(temperature, humidity, rainfall, soil_type)

    return render(request, 'crop_recommendation/weather_form.html', {'crop': crop})

@login_required
def evaluate_model(request):
    if request.method == 'POST':
        csv_path = os.path.join(settings.BASE_DIR, 'crop_production.csv')
        df = pd.read_csv(csv_path).dropna(subset=['Area', 'Production'])

        X = df[['Area']]
        y = df['Production']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = DecisionTreeRegressor()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        return render(request, 'crop_recommendation/evaluate_model.html', {
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'r2': round(r2, 2),
            'evaluated': True
        })

    return render(request, 'crop_recommendation/evaluate_model.html', {
        'evaluated': False
    })


@login_required
def evaluate_weather(request):
    try:
        # Load dataset
        df = pd.read_csv(os.path.join(settings.BASE_DIR, 'seattle-weather.csv'))

        # Ensure required columns are present
        required_features = ['precipitation', 'temp_max', 'temp_min', 'wind', 'weather']
        if not all(col in df.columns for col in required_features):
            return HttpResponse(f"Missing required columns in dataset. Found: {df.columns.tolist()}")

        # Prepare data for model
        X = df[['precipitation', 'temp_max', 'temp_min', 'wind']]
        y = df['weather']

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Initialize and train the model
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # Example: Predict weather based on form input (form data will be passed in the request)
        if request.method == 'POST':
            precipitation = float(request.POST['precipitation'])
            temp_max = float(request.POST['temp_max'])
            temp_min = float(request.POST['temp_min'])
            wind = float(request.POST['wind'])

            input_data = pd.DataFrame([[precipitation, temp_max, temp_min, wind]], columns=['precipitation', 'temp_max', 'temp_min', 'wind'])

            # Predict the weather based on the input data
            predicted_weather = model.predict(input_data)

            # Return the prediction and model performance metrics
            accuracy = accuracy_score(y_test, model.predict(X_test))
            report = classification_report(y_test, model.predict(X_test), output_dict=True)
            matrix = confusion_matrix(y_test, model.predict(X_test))

            return render(request, 'crop_recommendation/evaluate_weather.html', {
                'predicted_weather': predicted_weather[0],
                'accuracy': round(accuracy * 100, 2),
                'report': report,
                'matrix': matrix.tolist(),
                'evaluated': True
            })

        return render(request, 'crop_recommendation/evaluate_weather.html', {'evaluated': False})

    except Exception as e:
        return HttpResponse(f"Error during evaluation: {str(e)}")



def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('crop_recommendation:login')

@login_required
def farmer_dashboard_view(request):
    return render(request, 'crop_recommendation/farmer_dashboard.html')

@login_required
def dashboard_view(request):
    products = Product.objects.filter( farmer_id=request.user)  # Only fetch products by the logged-in user
    return render(request, 'crop_recommendation/farmer_dashboard.html', {'products': products})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price_per_kg = request.POST.get('price_per_kg')
        product.quantity = request.POST.get('quantity')
        product.harvest_date = request.POST.get('harvest_date')
        product.expiry_date = request.POST.get('expiry_date')
        product.organic = request.POST.get('organic')
        product.save()
        return redirect('crop_recommendation:your_products')

    return render(request, 'crop_recommendation/edit_product.html', {'product': product})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('crop_recommendation:your_products')
    return render(request, 'crop_recommendation/delete_product.html', {'product': product})
from .forms import ProductForm

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # Generate new product_id
                last_product = Product.objects.aggregate(max_id=Max('product_id'))['max_id']
                if last_product:
                    last_num = int(last_product[1:])  # Skip 'P'
                    new_id = f'P{last_num + 1:03d}'
                else:
                    new_id = 'P001'

                # Create the product instance but don't save it yet
                product = form.save(commit=False)
                
                # Set farmer_id from the logged-in user
                product.farmer_id = request.user.kisan_id  # Assuming kisan_id is the identifier for the farmer
                
                # Set the new product_id
                product.product_id = new_id
                
                # Save the product
                product.save()

                return HttpResponse("Product added successfully!")
            except Exception as e:
                return HttpResponse(f"Error: {e}")
        else:
            return render(request, 'crop_recommendation/add_product.html', {'form': form})
    
    # Create an empty form when GET method is used
    form = ProductForm()
    return render(request, 'crop_recommendation/add_product.html', {'form': form})

from .models import Product
def view_product(request):
    products = Product.objects.all()
    return render(request, 'crop_recommendation/view_product.html', {'products': products})

@login_required
def farmer_products(request):
    farmer_id = request.user.kisan_id  
    products = Product.objects.filter(farmer_id=farmer_id)
    return render(request, 'crop_recommendation/cart.html', {'products': products})

@login_required
def pdt_dashboard(request):
    return render(request, 'crop_recommendation/pdt_dashboard.html')
