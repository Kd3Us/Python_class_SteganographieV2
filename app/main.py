import streamlit as st
import tempfile
import os
from PIL import Image
import io

from backend import vigenere_cipher
from encoder import encode_message_in_image, calculate_image_capacity
from decoder import decode_message_from_image


def main():
    st.set_page_config(
        page_title="Cryptographie et Stéganographie",
        layout="wide"
    )
    
    st.title("Cryptographie et Stéganographie")
    
    mode = st.sidebar.radio(
        "Mode:",
        ["Encoder", "Décoder"]
    )
    
    if mode == "Encoder":
        encoder_interface()
    else:
        decoder_interface()


def encoder_interface():
    st.header("Encoder")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Image:",
            type=['png', 'jpg', 'jpeg'],
            key="encoder_image"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            capacity = calculate_image_capacity(image)
            st.write(f"Capacité: {capacity} caractères")
    
    with col2:
        message = st.text_area("Message:", height=100)
        password = st.text_input("Clé:", type="password")
        
        if message and uploaded_file is not None:
            if len(message) > calculate_image_capacity(Image.open(uploaded_file)):
                st.error("Message trop long")
    
    if st.button("Encoder"):
        if not uploaded_file or not message or not password:
            st.error("Remplir tous les champs")
        else:
            encode_process(uploaded_file, message, password)


def decoder_interface():
    st.header("Décoder")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Image encodée:",
            type=['png', 'jpg', 'jpeg'],
            key="decoder_image"
        )
        
        if uploaded_file is not None:
            st.image(Image.open(uploaded_file), use_column_width=True)
    
    with col2:
        password = st.text_input("Clé:", type="password", key="decoder_password")
    
    if st.button("Décoder"):
        if not uploaded_file or not password:
            st.error("Remplir tous les champs")
        else:
            decode_process(uploaded_file, password)


def encode_process(uploaded_file, message, password):
    try:
        crypted_message = vigenere_cipher(message, password, cipher=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_input:
            tmp_input.write(uploaded_file.getvalue())
            tmp_input_path = tmp_input.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_output:
            tmp_output_path = tmp_output.name
        
        success = encode_message_in_image(tmp_input_path, crypted_message, tmp_output_path)
        
        if success:
            with open(tmp_output_path, 'rb') as f:
                encoded_image_data = f.read()
            
            os.unlink(tmp_input_path)
            os.unlink(tmp_output_path)
            
            st.success("Encodé")
            
            st.download_button(
                label="Télécharger",
                data=encoded_image_data,
                file_name="image_encodee.png",
                mime="image/png"
            )
        else:
            st.error("Échec")
            os.unlink(tmp_input_path)
            
    except Exception as e:
        st.error(f"Erreur: {str(e)}")


def decode_process(uploaded_file, password):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        crypted_message = decode_message_from_image(tmp_path)
        
        if crypted_message is None:
            st.error("Aucun message trouvé")
            os.unlink(tmp_path)
            return
        
        original_message = vigenere_cipher(crypted_message, password, cipher=False)
        
        os.unlink(tmp_path)
        
        st.success("Décodé")
        st.text_area("Message:", value=original_message, height=100, disabled=True)
        
    except Exception as e:
        st.error(f"Erreur: {str(e)}")


if __name__ == "__main__":
    main()