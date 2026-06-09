import pandas as pd
import io
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
import logging

from app.core.exceptions import FileValidationError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
CHUNK_SIZE = 1024 * 1024  # 1 MB
EXTENSIONES_VALIDAS = {"csv", "xlsx", "xls"}
ENCODINGS_CSV = ["utf-8", "latin-1", "cp1252"]


def _sanitize_filename(name: str) -> str:
    return name.replace("\n", "").replace("\r", "")[:200]


class JiraFileReader:

    @staticmethod
    async def leer_archivo(archivo: UploadFile) -> pd.DataFrame:
        if not archivo.filename:
            raise FileValidationError("El archivo no tiene nombre.")

        safe_name = _sanitize_filename(archivo.filename)
        logger.info(f"Ingestando archivo: {safe_name}")

        extension = archivo.filename.rsplit(".", 1)[-1].lower()
        if extension not in EXTENSIONES_VALIDAS:
            raise FileValidationError(
                f"Formato '.{extension}' no admitido. Usa: {', '.join(sorted(EXTENSIONES_VALIDAS))}"
            )

        try:
            chunks = []
            total_size = 0
            while True:
                chunk = await archivo.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise FileValidationError(
                        f"El archivo excede el límite de {MAX_FILE_SIZE // (1024 * 1024)} MB."
                    )
                chunks.append(chunk)

            contenido = b"".join(chunks)
            buffer = io.BytesIO(contenido)

            if extension == "csv":
                df = await JiraFileReader._leer_csv(buffer)
            else:
                df = await run_in_threadpool(pd.read_excel, buffer)

            if df.empty:
                raise FileValidationError("El archivo está vacío.")

            logger.info(f"Archivo {extension} procesado. Filas: {len(df)}")
            return df

        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Error durante la lectura: {e}")
            raise FileValidationError(f"No se pudo procesar el archivo: {e}") from e

    @staticmethod
    async def _leer_csv(buffer: io.BytesIO) -> pd.DataFrame:
        for encoding in ENCODINGS_CSV:
            buffer.seek(0)
            try:
                return await run_in_threadpool(
                    pd.read_csv, buffer, encoding=encoding
                )
            except (UnicodeDecodeError, UnicodeError):
                logger.warning(
                    f"Falló lectura CSV con encoding {encoding}, probando siguiente..."
                )
        raise FileValidationError(
            f"No se pudo leer el CSV con ninguno de los encodings probados: {ENCODINGS_CSV}"
        )
