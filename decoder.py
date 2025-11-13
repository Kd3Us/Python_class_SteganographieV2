from PIL import Image
import numpy as np
import sys
import os


def decode_message(encoded_image_array):
    height, width, channels = encoded_image_array.shape
    binary_message = ''
    
    print(f"Extraction des bits de l'image {width}x{height} ({channels} canaux)...")
    
    for y in range(height):
        for x in range(width):
            for channel in range(channels):
                lsb = encoded_image_array[y, x, channel] & 1
                binary_message += str(lsb)
    
    delimiter = '1111111111111110'
    end_index = binary_message.find(delimiter)
    
    if end_index == -1:
        return None
    
    print(f"Delimiteur trouve a la position {end_index}")
    
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


def get_image_info(image_array):
    if image_array is None:
        print("Aucune image fournie")
        return
    
    height, width, channels = image_array.shape
    total_pixels = height * width
    total_bits = total_pixels * channels
    
    print(f"Informations sur l'image:")
    print(f"  Dimensions: {width} x {height} pixels")
    print(f"  Pixels totaux: {total_pixels:,}")
    print(f"  Valeurs par canal: min={image_array.min()}, max={image_array.max()}, moy={image_array.mean():.1f}")


def decode_message_from_image(image_path):
    print(f"Chargement de l'image: {image_path}")
    
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print(f"Image convertie en mode RGB")
        image_array = np.array(image)
    except Exception as e:
        print(f"Erreur: Impossible de charger l'image {image_path}")
        print(f"Details: {e}")
        return None
    
    print("Image chargee avec succes")
    get_image_info(image_array)
    
    try:
        print("Debut du decodage...")
        decoded_message = decode_message(image_array)
        
        if decoded_message is not None:
            print(f"Message decode avec succes!")
            return decoded_message
        else:
            print("Aucun message trouve (delimiteur non detecte)")
            print("Cette image ne contient peut-etre pas de message encode")
            return None
    except Exception as e:
        print(f"Erreur lors du decodage: {e}")
        return None


def analyze_lsb_distribution(image_array):
    print("Analyse de la distribution des LSB par canal...")
    
    height, width, channels = image_array.shape
    
    for channel in range(channels):
        channel_name = ["Rouge", "Vert", "Bleu"][channel]
        print(f"\nCanal {channel_name}:")
        
        lsbs = []
        for y in range(height):
            for x in range(width):
                lsbs.append(image_array[y, x, channel] & 1)
        
        zeros = lsbs.count(0)
        ones = lsbs.count(1)
        total = len(lsbs)
        
        print(f"  LSB = 0: {zeros:,} ({zeros/total*100:.1f}%)")
        print(f"  LSB = 1: {ones:,} ({ones/total*100:.1f}%)")
        
        if abs(zeros - ones) > total * 0.1:
            print(f"  Distribution desequilibree detectee - possible message dans ce canal")
        else:
            print(f"  Distribution equilibree - pas de message evident dans ce canal")


def main():
    print("DECODEUR STEGANOGRAPHIE LSB1 - VERSION PIL")
    
    image_path = "encoded_image.png"
    
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
        print(f"Utilisation de l'argument: {image_path}")
    else:
        print(f"Utilisation de l'image par defaut: {image_path}")
        print()
    
    decoded_message = decode_message_from_image(image_path)
    
    if decoded_message is not None:
        print(f"\nMESSAGE TROUVE!")
        print(f"Contenu: '{decoded_message}'")
        print(f"Longueur: {len(decoded_message)} caracteres")
        
        if decoded_message:
            print(f"Premier caractere: '{decoded_message[0]}' (code: {ord(decoded_message[0])})")
            if len(decoded_message) > 1:
                print(f"Dernier caractere: '{decoded_message[-1]}' (code: {ord(decoded_message[-1])})")
        
        if os.path.exists(image_path):
            base_name = os.path.splitext(image_path)[0]
            extension = os.path.splitext(image_path)[1]
            new_name = f"{base_name}_decoded{extension}"
            
            try:
                os.rename(image_path, new_name)
                print(f"\nImage renommee: {image_path} -> {new_name}")
            except OSError as e:
                print(f"\nImpossible de renommer l'image: {e}")
    else:
        print(f"\nAUCUN MESSAGE TROUVE")
        
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_array = np.array(image)
            analyze_lsb_distribution(image_array)
        except Exception as e:
            print(f"Impossible d'analyser l'image: {e}")
        
        print("\nSuggestions:")
        print("  - Verifiez que l'image contient bien un message")
        print("  - Assurez-vous d'utiliser la bonne image")
        print("  - Verifiez que l'image n'a pas ete compressee (utiliser PNG)")


if __name__ == "__main__":
    main()