from flask import Flask, request, render_template, send_file
import requests
import re
import os

app = Flask(__name__)

def download_tiktok_video(media_url, output_path="video_tiktok.mp4"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    session = requests.Session()

    try:
        # Obtener cookies iniciales
        session.get("https://www.tiktok.com", headers=headers)

        # Solicitud a la URL del contenido
        response = session.get(media_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"Error: No se pudo acceder a la URL, estado: {response.status_code}"

        # Buscar enlace del video
        video_match = re.search(r'"playAddr":"(https:[^"]+)', response.text)
        if not video_match:
            return "Error: No se encontró el enlace del video."

        # Procesar URL del video
        video_url = video_match.group(1).replace('\\u002F', '/')

        # Descargar el video
        video_response = session.get(video_url, headers=headers, stream=True)
        if video_response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
        else:
            return f"Error al descargar el video, estado: {video_response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        video_file = download_tiktok_video(url)
        if os.path.exists(video_file):
            return send_file(video_file, as_attachment=True)
        return video_file

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
