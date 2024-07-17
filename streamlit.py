import streamlit as st
from PIL import Image
import exifread
import io

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_dict(image):
    exif_dict = {}
    try:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        tags = exifread.process_file(img_byte_arr)
        for tag in tags.keys():
            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                exif_dict[tag] = tags[tag]
    except Exception as e:
        st.error(f"Erreur lors de l'extraction des métadonnées EXIF: {e}")
    
    return exif_dict

def update_exif(image, exif_dict):
    try:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        exif_bytes = exifread.makernote.remove_maker_notes(img_byte_arr.getvalue())
        
        for tag, value in exif_dict.items():
            if tag in exif_bytes:
                exif_bytes[tag] = exifread.classes.IfdTag(tag, value)
        
        return exif_bytes
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour des métadonnées EXIF: {e}")
        return None

st.title("Éditeur de métadonnées EXIF")

# Téléchargement de l'image
image_file = st.file_uploader("Téléchargez une image", type=["jpg", "jpeg"])

if image_file:
    img = load_image(image_file)
    st.image(img, caption='Image téléchargée', use_column_width=True)

    exif_dict = get_exif_dict(img)

    st.write("Métadonnées EXIF actuelles :")
    st.json(exif_dict)

    # Formulaire pour éditer les métadonnées
    st.header("Modifier les métadonnées EXIF")

    updated_exif_dict = exif_dict.copy()

    for tag, value in exif_dict.items():
        new_value = st.text_input(f"{tag}:", str(value))
        if new_value != str(value):
            updated_exif_dict[tag] = new_value

    if st.button("Sauvegarder les modifications"):
        updated_exif_bytes = update_exif(img, updated_exif_dict)
        if updated_exif_bytes:
            with open("edited_image.jpg", "wb") as edited_image_file:
                edited_image_file.write(updated_exif_bytes)
            st.success("Métadonnées mises à jour et image enregistrée sous 'edited_image.jpg'")

            # Afficher le lien pour télécharger l'image éditée
            with open("edited_image.jpg", "rb") as file:
                btn = st.download_button(
                    label="Télécharger l'image modifiée",
                    data=file,
                    file_name="edited_image.jpg",
                    mime="image/jpeg"
                )


