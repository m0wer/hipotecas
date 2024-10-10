import streamlit as st
import os
import tempfile
from pathlib import Path
import subprocess
from anthropic import Anthropic
import hashlib
import json


class Cache:
    def __init__(self, cache_file="analysis_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(
                self.cache, f, default=str
            )  # Use default=str to handle non-serializable objects

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
        self.save_cache()


def compute_file_hash(file_content):
    return hashlib.md5(file_content).hexdigest()


def perform_ocr(file_path: Path) -> str:
    try:
        # Try OCRmyPDF first
        subprocess.run(
            ["ocrmypdf", "--force-ocr", "-l", "spa", str(file_path), str(file_path)],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        st.warning(
            f"OCR con OCRmyPDF falló: {e}. Intentando con tesseract directamente."
        )

        # If OCRmyPDF fails, try tesseract directly
        try:
            output_file = file_path.with_suffix(".txt")
            subprocess.run(
                [
                    "tesseract",
                    str(file_path),
                    str(output_file.with_suffix("")),
                    "-l",
                    "spa",
                ],
                check=True,
            )
            with open(output_file, "r", encoding="utf-8") as f:
                return f.read()
        except subprocess.CalledProcessError as e:
            st.error(f"La extracción de texto con tesseract falló: {e}")
            return ""

    # If OCRmyPDF succeeds, use mutool to extract text
    try:
        subprocess.run(
            [
                "mutool",
                "draw",
                "-F",
                "txt",
                "-o",
                str(file_path.with_suffix(".txt")),
                str(file_path),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        st.error(f"La extracción de texto con mutool falló: {e}")
        return ""

    try:
        with open(file_path.with_suffix(".txt"), "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        st.warning(f"No se pudo decodificar {file_path}")
        return ""


def analyze_contract(text: str) -> str:
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""Analiza el siguiente texto de contrato hipotecario en español en busca de prácticas abusivas. 
    Identifica cualquier instancia de lo siguiente:
    1. Cláusulas Abusivas (incluyendo Cláusulas Suelo, Gastos de Formalización, Vencimiento Anticipado, Intereses de Demora Excesivos)
    2. Falta de Transparencia
    3. Prácticas Comerciales Desleales
    4. Problemas con los Índices de Referencia
    5. Doble Financiación
    6. Préstamos Multidivisa

    Para cada práctica identificada, cita el texto específico del contrato y explica por qué se considera abusiva.

    Texto del contrato:
    {text}
    """

    message = client.messages.create(
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="claude-3-sonnet-20240229",
    )

    return message.content[0].text


@st.cache_data
def get_or_analyze_contract(file_content, _cache):
    file_hash = compute_file_hash(file_content)
    cached_result = _cache.get(file_hash)

    if cached_result:
        st.info("Usando resultado de análisis en caché.")
        return cached_result

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = Path(tmp_file.name)

    extracted_text = perform_ocr(tmp_file_path)
    os.unlink(tmp_file_path)

    if extracted_text:
        analysis_result = analyze_contract(extracted_text)
        _cache.set(file_hash, analysis_result)
        return analysis_result
    else:
        return "No se pudo extraer texto del PDF."


def main():
    st.set_page_config(
        page_title="Analizador de Contratos Hipotecarios", page_icon="🏠"
    )
    st.title("Analizador de Contratos Hipotecarios en Español")

    cache = Cache()

    uploaded_file = st.file_uploader("Sube un archivo PDF", type="pdf")

    if uploaded_file is not None:
        file_content = uploaded_file.read()

        with st.spinner("Procesando el PDF y analizando el contrato..."):
            analysis_result = get_or_analyze_contract(file_content, cache)

        st.subheader("Resultados del Análisis")
        st.write(analysis_result)


if __name__ == "__main__":
    main()
