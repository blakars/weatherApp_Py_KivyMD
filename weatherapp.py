from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from plyer import gps
import requests
import geocoder
import platform
import os
from dotenv import load_dotenv

# pull data from file .env
load_dotenv()
api_key = os.getenv('API_KEY')    # crap API_KEY from file

class WeatherScreen(Screen):
    pass

class RootWidget(ScreenManager):
    pass

kv = '''
RootWidget:
    WeatherScreen:

<WeatherScreen>:
    name: 'weather'
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        padding: dp(20)
        
        MDLabel:
            text: "Weather App"
            halign: "center"
            font_style: "H6"
            theme_text_color: "Primary"
            size_hint_y: 0.1

        Image:
            id: weather_icon
            source: ""
            size_hint_y: 0.2
            pos_hint: {'center_x': 0.5}

        GridLayout:
            cols: 2
            spacing: dp(20)
            padding: dp(20)
            size_hint_y: 0.4
            
            MDLabel:
                text: "Location:"
                halign: "right"
                theme_text_color: "Secondary"

            MDLabel:
                id: location_label
                halign: "left"
                theme_text_color: "Primary"

            MDLabel:
                text: "Temperature:"
                halign: "right"
                theme_text_color: "Secondary"

            MDLabel:
                id: temperature_label
                halign: "left"
                theme_text_color: "Primary"

            MDLabel:
                text: "Description:"
                halign: "right"
                theme_text_color: "Secondary"

            MDLabel:
                id: description_label
                halign: "left"
                theme_text_color: "Primary"

            MDLabel:
                text: "Humidity:"
                halign: "right"
                theme_text_color: "Secondary"

            MDLabel:
                id: humidity_label
                halign: "left"
                theme_text_color: "Primary"

            MDLabel:
                text: "Rain:"
                halign: "right"
                theme_text_color: "Secondary"

            MDLabel:
                id: rain_label
                halign: "left"
                theme_text_color: "Primary"

        MDTextField:
            id: city_input
            hint_text: "Enter city name"
            helper_text: "Press Enter or click 'Search' to get weather"
            helper_text_mode: "on_focus"
            size_hint_y: None
            height: dp(40)
            on_text_validate: app.get_weather_by_city(self.text)
            
        MDRectangleFlatButton:
            text: "Search"
            on_release: app.get_weather_by_city(city_input.text)
            pos_hint: {'center_x': 0.5}

'''

class WeatherApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(kv)

    def on_start(self):
        # Request location permissions and start receiving updates
        try:
            if platform.system()=="Windows":
                g = geocoder.ip('me')
                lat, lng = g.latlng
            else:
                location=gps.getlocation()
                lat, lng = location["lat"], location["lon"]

            if lat and lng:
                self.get_weather_by_location(lat, lng)
            else:
                self.root.get_screen('weather').ids.weather_label.text = "Location data not available"  

        except Exception as e:
            # Handle any exceptions gracefully
            print("Error:", e)

    def get_weather(self, params):
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(weather_url, params=params)
        weather_data = response.json()
        
        if response.status_code == 200:
            city = weather_data["name"]
            temperature = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"].capitalize()
            humidity = weather_data["main"]["humidity"]
            rain = weather_data.get("rain", {}).get("1h", 0)
            
            self.root.get_screen('weather').ids.location_label.text = city
            self.root.get_screen('weather').ids.temperature_label.text = f"{temperature}°C"
            self.root.get_screen('weather').ids.description_label.text = description
            self.root.get_screen('weather').ids.humidity_label.text = f"{humidity}%"
            self.root.get_screen('weather').ids.rain_label.text = f"{rain} mm"

            # Set weather icon based on weather condition
            weather_icon = weather_data["weather"][0]["icon"]
            self.root.get_screen('weather').ids.weather_icon.source = f"icons/{weather_icon}.png"
        else:
            self.root.get_screen('weather').ids.weather_label.text = "Weather data not found"

    def get_weather_by_location(self, lat, lon):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        self.get_weather(params)

    def get_weather_by_city(self, city):
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        self.get_weather(params)

if __name__ == '__main__':
    WeatherApp().run()