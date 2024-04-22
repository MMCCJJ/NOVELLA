import adquisicion.librosNYT as librosNYT
import adquisicion.librosPopulares as librosPopulares

def main():

    """Se obtienen, mediante web scraping, las dos listas de libros que usaremos 
    en nuestro proyecto"""

    # Obtenemos los libros de la lista de bestsellers del NYT
    dfNYT = librosNYT.getBooksNYT()
    dfNYT.to_csv('librosNYT.csv')

    # Obtenemos los libros de la lista de populares de goodreads
    dfPopulares = librosPopulares.getPopularBooks()
    dfPopulares.to_csv('librosPopulares.csv')

if __name__ == "__main__":
    main()
