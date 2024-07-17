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

def to_deg(value, loc):
    """Convert decimal coordinates into degrees, minutes, and seconds."""
    if value < 0:
        loc_value = loc[0]
        value = -value
    else:
        loc_value = loc[1]

    deg = int(value)
    t1 = (value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60 * 10000)

    return (deg, min, sec), loc_value

def set_gps_location(exif_dict, lat, lon):
    """Add GPS information to exif data."""
    lat_deg, lat_ref = to_deg(lat, ['S', 'N'])
    lon_deg, lon_ref = to_deg(lon, ['W', 'E'])

    exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = [lat_deg[0], lat_deg[1], lat_deg[2]]
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = lon_ref
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = [lon_deg[0], lon_deg[1], lon_deg[2]]

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

    # Champs pour les coordonnées GPS
    st.subheader("Ajouter/modifier la position GPS")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")

    if st.button("Sauvegarder les modifications"):
        set_gps_location(updated_exif_dict, lat, lon)
        exif_bytes = exif_dict_to_bytes(updated_exif_dict)
        img.save("edited_image.jpg", exif=exif_bytes)
        st.success("Métadonnées mises à jour et image enregistrée sous 'edited_image.jpg'")

        # Afficher le lien pour télécharger l'image éditée
        with open("edited_image.jpg", "rb") as file:
            btn = st.download_button(
                label="Télécharger l'image modifiée",
                data=file,
                file_name="edited_image.jpg",
                mime="image/jpeg"
            )
