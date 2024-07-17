import streamlit as st
from PIL import Image
import piexif
import io

def load_image(image_file):
    img = Image.open(image_file)
    return img

def get_exif_dict(image):
    exif_bytes = image.info.get('exif', None)
    if exif_bytes:
        exif_dict = piexif.load(exif_bytes)
    else:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}
    return exif_dict

def exif_dict_to_bytes(exif_dict):
    return piexif.dump(exif_dict)

def update_exif(exif_dict, field, value):
    if field in exif_dict["0th"]:
        exif_dict["0th"][field] = value
    elif field in exif_dict["Exif"]:
        exif_dict["Exif"][field] = value
    elif field in exif_dict["GPS"]:
        exif_dict["GPS"][field] = value
    elif field in exif_dict["Interop"]:
        exif_dict["Interop"][field] = value
    return exif_dict

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

    tag_fields = {
        "0th": piexif.TAGS["0th"],
        "Exif": piexif.TAGS["Exif"],
        "GPS": piexif.TAGS["GPS"],
        "Interop": piexif.TAGS["Interop"],
    }

    updated_exif_dict = exif_dict.copy()

    for ifd_name, tags in tag_fields.items():
        st.subheader(ifd_name)
        for tag, desc in tags.items():
            if tag in exif_dict[ifd_name]:
                value = exif_dict[ifd_name][tag]
                new_value = st.text_input(f"{desc['name']} ({ifd_name}):", str(value))
                if new_value:
                    if isinstance(value, bytes):
                        new_value = new_value.encode()
                    updated_exif_dict[ifd_name][tag] = new_value

    if st.button("Sauvegarder les modifications"):
        exif_bytes = exif_dict_to_bytes(updated_exif_dict)
        img.save("edited_pic.jpg", exif=exif_bytes)
        st.success("Métadonnées mises à jour et image enregistrée sous 'edited_pic.jpg'")

        # Afficher le lien pour télécharger l'image éditée
        with open("edited_pic.jpg", "rb") as file:
            btn = st.download_button(
                label="Télécharger l'image modifiée",
                data=file,
                file_name="edited_image.jpg",
                mime="image/jpeg"
            )
