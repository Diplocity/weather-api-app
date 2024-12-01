from flask import Flask, render_template, request  # Import request for handling user input
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# OpenWeather API details
api_key = '9935b634f18b706235e895eca7a81c3f'  # Replace with your actual API key
url_template = 'http://api.openweathermap.org/data/2.5/forecast?q={}&appid={}&units=metric'


def get_weather_data(city):
    url = url_template.format(city, api_key)  # Format URL with the city
    response = requests.get(url)
    data = response.json()

    # Check if the request was successful
    if response.status_code != 200:
        return None

    # Extract temperature and timestamp
    timestamps = []
    temperatures = []
    for entry in data['list']:
        timestamps.append(entry['dt_txt'])
        temperatures.append(entry['main']['temp'])

    # Create a DataFrame for processing
    weather_data = pd.DataFrame({'Timestamp': timestamps, 'Temperature': temperatures})
    return weather_data


@app.route('/', methods=['GET', 'POST'])
def home():
    city = 'Berlin'  # Default city
    if request.method == 'POST':
        city = request.form['city']  # Get the city from the form

    weather_data = get_weather_data(city)

    if weather_data is None:
        return render_template('index.html', error="City not found. Please try again.", city=city)

    # Plot the data and encode it to display on the webpage
    plt.figure(figsize=(10, 6))
    plt.plot(weather_data['Timestamp'], weather_data['Temperature'], marker='o', color='b')
    plt.xticks(rotation=45, ha='right')
    plt.title(f'Temperature Trends for {city}', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.grid(True)

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render_template('index.html', image_base64=image_base64, city=city)


if __name__ == '__main__':
    app.run(debug=True)
