import pandas as pd
import pyarrow.parquet as pq

import adquisicion.librosNYT as librosNYT
import adquisicion.librosPopulares as librosPopulares
import adquisicion.goodreads as goodreads
import adquisicion.barnesAndNoble as barnesAndNoble
import adquisicion.googleTrends as googleTrends

import adquisicion.autoresGoodreads as autoresGoodreads
import adquisicion.autoresWikipedia as autoresWiki

import limpieza.limpieza as limpieza
import limpieza.limpieza_autores as limpiezaAutores

def main():

    # --- LIBROS ---
    
    # Obtenemos los libros de la lista de bestsellers del NYT
    dfNYT = librosNYT.getBooksNYT()

    # Obtenemos los libros de la lista de populares de goodreads
    dfPopulares = librosPopulares.getPopularBooks()

    # Agrupamos por título los bestsellers
    dfBestsellers = limpieza.agruparTitulosBestsellers(dfNYT)

    # Eliminamos aquellos libros que estén en populares pero que no sean bestsellers
    dfPopulares = limpieza.eliminarCoincidencias(dfBestsellers, dfPopulares)
    
    # Combinamos los libros (se crea la columna potencialBS)
    dfLibros = limpieza.juntarLibros(dfBestsellers, dfPopulares)

    dfLibros = limpieza.corregirTitulos(dfLibros)
    dfLibros= limpieza.corregirAutores(dfLibros)

    # Eliminamos posibles parejas libro-autor duplicadas
    dfLibros = limpieza.eliminarDuplicados(dfLibros)

    # Obtenemos la información de GoodReads

    dfLibros = limpieza.gestionarFechasParaTrends(dfLibros)
    dfLibros = getInfoGoodReads(dfLibros)

    # Obtenemos los precios
    dfLibros = getPricesBN(dfLibros)

    # Obtenemos las medidas de tendencia de GoogleTrends
    dfLibros = googleTrends.getTrends(dfLibros)

    # --- Limpieza ---
    
    dfLibros = limpieza.corregirWeeksOnList(dfLibros)
    dfLibros = limpieza.limpiarSagas(dfLibros)
    dfLibros = limpieza.limpiarNumPaginas(dfLibros)

    # Creamos la columna WordsTitle
    dfLibros = limpieza.crearWordsTitle(dfLibros)

    # Imputamos precios
    dfLibros = limpieza.corregirType(dfLibros)
    dfLibros = limpieza.corregirPriceFormat(dfLibros)
    dfLibros = limpieza.imputarPrecios(dfLibros)

    dfLibros = limpieza.eliminarNulos(dfLibros)
    dfLibros = limpieza.eliminarColumnasInnecesarias(dfLibros)

    # Nos quedamos solo con aquellos libros de ficción que han ingresado en la lista por lo menos 20 días después de su publicación
    dfLibros = limpieza.soloFiccion(dfLibros)
    dfLibros = limpieza.eliminarBestsellersPrecoces(dfLibros)

    dfLibros.to_parquet("libros.parquet")

    # --- AUTORES ---

    # Obtenemos información de los autores a partir de la lista de libros
    dfAutoresWiki = autoresWiki.generarDfAutores(dfLibros)
    dfAutoresGoodreads = autoresGoodreads.generarDfAutoresGoodReads(dflibros)

    # Juntamos la información de ambos df y limpiamos los datos
    dfAutores = limpiaAutores(dfAutoresWiki, dfAutoresGoodreads)

    dfAutores.to_parquet('autores.parquet')


def getInfoGoodReads(dfLibros):
    df_info = dfLibros['Title'].apply(goodreads.getInfoLibro).apply(pd.Series)
    dfLibros = pd.concat([dfLibros, df_info], axis=1)
    return dfLibros

def getPricesBN(dfLibros):
    df_precios = pd.DataFrame(dfLibros['Title'].apply(barnesAndNoble.getPrice).tolist())
    dfLibros= pd.concat([dfLibros, df_precios], axis=1)
    return dfLibros

def getInfoGoodReadsPorPartes():
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
