# PROYECTO NOVELLA
<code> Proyecto de Datos 1 </code>
***

### ▸ Índice

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Integrantes](#2-integrantes)
3. [Instrucciones de instalación](#3-instrucciones-de-instalación)
   - [Clonación del repositorio](#clonación-del-repositorio)
   - [Instalación de bibliotecas](#instalación-de-bibliotecas)
   - [Ejecución del proyecto](#ejecución-del-proyecto)
4. [Fuentes de datos](#4-fuentes-de-datos)
5. [Estructura del código](#5-estructura-del-código)
6. [Resultados y evaluación](#6-resultados-y-evaluación)
7. [Trabajo futuro](#7-trabajo-futuro)
8. [Agradecimientos](#8-agradecimientos)
### 1. Descripción del proyecto

El objetivo de este proyecto es desarrollar un sistema de aprendizaje automático que sea capaz de predecir qué libros tienen el potencial de convertirse en *bestsellers* en Estados Unidos. Para ello, nos basaremos en los datos históricos de libros que aparecen en la lista de bestsellers del New York Times, la cual se actualiza semanalmente.

Para más información sobre cómo se elabora esta lista, puedes consultar [About the Best Sellers](https://www.nytimes.com/books/best-sellers/methodology/).


### 2. Integrantes

- Carmen Fernández González
- Javier Martín Fuentes
- María Romero Huertas

### 3. Instrucciones de instalación

#### Clonación del repositorio

En primer lugar, clona el repositorio de este proyecto en tu dispositivo utilizando el comando 

<code>git clone [URL del repositorio] </code>

 Si prefieres una interfaz gráfica, puedes apoyarte en aplicaciones como GitHub Desktop.

#### Instalación de bibliotecas

Asegúrate de tener instalado Python en tu dispositivo (preferiblemente con la versión 3.10 o superior). A continuación, instala las bibliotecas requeridas ejecutando el siguiente comando en la terminal, asegurándote de estar en el directorio raíz del proyecto:

<code> pip install -r requirements.txt </code>

#### Ejecución del proyecto

Una vez instaladas las dependencias, puedes ejecutar el proyecto. 

Para trabajar con estos archivos, puedes utilizar PyCharm. Simplemente abre PyCharm y carga el directorio del proyecto. Desde allí, puedes abrir y editar los archivos Python, ejecutarlos y depurarlos según sea necesario.

Por otro lado, hay ciertas partes del proyecto para los que necesitarás tener Jupyter Notebook instalado. Ejecuta el servidor de Jupyter en el directorio del proyecto con el comando:

<code> jupyter notebook [nombre].ipynb </code>

También puedes utilizar Anaconda Navigator para abrir los notebooks. Abre Anaconda Navigator y selecciona Jupyter Notebook desde el menú. Luego, navega hasta el directorio del proyecto y abre el archivo de notebook desde la interfaz de Jupyter Notebook para explorar y ejecutar el código.


**F1. Adquisición y limpieza**

Tanto la etapa de adquisición como la de limpieza disponen de dos *main* cada una, ya que para obtener correctamente nuestros datos es necesario ir alternándolas. Por este motivo, el orden correcto de ejecución es el siguiente:

- <code> python main_adquisicion_1.py </code> - Descarga la lista de libros del NYT y de libros populares de GoodReads.
- <code> python goodreadsReviews.py </code> - Descarga las reviews históricas hasta la fecha elegida de GoodReads. Va en un módulo aparte debido a que el tiempo de ejecución es muy alto. Se pueden ejecutar el resto de módulos mientras este funciona porque la integración con el dataset final se realiza al final de todo el proceso.

- <code> python main_limpieza_1.py </code> - Limpia los títulos, junta todos los libros y elimina duplicados.

- <code> python main_adquisicion_2.py </code> - Descarga información a partir de los títulos limpios de GoodReads, precios, GoogleTrends y datos de los autores de Wikipedia y GoodReads.

- <code> python main_limpieza_2.py </code> - Limpia el conjunto de libros y autores. Incluye tratamiento de valores nulos, creación de nuevas variables, formatea las fechas, elimina variables innecesarias y deja los datos listos para el entrenamiento del modelo. Además, integra las reviews históricas con los datos ya procesados y limpios.

Del mismo modo ocurre para la etapa de captura de datos nuevos, que en algunos casos hay que sustituir los mains anteriores por los que tienen el infijo *nueva_captura* ya que se ajustan a distintas ventanas temporales / métodos más eficientes para la captura.

**F2. Exploración**

A continuación puedes explorar las distribuciones de estos datos con los *notebooks* <code>exploracion.ipynb</code> y <code>exploracion_autores.ipynb</code>. 

**F3. Entrenamiento de modelos**

Un paso previo a la selección de modelos candidatos fue realizar un análisis de la relevancia de las variables con respecto a la variable respuesta. Para ello se emplearon distintas métricas dependiendo de la naturaleza de las variables, como el coeficiente de correlación de Spearman, la información mutua o el test chi-2. De este modo pudimos descartar variables que no influían en la variable respuesta. Para ello, ejecuta <code>analisisVariablesRelevantes.ipynb</code>.

Se ajustaron los hiperparámetros de tres modelos distintos: uno de regresión logística con regularización, un Random Forest y un perceptrón multicapa. Cada modelo tiene asociado un *notebook* para la selección de variables (si así lo requiere) y otro para la obtención de los hiperparámetros óptimos. Se emplearon dos estrategias de exploración: en rejilla y aleatoria. Se probaron en torno a 200 combinaciones de hiperparámetros por estrategia.

Finalmente, se evaluaron los tres modelos con el mismo conjunto de prueba en `evaluacionModelosCandidatos.ipynb` y se eligió el perceptrón multicapa debido a sus métricas superiores. También se realiza el análisis por segmentos y la observación de las variables más relevantes de cada modelo.

**F4. Captura de nuevos datos**

Para la captura de datos nuevos se pueden emplear los mismos mains que en la adquisición y limpieza anterior, solo que en algunos casos hay que sustituir los mains anteriores por los que tienen el infijo *nueva_captura* ya que se ajustan a distintas ventanas temporales / métodos más eficientes para la captura.

**F5. Análisis de la deriva**

Se puede realizar un análisis de la deriva de los nuevos datos con el *notebook*`exploracion_variables_relevantes.ipynb`. En este se crean visualizaciones y se emplean tests estadísticos para verificar si ambas distribuciones de ciertas variables relevantes provienen o no de la misma población.

**F6. Evaluación del modelo**

Finalmente, se puede evaluar el modelo candidato seleccionado para continuar a la fase de producción comparándolo con una heurística y realizar un análisis por segmentos ejecutando el *notebook* `evaluacionModeloFinal.ipynb`.

### 4. Fuentes de datos

- [The New York Times Best Sellers](https://www.nytimes.com/books/best-sellers/)

Extraemos una lista con los libros que se han convertido en bestsellers en Estados Unidos.

- [GoodReads](https://www.goodreads.com)

Obtenemos una lista de libros populares por mes de publicación. Asimismo, recopilamos información específica de cada libro (fecha de publicación, rating, géneros literarios a los que pertenece, etc.) así como de los autores. 

- [Wikipedia](https://es.wikipedia.org/wiki/Wikipedia:Portada)

Empleamos esta fuente para extraer información acerca de los autores (años en activo, sexo, nacionalidad, etc.).

- [Barnes&Noble](https://www.nytimes.com/books/best-sellers/)

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
- <code>main_adquisicion_1.py</code> - Hace uso de los módulos *librosNYT* y *librosPopulares*.
- <code>main_adquisicion_2.py</code> - Utiliza los módulos *goodreads*, *barnesAndNoble*, *googleTrends*, *autoresGoodreads* y *autoresWiki*.
- `main_nuevaCaptura_1.py` - Hace uso de los módulos *librosNYT* y *librosPopulares* para recoger libros en fechas más recientes.

<code>**Carpeta _limpieza_**</code>

Contiene los módulos relacionados con la limpieza de los datos, su integración y la creación de nuevas variables.

- <code>limpieza.py</code> - Contiene las funciones correspondientes a los libros para imputar los precios faltantes, seleccionar los de categoría 'Ficción', etc..
- <code>limpieza_autores.py</code> - Contiene las funciones correspondientes a los autores para eliminar errores, añadir las columnas 'Country' y 'hasWikipedia', etc.
- <code>main_limpieza_1.py</code> - Usa únicamente el módulo *limpieza* para limpiar los datos de los libros.
- <code>main_limpieza_2.py</code> - Usa tanto el módulo de *limpieza* como el de *limpieza_autores*.
- `main_limpieza_autores_nuevaCaptura.py` - Utiliza el módulo *limpieza_autores* para limpiar los datos de autores. Añade la columna 'HasWikipedia', selecciona las variables relevantes para el modelo final e incluye los datos de autores a los datos de libros.

<code>**Carpeta _exploracion_**</code>

Una vez completadas las dos etapas anteriores, se puede proceder a la exploración de los datos. Contiene:

- <code>exploracion.ipynb</code> - Exploración de los datos relacionados con los libros.
- <code>exploracion_autores.ipynb</code> - Exploración de los datos relacionados con los autores.
- `exploracion_variables_relevantes.ipynb` - Análisis descriptivo de la variable respuesta y las variables más relevantes para el modelo elegido, comparando los datos de entrenamiento y los de nueva captura.

<code>**Carpeta _drive_**</code>

Cuenta con archivos relacionados con la descarga de los conjuntos de datos almacenados en Google Drive.

<code>**Carpeta _modelos_**</code>

- <code>analisisVariablesRelevantes.ipynb</code> - Contiene un análisis previo de variables relevantes (correlaciones, información mútua, test chi2).
- `evaluacionModelosCandidatos.ipynb` - Contiene la evaluación de los modelos candidatos obtenidos de cada una de las carpetas del directorio. Carga y prepara los datos para entrenar los modelos creados con información de mlflow. Después aplica las distintas estrategias de análisis de rendimiento especificadas en el índice del cuaderno.
- <code>utilidadesModelos.py</code> - Contiene funciones y métodos comunes a todos los modelos: constantes, métricas de evaluación, estrategia de validación, transformaciones, SMOTE-NC, creación del pipeline de entrenamiento, estrategias de búsqueda y la inicialización y registro de resultados en el entorno MLFlow.

Cada carpeta de este directorio se corresponde con un modelo distinto y contiene dos jupyter notebooks: uno relacionado con la selección de variables (solo si es necesario) y otro que entrena los modelos y guarda los resultados en MLFlow. Los modelos entrenados son una regresión logística con regularización, un Random Forest y un perceptrón multicapa.

<code>**Carpeta _evaluacion_**</code>
- `evaluacionModeloFinal.ipynb` - Aplica el modelo seleccionado sobre el conjunto de datos nuevos y compara las métricas de rendimiento con los datos de entrenamiento y la heurística.

### 6. Resultados y evaluación

Tras realizar el ajuste de hiperparámetros de tres modelos distintos con distintas estrategias de exploración, decidimos que el modelo que continuase a la fase de producción fuese el **perceptrón multicapa (MLP)** con los siguientes hiperparámetros:

- *activation* — 'logistic'
- *alpha* — 0.8773407884629941
- *early_stopping* — True
- *hidden_layer_sizes* — (150, 150)
- *learning_rate* — 'adaptive'
- *learning_rate_init* — 0.0023019050769459534
- *random_state* — 22

Para la evaluación de este modelo, decidimos compararlo frente a la heurística que definimos como «serán bestsellers aquellos libros cuyos autores hayan tenido al menos uno bestseller previo». Los resultados de la evaluación con la totalidad del conjunto de datos de entrenamiento y el conjunto de datos nuevos es el siguiente:

<table>
  <tr>
    <th>Modelo</th>
    <th>Datos</th>
    <th>Balanced Accuracy</th>
    <th>Sensibilidad</th>
    <th>Especificidad</th>
  </tr>
  <tr>
    <td rowspan="2">MLP</td>
    <td>Prueba (train)</td>
    <td>0.78</td>
    <td>0.73</td>
    <td>0.83</td>
  </tr>
  <tr>
    <td>Nuevos</td>
    <td>0.72</td>
    <td>0.52</td>
    <td>0.92</td>
  </tr>
  <tr>
    <td rowspan="2">Heurística</td>
    <td>Prueba (train)</td>
    <td>0.63</td>
    <td>0.29</td>
    <td>0.97</td>
  </tr>
  <tr>
    <td>Nuevos</td>
    <td>0.73</td>
    <td>0.50</td>
    <td>0.97</td>
  </tr>
</table>

Se puede observar que se observa una degradación de las métricas con el MLP en los datos nuevos mientras hay una mejora en las predicciones de la heurística. Esto se puede atribuir a varios factores, como cierto ruido añadido en la captura de los datos de GoogleTrends o los cambios en las distribución de los bestsellers previos que reflejó la prueba de Mann–Whitney U cuando realizamos el análisis de la deriva.

No obstante, descubrimos que en aquellos libros cuyos autores no habían tenido bestsellers previos nuestro modelo tenía cierto poder de predicción del cual la heurísica carecía completamente. Esto se puede observar en la siguiente tabla:

<table>
  <tr>
    <th>Modelo</th>
    <th>Datos</th>
    <th>Balanced Accuracy</th>
    <th>Sensibilidad</th>
    <th>Especificidad</th>
  </tr>
  <tr>
    <td rowspan="2">MLP</td>
    <td>Prueba (train) NB</td>
    <td>0.75</td>
    <td>0.65</td>
    <td>0.84</td>
  </tr>
  <tr>
    <td>Nuevos NB</td>
    <td>0.58</td>
    <td>0.22</td>
    <td>0.93</td>
  </tr>
  <tr>
    <td rowspan="2">Heurística</td>
    <td>Prueba (train) NB</td>
    <td>0.50</td>
    <td>0</td>
    <td>1</td>
  </tr>
  <tr>
    <td>Nuevos NB</td>
    <td>0.50</td>
    <td>0</td>
    <td>1</td>
  </tr>
</table>

### 7. Trabajo futuro

En base a los resultados, se abre un nuevo enfoque para nuestro proyecto: construir un modelo especializado en aquellos libros cuyos autores no han tenido bestsellers previos. Esto es debido a  que es el sector donde las heurísticas convencionales no funcionan pero que sin embargo su predicción de potencial bestseller podría ofrecerle una gran ventaja a la empresa con respecto a la competencia.

### 8. Agradecimientos

Queremos agradecer a Javier Arroyo por su supervisión de este proyecto. Sus detallados feedbacks y orientación constante han sido fundamentales para el desarrollo del mismo.