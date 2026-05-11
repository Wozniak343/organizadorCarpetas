from pathlib import Path

MAPA_CATEGORIAS = {
    "PDF": {"pdf"},
    "Imagenes": {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tif", "tiff", "svg", "heic"},
    "Videos": {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v"},
    "Musica": {"mp3", "wav", "flac", "aac", "ogg", "m4a"},
    "Documentos": {"doc", "docx", "odt", "rtf", "txt", "md", "xls", "xlsx", "ppt", "pptx", "csv"},
    "Comprimidos": {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"},
    "Ejecutables": {"exe", "msi", "bat", "cmd", "ps1", "app", "deb", "rpm", "dmg"},
    "Otros": set(),
}


def obtener_extension(nombre_archivo: str) -> str:
    return Path(nombre_archivo).suffix.lower().lstrip(".")


def obtener_categoria(nombre_archivo: str, mapa_categorias: dict[str, set[str]] | None = None) -> str:
    mapa = mapa_categorias or MAPA_CATEGORIAS
    extension = obtener_extension(nombre_archivo)

    for categoria, extensiones in mapa.items():
        if categoria == "Otros":
            continue
        if extension in extensiones:
            return categoria

    return "Otros"


def obtener_nombres_carpetas(mapa_categorias: dict[str, set[str]] | None = None) -> set[str]:
    mapa = mapa_categorias or MAPA_CATEGORIAS
    return {categoria.lower() for categoria in mapa}
