import pandas as pd

import librosNYT
import goodreads
import barnesAndNoble
import googleTrends

def main():

    # Obtenemos los libros de la lista de bestsellers del NYT

    # Obtenemos los libros de la lista de populares de goodreads

    # Obtenemos la información de goodreads de cada libro
    getInfoPorPartes()

def getInfoPorPartes():
    """Obtiene la información de goodreads de los libros divididos en 2 partes para facilitar el procesamiento"""

    for i in range(2):
        print(f"COMENZANDO PROCESAMIENTO PARTE {i + 1}")
        
        LIBROS = pd.read_csv(f"LIBROS_parte{i + 1}.csv")
        df_info = LIBROS['Title'].apply(goodreads.getInfoLibro).apply(pd.Series)

        LIBROS = pd.concat([LIBROS, df_info], axis=1)

        LIBROS.to_csv(f"LIBROS_PROCESADOS_parte{i + 1}.csv")
        
        print(f"FINALIZANDO PROCESAMIENTO PARTE {i + 1}")
        
if __name__ == "__main__":
    main()