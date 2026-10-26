from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core.database import DEFAULT_DB, init_db, list_records, save_analysis
from core.pipeline import process_document


st.set_page_config(page_title="OCR de comprobantes peruanos", page_icon="🧾", layout="wide")
init_db(DEFAULT_DB)

st.title("Análisis OCR y NLP de comprobantes peruanos")
st.caption("Extrae texto, identifica datos clave y conserva un historial estructurado en SQLite.")

with st.sidebar:
    st.header("Flujo de trabajo")
    st.write("1. Carga uno o más archivos.\n2. Procesa el contenido.\n3. Revisa los campos.\n4. Guarda o descarga resultados.")
    st.info("Los datos de demostración son sintéticos. No publiques comprobantes reales con datos personales.")

tab_process, tab_history, tab_method = st.tabs(["Procesar", "Base de datos", "Metodología"])

with tab_process:
    files = st.file_uploader(
        "Carga facturas, boletas o recibos",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
        help="Máximo recomendado: 10 páginas por PDF y 25 MB por archivo.",
    )
    if files and st.button("Procesar documentos", type="primary"):
        progress = st.progress(0)
        processed_docs = []
        for position, uploaded in enumerate(files, start=1):
            try:
                with st.status(f"Procesando {uploaded.name}") as status:
                    payload = uploaded.getvalue()
                    result = process_document(payload, uploaded.name)
                    result["filename"] = uploaded.name
                    result["mime_type"] = uploaded.type or "application/octet-stream"
                    processed_docs.append(result)
                    status.update(label=f"{uploaded.name} procesado", state="complete")
            except Exception as exc:
                st.error(f"No se pudo procesar {uploaded.name}: {exc}")
            progress.progress(position / len(files))
        st.session_state["processed_docs"] = processed_docs

    for position, result in enumerate(st.session_state.get("processed_docs", []), start=1):
        analysis = result["analysis"]
        entity = analysis["entities"]
        with st.expander(result["filename"], expanded=True):
            st.write(f"Páginas: {result['page_count']} | Confianza OCR: {result['confidence']:.1f}%")
            left, right = st.columns(2)
            with left:
                st.image(result["original_pages"][0], caption="Primera página original", use_container_width=True)
            with right:
                st.image(result["processed_pages"][0], caption="Primera página preprocesada", use_container_width=True)

            st.write(analysis["summary"])
            st.write("Palabras clave:", ", ".join(analysis["keywords"]) or "No detectadas")
            with st.form(f"review_{position}"):
                raw_text = st.text_area("Texto extraído", result["raw_text"], height=210)
                clean_text = st.text_area("Texto limpio", analysis["clean_text"], height=180)
                c1, c2, c3 = st.columns(3)
                ruc = c1.text_input("RUC emisor", entity.get("ruc_emisor") or "")
                supplier = c2.text_input("Razón social", entity.get("razon_social_emisor") or "")
                date = c3.text_input("Fecha", entity.get("fecha_emision") or "")
                c4, c5, c6 = st.columns(3)
                series = c4.text_input("Serie y número", entity.get("serie_numero") or "")
                currency = c5.selectbox("Moneda", ["PEN", "USD"], index=0 if entity.get("moneda") != "USD" else 1)
                total = c6.number_input("Total", min_value=0.0, value=float(entity.get("total") or 0.0), step=0.01)
                submitted = st.form_submit_button("Guardar revisión en la base", type="primary")
            if submitted:
                result["raw_text"] = raw_text
                analysis["clean_text"] = clean_text
                entity.update({
                    "ruc_emisor": ruc or None,
                    "razon_social_emisor": supplier or None,
                    "fecha_emision": date or None,
                    "serie_numero": series or None,
                    "moneda": currency,
                    "total": total,
                    "verified": 1,
                })
                document_id = save_analysis(
                    filename=result["filename"], file_hash=result["file_hash"], mime_type=result["mime_type"],
                    page_count=result["page_count"], raw_text=raw_text, result=analysis,
                    ocr_confidence=result["confidence"], ocr_language=result["language"],
                )
                st.success(f"Registro {document_id} guardado correctamente.")
            export = {
                "filename": result["filename"], "ocr_confidence": result["confidence"],
                "raw_text": result["raw_text"], **analysis,
            }
            st.download_button(
                "Descargar resultado JSON", json.dumps(export, ensure_ascii=False, indent=2),
                file_name=f"{result['filename'].rsplit('.', 1)[0]}_resultado.json",
                mime="application/json", key=f"json_{position}",
            )

with tab_history:
    records = list_records(DEFAULT_DB)
    frame = pd.DataFrame(records)
    if frame.empty:
        st.info("La base todavía no tiene registros.")
    else:
        st.metric("Documentos registrados", len(frame))
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.download_button(
            "Descargar base visible en CSV",
            frame.to_csv(index=False).encode("utf-8-sig"),
            file_name="historial_comprobantes.csv",
            mime="text/csv",
        )

with tab_method:
    st.subheader("Pipeline")
    st.markdown(
        """
        1. **Entrada:** imagen o PDF.
        2. **Preprocesamiento:** tamaño, grises, reducción de ruido, contraste y binarización.
        3. **OCR:** Tesseract en español y confianza promedio por palabra.
        4. **NLP:** limpieza, clasificación, extracción de entidades, palabras clave y resumen.
        5. **Validación:** corrección humana de campos antes del almacenamiento.
        6. **Salida:** SQLite y archivos CSV o JSON.
        """
    )
    st.write("Limitación principal: la precisión depende de la resolución, orientación, iluminación, tipografía y estructura del comprobante.")

