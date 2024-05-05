import limpieza_autores as la
import pandas as pd

def main():
    
    """Realizamos la limpieza final sobre los autores y los unimos con el df de libros"""

    # --- AUTORES ---

    # Cargamos los csv con los datos de autores crudos
    dfAutores = pd.read_csv('autores.csv', index_col=0)

    # Corrige los nombres de los autores
    dfAutores = la.corregirAutores(dfAutores)

    # Generamos la nueva columna HasWikipedia
    dfAutores['HasWikipedia'] = dfAutores.apply(lambda row: la.hasWikipedia(row), axis=1)

    # Selecciona las columnas relevantes para el modelo
    dfAutores = dfAutores[['FullName', 'HasWikipedia', 'HasTwitter']]

    # Almacenamos el dataframe en formato parquet
    dfAutores.to_parquet('autores_limpios.parquet')

    # Hace un merge de ambos dataframe
    dfLibros = pd.read_csv('libros.csv')
    df_merged = pd.merge(dfLibros, dfAutores, left_on='Author', right_on='FullName', how='left')
    df_merged.to_csv('libros_autores.csv')

if __name__ == "__main__":
    main()