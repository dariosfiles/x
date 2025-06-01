import subprocess
import sys
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from rule34Py import rule34Py
from kivy.core.image import Image as CoreImage
import requests
from io import BytesIO
from PIL import Image as PILImage

class Rule34App(App):
    def build(self):
        # Check and install required packages if necessary
        self.check_and_install_requirements()

        self.r34 = rule34Py()
        self.results = []
        self.index = 0

        # Create layout
        self.layout = BoxLayout(orientation='vertical', padding=20)

        # Password prompt
        self.password_label = Label(text="Enter Password to Continue", size_hint=(1, 0.1))
        self.layout.add_widget(self.password_label)

        self.password_input = TextInput(password=True, hint_text="Password", size_hint=(1, 0.1))
        self.layout.add_widget(self.password_input)

        self.password_button = Button(text="Unlock", on_press=self.check_password, size_hint=(1, 0.1))
        self.layout.add_widget(self.password_button)

        # Search input and button
        self.search_input = TextInput(hint_text="Enter search tag(s)", size_hint=(1, 0.1), disabled=True)
        self.layout.add_widget(self.search_input)

        self.search_button = Button(text="Search", on_press=self.search_images, disabled=True, size_hint=(1, 0.1))
        self.layout.add_widget(self.search_button)

        # Image display area
        self.image = Image(size_hint=(1, 0.7))
        self.layout.add_widget(self.image)

        self.next_button = Button(text="Next Image", on_press=self.next_image, size_hint=(1, 0.1), disabled=True)
        self.layout.add_widget(self.next_button)

        return self.layout

    def check_and_install_requirements(self):
        """Check if required packages are installed. If not, install them."""
        required_packages = ['rule34Py', 'requests', 'pillow', 'kivy']
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    def check_password(self, instance):
        """Check if the password is correct."""
        if self.password_input.text == "mangito":
            self.password_label.text = "Password correct!"
            self.password_input.disabled = True
            self.password_button.disabled = True
            self.search_input.disabled = False
            self.search_button.disabled = False
        else:
            self.password_label.text = "Incorrect password, try again!"

    def search_images(self, instance):
        """Search for images using the Rule34 API."""
        tags = self.search_input.text.strip().split()
        if not tags:
            return

        try:
            self.results = self.r34.search(tags, limit=20)
            self.index = 0
            if self.results:
                self.display_image()
                self.next_button.disabled = False
            else:
                self.image.source = ''
                self.password_label.text = "No results found!"
        except Exception as e:
            self.password_label.text = f"Error: {e}"

    def next_image(self, instance):
        """Display the next image."""
        if self.results:
            self.index = (self.index + 1) % len(self.results)
            self.display_image()

    def display_image(self):
        """Display the current image from the results."""
        try:
            post = self.results[self.index]
            url = post.image
            response = requests.get(url)
            image_data = BytesIO(response.content)

            pil_image = PILImage.open(image_data)
            pil_image.thumbnail((Window.width, Window.height * 0.7))

            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)

            kivy_image = CoreImage(buffer, ext='png').texture
            self.image.texture = kivy_image
        except Exception as e:
            self.password_label.text = f"Error: {e}"

if __name__ == "__main__":
    # Set window size to better fit mobile devices
    Window.size = (360, 640)
    Rule34App().run()
