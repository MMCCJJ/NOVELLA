import descarga_archivos_GD

def descargar_archivos_concretos(nombres_archivos, ruta_drive):
    """Descarga de Google Drive los archivos cuyos nombres son indicados como parámetro"""

    # Ruta al archivo que contiene la información de los archivos a descargar
    ruta_archivo_info = f'{ruta_drive}/archivos_info.txt'

    # Obtenemos la lista con la info de los archivos del fichero
    archivos_a_descargar = descarga_archivos_GD.procesar_archivo_info(ruta_archivo_info)

    # Filtramos la lista para obtener solo los elementos con esos nombres
    archivos_filtrados = [archivo for archivo in archivos_a_descargar if archivo[1].strip() in nombres_archivos]

    # Descargamos cada archivo
    for id_archivo, nombre_archivo, directorio_destino in archivos_filtrados:
        nombre_archivo_descargado, ruta_archivo_guardado = descarga_archivos_GD.descargar_archivo_directo(id_archivo, directorio_destino, nombre_archivo)
        print(f"Archivo {nombre_archivo_descargado} guardado en: {ruta_archivo_guardado}")