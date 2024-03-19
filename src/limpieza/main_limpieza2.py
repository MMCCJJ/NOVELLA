import pandas as pd

import limpieza.limpieza as limpieza
import limpieza_autores

def main():
    
    """Realizamos la limpieza final sobre los libros y los autores"""

    # --- LIBROS ---
    
    dfLibros = limpieza.corregirWeeksOnList(dfLibros)
    dfLibros = limpieza.limpiarSagas(dfLibros)
    dfLibros = limpieza.limpiarNumPaginas(dfLibros)

    # Creamos la columna WordsTitle
    dfLibros = limpieza.crearWordsTitle(dfLibros) # NO ESTÁ???

    # Imputamos precios
    dfLibros = limpieza.corregirType(dfLibros)
    dfLibros = limpieza.corregirPriceFormat(dfLibros)
    dfLibros = limpieza.imputarPrecios(dfLibros)

    dfLibros = limpieza.eliminarNulos(dfLibros)
    dfLibros = limpieza.eliminarColumnasInnecesarias(dfLibros)

    # Nos quedamos solo con aquellos libros de ficción que han ingresado en la lista por lo menos 20 días después de su publicación
    dfLibros = limpieza.soloFiccion(dfLibros)
    dfLibros = limpieza.eliminarBestsellersPrecoces(dfLibros)

    # Almacenamos el dataframe en formato parquet
    dfLibros.to_parquet("libros_limpios.parquet")

    # --- AUTORES ---

    # Cargamos los csv con los datos de autores crudos
    dfAutoresWiki = pd.read_csv('autores_wikipedia.csv', index_col=0)
    dfAutoresGoodreads = pd.read_csv('autores_goodreads.csv', index_col=0)

    # Juntamos la información de ambos df y limpiamos los datos
    dfAutores = limpieza_autores.limpiaAutores(dfAutoresWiki, dfAutoresGoodreads)

    # Almacenamos el dataframe en formato parquet
    dfAutores.to_parquet('autores_limpios.parquet')

if __name__ == "__main__":
    main()
