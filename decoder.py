from PIL import Image
import sys


def decode_message(image):
    width, height = image.size
    pixels = image.load()
    binary_message = ''
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
    
    delimiter = '1111111111111110'
    end_index = binary_message.find(delimiter)
    
    if end_index == -1:
        return None
    
    binary_message = binary_message[:end_index]
    
    decoded_text = ''
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:
            try:
                char = chr(int(byte, 2))
                decoded_text += char
            except ValueError:
                pass
    
    return decoded_text


def decode_message_from_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        print(f"Erreur: Impossible de charger l'image {image_path}")
        return None
    
    try:
        decoded_message = decode_message(image)
        return decoded_message
    except Exception as e:
        print(f"Erreur lors du decodage: {e}")
        return None


def main():
    image_path = "encoded_image.png"
    
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
    
    decoded_message = decode_message_from_image(image_path)
    
    if decoded_message is not None:
        print(f"Message trouve: {decoded_message}")
    else:
        print("Aucun message trouve")


if __name__ == "__main__":
    main()