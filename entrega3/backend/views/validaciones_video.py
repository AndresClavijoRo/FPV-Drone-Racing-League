import os

from dataclasses import dataclass
from models import FileValidFormats


@dataclass
class VideoValido:
    valid: bool = False
    mensaje: str = ""


def validaciones_video(video) -> VideoValido:
    if video.filename == '':
        return VideoValido(False, "No se seleccionó ningún archivo")

    extension_file = video.filename.split('.')[-1]
    if not FileValidFormats.is_valid_format(extension_file):
        return VideoValido(False, f"Formato de archivo no permitido, formatos permitidos: {[format.value for format in FileValidFormats]}")

    max_file_size = 100 * 1024 * 1024  # 100MB
    if len(video.read()) > max_file_size:
        return VideoValido(False, "Tamaño de archivo excede el límite permitido")
    video.seek(0,os.SEEK_SET)
    return VideoValido(True)
