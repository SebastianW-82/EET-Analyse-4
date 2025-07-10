
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import io
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(layout="wide")
st.title("Analyse EET-Daten")

# Excel-Datei laden (muss im Projektverzeichnis liegen)
excel_path = "EET_Beispieldaten_100_ISINs_variiert.xlsx"

if not os.path.exists(excel_path):
    st.error(f"Die Datei '{excel_path}' wurde nicht gefunden. Bitte stelle sicher, dass sie im Projektverzeichnis liegt.")
else:
    data = pd.read_excel(excel_path)

    spalten = [
        'Mindestanteil nachhaltiger Investionen (in %)',
        'Tatsächlicher Anteil nachhaltiger Investitionen (in %)',
        'Mindestanteil taxonomiekonformer Investitionen (in %)',
        'Tatsächlicher Anteil taxonomiekonformer Investitionen (in %)',
        'Scope 1 Emissionen (in MT)',
        'Scope 2 Emissionen (in MT)',
        'Scope 3 Emissionen (in MT)'
    ]

    # ISIN-Eingabe mit schmalerer Box
    st.markdown("""
        <style>
        div[data-testid="stTextInput"] input {
            width: 300px;
        }
        </style>
    """, unsafe_allow_html=True)

    user_isin = st.text_input("Bitte geben Sie die ISIN ein:").strip().upper()

    if st.button("Analyse starten"):
        if user_isin not in data['ISIN'].values:
            st.error("ISIN nicht gefunden. Bitte überprüfen Sie Ihre Eingabe.")
        else:
            user_row = data[data['ISIN'] == user_isin].iloc[0]
            user_klassifikation = user_row['Klassifikation']
            subset = data[data['Klassifikation'] == user_klassifikation]

            klassifikation_label = f"Art. {int(user_klassifikation)}"

            st.markdown(f"""
                <div style='background-color:#1f77b4; padding: 15px; border-radius: 5px; width: fit-content;'>
                    <h4 style='color: white;'>Daten zur ISIN {user_isin}</h4>
                    <p style='color: white;'>Klassifikation: {klassifikation_label}</p>
                    <ul style='color: white;'>
                        {''.join([f'<li>{column}: {user_row[column]}</li>' for column in spalten])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # Buffer für kombinierten Report vorbereiten
            combined_figs = []

            for column in spalten:
                user_value = user_row[column]
                mean_val = subset[column].mean()
                median_val = subset[column].median()
                percentile = (subset[column] < user_value).mean() * 100
                num_values = subset[column].count()

                col1, col2 = st.columns([3, 1])

                with col1:
                    fig, ax = plt.subplots(figsize=(10, 4.5))
                    ax.hist(subset[column], bins=10, edgecolor='black', alpha=0.3, label='Verteilung')

                    ax.axvline(user_value, color='red', linestyle='--', linewidth=2, label='Wert zur ISIN')
                    ax.axvline(mean_val, color='green', linestyle=':', linewidth=2, label='Mittelwert')
                    ax.axvline(median_val, color='blue', linestyle='-.', linewidth=2, label='Median')

                    ax.set_xlabel(column)
                    ax.set_ylabel('Häufigkeit')
                    ax.legend()
                    ax.grid(True)

                    st.pyplot(fig)

                    # Grafik für PDF vorbereiten
                    fig.tight_layout()
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png')
                    buf.seek(0)
                    img = Image.open(buf).convert("RGB")

                    # Infokasten
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.load_default()

                    # Hauptinfo-Kasten
                    box_x = img.width - 850
                    box_y = 10
                    draw.rectangle([box_x, box_y, box_x + 400, box_y + 150], fill="#e0e0e0")
                    info_lines = [
                        f"ISIN: {user_isin}",
                        f"{column}: {user_value}",
                        f"Anzahl ISINs Peergroup: {num_values}",
                        f"Mittelwert: {mean_val:.1f}",
                        f"Median: {median_val:.1f}",
                        f"{percentile:.1f}% der Werte sind kleiner"
                    ]
                    for i, line in enumerate(info_lines):
                        draw.text((box_x + 10, box_y + 10 + i * 17), line, fill="black", font=font)

                    # Separater Legendenkasten
                    leg_x = img.width - 420
                    leg_y = 10
                    draw.rectangle([leg_x, leg_y, leg_x + 400, leg_y + 100], fill="#f0f0f0")
                    legend_lines = [
                        "Legende:",
                        "- Rot: Wert zur ISIN",
                        "- Grün: Mittelwert",
                        "- Blau: Median"
                    ]
                    for j, line in enumerate(legend_lines):
                        draw.text((leg_x + 10, leg_y + 10 + j * 17), line, fill="black", font=font)

                    combined_figs.append(img)

                with col2:
                    st.markdown(f"""
                    <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 5px;'>
                        <strong>ISIN:</strong> {user_isin}<br>
                        <strong>{column}:</strong> {user_value}<br>
                        <strong>Anzahl ISINs Peergroup:</strong> {num_values}<br>
                        <strong>Mittelwert:</strong> {mean_val:.1f}<br>
                        <strong>Median:</strong> {median_val:.1f}<br>
                        <strong>{percentile:.1f}%</strong> der Werte sind kleiner als der ISIN-Wert
                    </div>
                    """, unsafe_allow_html=True)

            if combined_figs:
                output_buffer = io.BytesIO()
                combined_figs[0].save(output_buffer, format="PDF", save_all=True, append_images=combined_figs[1:])
                output_buffer.seek(0)
                st.download_button(
                    label="📄 Gesamte Analyse als PDF herunterladen",
                    data=output_buffer,
                    file_name=f"{user_isin}_analyse.pdf",
                    mime="application/pdf"
                )
