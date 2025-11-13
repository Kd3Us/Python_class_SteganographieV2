from PIL import Image
import sys


def text_to_binary(text):
    binary_string = ''
    for char in text:
        binary_string += format(ord(char), '08b')
    binary_string += '1111111111111110'
    return binary_string


def make_pixels_even(image):
    width, height = image.size
    even_image = image.copy()
    pixels = even_image.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            pixels[x, y] = (r & 0xFE, g & 0xFE, b & 0xFE)
    
    return even_image


def encode_message(image, binary_message):
    width, height = image.size
    encoded_image = image.copy()
    pixels = encoded_image.load()
    message_index = 0
    
    for y in range(height):
        for x in range(width):
            if message_index >= len(binary_message):
                break
            r, g, b = pixels[x, y]
            
            if message_index < len(binary_message):
                if binary_message[message_index] == '1':
                    r = r | 1
                message_index += 1
            
            if message_index < len(binary_message):
                if binary_message[message_index] == '1':
                    g = g | 1
                message_index += 1
            
            if message_index < len(binary_message):
                if binary_message[message_index] == '1':
                    b = b | 1
                message_index += 1
            
            pixels[x, y] = (r, g, b)
        
        if message_index >= len(binary_message):
            break
    
    return encoded_image


def calculate_image_capacity(image):
    width, height = image.size
    total_bits = width * height * 3
    delimiter_bits = 16
    available_bits = total_bits - delimiter_bits
    return max(0, available_bits // 8)


def encode_message_in_image(image_path, message, output_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        print(f"Erreur: Impossible de charger l'image {image_path}")
        return False
    
    capacity = calculate_image_capacity(image)
    if len(message) > capacity:
        print(f"Erreur: Message trop long ({len(message)} > {capacity} caracteres max)")
        return False
    
    try:
        binary_msg = text_to_binary(message)
        even_image = make_pixels_even(image)
        encoded_image = encode_message(even_image, binary_msg)
        
        encoded_image.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"Erreur lors de l'encodage: {e}")
        return False


def main():
    image_path = "picture.jpg"
    output_path = "encoded_image.png"
    
    if len(sys.argv) == 4:
        image_path = sys.argv[1]
        message = sys.argv[2]
        output_path = sys.argv[3]
    else:
        message = input("Entrez votre message a encoder: ")
    
    success = encode_message_in_image(image_path, message, output_path)
    
    if success:
        print("Encodage reussi!")
    else:
        print("Echec de l'encodage")


if __name__ == "__main__":
    main()