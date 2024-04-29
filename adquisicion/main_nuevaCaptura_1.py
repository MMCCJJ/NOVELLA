import adquisicion.librosNYT as librosNYT
import adquisicion.librosPopulares as librosPopulares

def main():

    # Obtenemos los libros de la lista de bestsellers del NYT
    NEW_DAY_INI = 5
    NEW_MONTH_INI = 5 # Mayo
    NEW_YEAR_INI = 2024
    NEW_WEEKS_BACK = 13

    dfNYT = librosNYT.getBooksNYT(NEW_DAY_INI, NEW_MONTH_INI, NEW_YEAR_INI, NEW_WEEKS_BACK)
    dfNYT.to_csv('nuevosNYTsucios.csv')

    # Obtenemos los libros de la lista de populares de goodreads
    NEW_MONTH_INI = 4 # Abril
    NEW_YEAR_INI = 2024
    NEW_MONTHS_BACK = 3

    dfPopulares = librosPopulares.getPopularBooks(NEW_MONTHS_BACK, NEW_MONTH_INI, NEW_YEAR_INI)
    dfPopulares.to_csv('librosPOPULARESsucios.csv')

if __name__ == "__main__":
    main()
