# NOVELLA
<code> PD1 </code>

### 1. Descripción del proyecto

El objetivo de este proyecto es desarrollar un sistema de aprendizaje automático que sea capaz de predecir qué libros tienen el potencial de convertirse en *bestsellers* en Estados Unidos. Para ello, nos basaremos en los datos históricos de libros que aparecen en la lista de bestsellers del New York Times, la cual se actualiza semanalmente.

Para más información sobre cómo se elabora esta lista, puedes consultar [About the Best Sellers](https://www.nytimes.com/books/best-sellers/methodology/).


### 2. Integrantes

- Carmen Fernández González
- Javier Martín Fuentes
- María Romero Huertas

### 3. Instrucciones de instalacion

**Clonación del repositorio**

En primer lugar, clona el repositorio de este proyecto en tu dispositivo utilizando el comando 

<code>git clone [URL del repositorio] </code>

 Si prefieres una interfaz gráfica, puedes apoyarte en aplicaciones como GitHub Desktop.

**Instalación de bibliotecas**

Asegúrate de tener instalado Python en tu dispositivo (preferiblemente con la versión 3.10 o superior). A continuación, instala las bibliotecas requeridas ejecutando el siguiente comando en la terminal, asegurándote de estar en el directorio raíz del proyecto:

<code> pip install -r requirements.txt </code>

**Ejecución del proyecto**

Una vez instaladas las dependencias, puedes ejecutar el proyecto. Cada una de la tareas (adquisición de los datos, limpieza, etc.) tiene su propio *main*, ejecútalos según sean tus necesidades. Tanto la etapa de adquisición como la de limpieza disponen de dos *main* cada una, ya que para obtener correctamente nuestros datos es necesario ir alternándolas. Por este motivo, el orden correcto de ejecución es el siguiente:

- <code> python main_adquisicion_1.py </code> - Descarga la lista de libros del NYT y de libros populares de GoodReads.

- <code> python main_limpieza_1.py </code> - Limpia los títulos, junta todos los libros y elimina duplicados.

- <code> python main_adquisicion_2.py </code> - Descarga información a partir de los títulos limpios de GoodReads, precios, GoogleTrends y datos de los autores de Wikipedia y GoodReads.

- <code> python main_limpieza_2.py </code> - Limpia el conjunto de libros y autores. Incluye tratamiento de valores nulos, creación de nuevas variables, formatea las fechas, elimina variables innecesarias y deja los datos listos para el entrenamiento del modelo.

Para trabajar con estos archivos, también puedes utilizar PyCharm. Simplemente abre PyCharm y carga el directorio del proyecto. Desde allí, puedes abrir y editar los archivos Python, ejecutarlos y depurarlos según sea necesario.

Por otro lado, hay ciertas partes del proyecto (como la exploración) para los que necesitarás tener Jupyter Notebook instalado. Ejecuta el servidor de Jupyter en el directorio del proyecto con el comando:

<code> jupyter notebook exploracion.ipynb </code>

También puedes utilizar Anaconda Navigator para abrir los notebooks. Abre Anaconda Navigator y selecciona Jupyter Notebook desde el menú. Luego, navega hasta el directorio del proyecto y abre el archivo de notebook desde la interfaz de Jupyter Notebook para explorar y ejecutar el código.

### 4. Fuentes de datos

- [The New York Times Best Sellers](https://www.nytimes.com/books/best-sellers/).

Extraemos una lista con los libros que se han convertido en bestsellers en Estados Unidos.

- [GoodReads](https://www.goodreads.com).

Obtenemos una lista de libros populares por mes de publicación. Asimismo, recopilamos información específica de cada libro (fecha de publicación, rating, géneros literarios a los que pertenece, etc.) así como de los autores. 

- [Wikipedia](https://es.wikipedia.org/wiki/Wikipedia:Portada).

Empleamos esta fuente para extraer información acerca de los autores (años en activo, sexo, nacionalidad, etc.).

- [Barnes&Noble](https://www.nytimes.com/books/best-sellers/).

La mayor librería de Estados Unidos. De ella sacamos los precios de los libros.

- [Google Trends](https://trends.google.es/trends/)

De esta fuente obtenemos medidas de popularidad de los libros.

### 5. Estructura del código

Dentro de la carpera *src*, que incluye todo el código de nuestro proyecto, encontrarás una serie de carpetas que se corresponden con distintas las distintas etapas. A continuación procedemos a detallar los módulos de cada una de ellas:

<code>**Carpeta _adquisicion_**</code>

Corresponde a la adquisición de los datos de las distintas fuentes.

- <code>librosNYT.py</code> - Recopila datos de los libros de la lista semanal de bestsellers del New York Times. Puedes especificarle el punto de partida (día, mes y año) y el número de semanas que quieres retroceder.

- <code>librosPopulares.py</code> - Recoge la lista mensual de libros publicados populares de GoodReads. Del mismo modo, puedes especificarle el mes y año de partida así como el número de meses en los que retroceder. 
- <code>goodreads.py</code> - Contiene funciones relacionadas con la adquisición de información específica de los libros en GoodReads.
- <code>goodreadsReviews.py</code> - Recopila ratings antes de una fecha dada de un libro específico en GoodReads mediante técnicas de web crawling.
- <code>barnesAndNoble.py</code> - Módulo que permite obtener el precio y su formato de un libro dado.
- <code>autoresWikipedia.py</code> - Permite extraer información específica de un autor desde su página de Wikipedia.
- <code>autoresGoodreads.py</code> - Permite extraer información específica de un autor desde su página de GoodReads.
- <code>googleTrends.py</code> - Recopila el interés a lo largo del tiempo en un timeframe especificado para un libro dado.

<code>**Carpeta _limpieza_**</code>

Contiene los módulos relacionados con la limpieza de los datos, su integración y la creación de nuevas variables. Contiene un único módulo <code>limpieza.py</code> con todas las funciones correspondientes.

<code>**Carpeta _exploracion_**</code>

Una vez completadas las dos etapas anteriores, se puede proceder a la exploración de los datos. Contiene dos notebooks:

- <code>exploracion.py</code> - Exploración de los datos relacionados con los libros.

- <code>exploracion_autores.py</code> - Exploración de los datos relacionados con los autores.


<code>**Carpeta _drive_**</code>

Cuenta con archivos relacionados con la descarga de los conjuntos de datos almacenados en Google Drive.






