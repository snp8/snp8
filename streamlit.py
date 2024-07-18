from PIL import Image
import piexif
import exifread
import streamlit as st
import folium
from streamlit_folium import st_folium

def convert_to_dms(value):
    """
    Convertit des coordonnées décimales en degrés, minutes et secondes (DMS)
    """
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = (value - degrees - minutes / 60) * 3600
    return degrees, minutes, seconds

def create_gps_ifd(latitude, longitude):
    """
    Crée un GPS IFD (Image File Directory) pour les données EXIF
    """
    lat_deg, lat_min, lat_sec = convert_to_dms(latitude)
    lon_deg, lon_min, lon_sec = convert_to_dms(longitude)
    
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: [(lat_deg, 1), (lat_min, 1), (int(lat_sec * 100), 100)],
        piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: [(lon_deg, 1), (lon_min, 1), (int(lon_sec * 100), 100)],
    }
    return gps_ifd

# on charge l'image
image_path = '/pic.JPG'
image = Image.open(image_path)
st.image(image, caption='Image originale')

# on lit les métadonnées EXIF
with open(image_path, 'rb') as f:
    tags = exifread.process_file(f)

# on montre les métadonnées EXIF 
st.subheader('Métadonnées EXIF:')
for tag in tags.keys():
    if tag not in ('JPEGThumbnail', 'EXIF MakerNote'):
        st.write(f"{tag}: {tags[tag]}")

# formulaire de modification de la latitude et la longitude
st.subheader('Modifier latitude et longitude')
with st.form('modify_location'):
    latitude = st.number_input('Latitude')
    longitude = st.number_input('Longitude')
    submit = st.form_submit_button('Update')
    if submit:
        # on crée un nouveau IFD GPS
        gps_ifd = create_gps_ifd(latitude, longitude)
        
        # on prend les données EXIF existantes
        exif_dict = piexif.load(image.info['exif'])
        
        # on change le IFD GPS dans les données EXIF
        exif_dict['GPS'] = gps_ifd
        
        # on convertit les données EXIF en bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # on sauvegarde l'image éditée avec les nouvelles données GPS
        modified_image_path = '/modified_pic.JPG'
        image.save(modified_image_path, exif=exif_bytes)
        
        st.success('Image modifiée avec succès ! Une copie a été téléchargée sur votre machine.')

        # on crée une carte avec Folium
        m = folium.Map(location=[latitude, longitude], zoom_start=7)

        # on ajoute un Marker
        folium.Marker([latitude, longitude], icon=folium.Icon(color='red', icon='map-marker'), tooltip=f"<span style='font-size:16px;'>Coordinates: ({latitude}, {longitude})</span>").add_to(m)

        # on montre la carte dans Streamlit
        st_folium(m, width=700, height=500)

st.write("\n")
st.subheader("Les capitales européennes que j'ai visité.")
# on définit les coordonnées 
locations = [
    (50.8466, 4.3528, 'Brussels, Belgium'),
    (49.815764, 6.131514, 'Luxembourg City, Luxembourg'),
    (48.866667, 2.333333, 'Paris, France'),
    (52.520008, 13.404954, 'Berlin, Germany'),
    (51.507351, -0.127758, 'London, England'),
    (48.208174, 16.373819, 'Vienna, Austria'),
    (49.80090099, 15.47815249, 'Prague, Czech Republic'),
    (52.229676, 21.012229, 'Warsaw, Poland'),
    (53.349805, -6.26031, 'Dublin, Ireland'),
    (54.687157, 25.279652, 'Vilnius, Lithuania'),
]
# on initialise la carte centrée sur la première localisation 
m = folium.Map(location=locations[0][:2], zoom_start=5)

for i, (lat, lon, city) in enumerate(locations):
    popup_html = f'<div style="font-size: 16px; font-weight: bold;">{city}</div>'
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(icon='star', color='red')
    ).add_to(m)
    
    
    if i > 0:
        folium.PolyLine([(locations[i-1][0], locations[i-1][1]), (lat, lon)], color='blue').add_to(m)

# on montre la carte
st_data = st_folium(m, width=800, height=600)








