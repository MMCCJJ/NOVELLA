import pandas as pd

import limpieza.limpieza as limpieza
import limpieza.limpieza_autores as limpiezaAutores

def main():

    """Se juntan las dos listas de libros obtenidas en la parte de adquisición y se 
    juntan y limpian en un único dataframe"""

    # Cargamos las dos listas de libros que obtuvimos en la parte de adquisición
    dfNYT = pd.read_csv('librosNYT.csv', index_col=0)
    dfPopulares = pd.read_csv('librosPopulares.csv', index_col=0)

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

    # Almacenamos el dataframe resultante (en drive corresponde a libros1.csv y libros2.csv
    # ya que lo dividimos para facilitar el procesamiento)
    dfLibros.to_csv('libros.csv')

if __name__ == "__main__":
    main()
