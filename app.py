import qrcode  # Import the QR code library
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import os

app = Flask(__name__)

# Define folders for storing uploads and generated cards
UPLOAD_FOLDER = 'uploads'
CARD_FOLDER = 'cards'

# Ensure the folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_card():
    # Print form data for debugging
    print(request.form)

    # Collect form data
    name = request.form['name']
    role = request.form['role']
    purpose = request.form.get('purpose', '')
    phone = request.form['phone']  # Capture phone number

    # The rest of your code...


    # Save the uploaded photo
    photo = request.files['photo']
    photo_path = os.path.join(UPLOAD_FOLDER, photo.filename)
    photo.save(photo_path)
    
    # Generate the ID card or visitor pass
    card_path = create_id_card(name, role, purpose, photo_path, phone)
    
    # Send the generated ID card/pass to the user
    return send_file(card_path, as_attachment=True)

def create_qr_code(data):
    # Generate a QR code for the provided data
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_code_path = os.path.join(CARD_FOLDER, "qr_code.png")
    img.save(qr_code_path)
    return qr_code_path

def create_id_card(name, role, purpose, photo_path, phone):
    # Create a blank image for the ID card with a gradient background
    card = Image.new('RGB', (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(card)

    # Create a gradient background
    for i in range(400):
        color = (200 - i // 2, 220 - i // 3, 255)  # Create a gradient effect
        draw.line([(0, i), (600, i)], fill=color)
    
    # Draw a border around the card
    border_color = (50, 50, 200)  # Dark blue
    draw.rectangle([(0, 0), (599, 399)], outline=border_color, width=5)

    # Load fonts with increased size
    font_large = ImageFont.truetype("arial.ttf", 28)  # Increase font size for large text
    font_small = ImageFont.truetype("arial.ttf", 20)  # Increase font size for small text

    # Set company name color
    company_name_color = (255, 0, 0)  # Change this to the desired color (e.g., red)

    # Add company name at the top with the specified color
    draw.text((20, 20), "B.S.H.S ALUMNI", font=font_large, fill=company_name_color)
    
    # Add user details to the card
    draw.text((20, 80), f"Name: {name}", font=font_large, fill=(0, 0, 0))
    draw.text((20, 120), f"Role: {role}", font=font_large, fill=(0, 0, 0))
    
    # If the user is a visitor, add the purpose of the visit
    if role == "visitor":
        draw.text((20, 160), f"Purpose: {purpose}", font=font_large, fill=(0, 0, 0))

    # Add phone number
    draw.text((20, 200), f"Phone: {phone}", font=font_large, fill=(0, 0, 0))

    # Open the uploaded photo and resize it
    photo = Image.open(photo_path)
    photo = photo.resize((150, 150))  # Resize the photo to fit on the card
    
    # Add a border to the photo
    photo = ImageOps.expand(photo, border=5, fill=border_color)
    
    # Paste the photo onto the card
    card.paste(photo, (400, 70))  # Adjust the position of the photo
    
    # Add shadow effect to the photo (simple shadow)
    shadow = photo.copy()
    shadow = ImageEnhance.Brightness(shadow).enhance(0.5)  # Make shadow darker
    shadow = ImageOps.expand(shadow, border=5, fill=(0, 0, 0))  # Black shadow border
    card.paste(shadow, (395, 65))  # Shadow position (offset slightly)
    
    # Create and add QR code
    qr_code_data = f"Name: {name}, Role: {role}, Phone: {phone}"  # Change to include phone number
    qr_code_path = create_qr_code(qr_code_data)
    qr_code = Image.open(qr_code_path)
    qr_code = qr_code.resize((100, 100))  # Resize the QR code
    card.paste(qr_code, (480, 250))  # Position the QR code on the card
    
    # Add a small footer or additional info at the bottom
    draw.text((20, 350), "Valid from 5th Oct,2024 to 13th Oct,2024", font=font_small, fill=(0, 0, 0))

    # Save the generated card to the cards folder
    card_path = os.path.join(CARD_FOLDER, f"{name}_id_card.png")
    card.save(card_path)
    
    return card_path

if __name__ == '__main__':
    app.run(debug=True)
