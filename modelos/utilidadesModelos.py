import pandas as pd
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import make_scorer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

from imblearn.over_sampling import SMOTENC
from imblearn.pipeline import Pipeline

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature


# --- CONSTANTES ---

# Semilla para los proceso aleatorios
SEED = 22

# Número de folds (k) para la validación cruzada
CV_FOLDS = 5

# Proporción del conjunto de test
TEST_SIZE = 0.3

# --- MÉTRICAS DE EVALUACIÓN --- 

# Función para calcular la sensibilidad
def sensitivity(y_true, y_pred):
    """Calcula la sensibilidad dados los valores verdaderos y los predichos"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tp / (tp + fn)

# Función para calcular la especificidad
def specificity(y_true, y_pred):
    """Calcula la especificidad dados los valores verdaderos y los predichos"""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tn / (tn + fp)

def generarMetricas():
    """Genera un diccinario con las métricas empleadas para evaluar los modelos"""

    # Convierte las funciones en funciones de puntuación para usar en RandomizedSearchCV
    sensitivity_scorer = make_scorer(sensitivity)
    specificity_scorer = make_scorer(specificity)

    # Contiene las métricas con las que evaluar los modelos
    return {'balanced_accuracy': 'balanced_accuracy',
            'sensitivity': sensitivity_scorer,
            'specificity': specificity_scorer}

METRICS = generarMetricas()

# --- ESTRATEGIA DE VALIDACIÓN ---

def getYX(df):
    """Devuelve los vectores y, X"""
    return df["Bestseller"], df.drop(columns="Bestseller", axis=1)

def separacionTrainTest(X, y):
    """Genera particiones estratificadas"""
    return train_test_split(X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)

def generarFoldsEstratificados():
    """Genera los folds estratificados"""
    return StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)

# --- TRANSFORMACIONES ---

def codificarPriceFormat(df):
    """Devuelve el df dado con la columna PriceFormat con One-Hot Encoding"""
    return pd.get_dummies(df, columns=['PriceFormat'], dtype = int)

def redondearVariables(X):
    """Redondea las variables (se usa tras apicar el SMOTE-NC)"""

    variablesRedondeo = ["WordsTitle", "NumPages", "SagaNumber", "PrevBestSellAuthor"]

    # Iteramos sobre las columnas especificadas y redondea sus valores
    for v in variablesRedondeo:
        if v in list(X.columns):
            X[v] = np.round(X[v])
    return X

def aplicarEscaladoRobusto(X_train, X_test, variablesTransformacion):
    """Transforma con escalado robusto en train y test las variables indicadas"""

    X_scaled_train = X_train.copy()
    X_scaled_test = X_test.copy()

    # Inicializamos RobustScaler
    scaler = RobustScaler()

    # Aplicamos el RobustScaler a los datos de entrenamiento y test
    X_scaled_train[variablesTransformacion] = scaler.fit_transform(X_scaled_train[variablesTransformacion])
    X_scaled_test[variablesTransformacion] = scaler.transform(X_scaled_test[variablesTransformacion])

    return X_scaled_train, X_scaled_test


# --- OVERSAMPLING ---

def generarSMOTENC(variablesCategoricas):
    """Dadas unas variables categóricas, devuelve el objeto de SMOTE-NC"""
    return SMOTENC(categorical_features = variablesCategoricas, random_state = SEED)

# --- ESTRATEGIAS DE BÚSQUEDA ---

def realizarGridSearchCV(estimador, param_grid, kf, X, y):
    """Realiza la estrategia de búsqueda Grid Search CV"""

    # Definimos la búsqueda en rejilla
    grid_search = GridSearchCV(estimator=estimador, param_grid=param_grid, cv=kf,
                            scoring=METRICS, refit = "balanced_accuracy", return_train_score=True, n_jobs=-1, error_score="raise")

    # Realizamos la exploración
    grid_search.fit(X, y)
    
    return grid_search

def realizarRandomizedSearchCV(estimador, param_dist, kf, X, y, iteraciones):
    """Realiza la estrategia de búsqueda Randomized Search CV, es importante especificar
    el número de iteraciones"""

    # Definimos la búsqueda aleatoria
    random_search = RandomizedSearchCV(
        estimator=estimador, param_distributions=param_dist, 
        n_iter=iteraciones, cv=kf, 
        scoring= METRICS, 
        refit = "balanced_accuracy",
        return_train_score=True, n_jobs = -1
    )

    # Realiza la exploración
    random_search.fit(X, y)

    return random_search

# --- CREACIÓN DEL PIPELINE ---

def generarPipeline(smotenc, modelo):
    """Devuelve el pipeline empleado para el entrenamiento de los modelos"""

    # Definimos el transformador para codificar la variable categórica 'PriceFormat'
    column_transformer = ColumnTransformer([
        ('ohe', OneHotEncoder(), ['PriceFormat'])
    ], remainder='passthrough')

    # Definimos el transformador de la función para redondear
    transformador_funcion = FunctionTransformer(func=redondearVariables)

    # Construimos el pipeline
    pipeline = Pipeline([
        ('smote', smotenc),
        ('redondear_variables', transformador_funcion),
        ('encoder', column_transformer),
        ('classifier', modelo)
    ])

    return pipeline

# --- ENTORNO MLFLOW ---

def inicializarMLFlow(experimento):
    """Inicializa el entorno de MLFLOW, estableciendo el experimento dado"""

    # Establece la base de datos sqlite cini MLFLOW_TRACKING_URI 
    os.environ['MLFLOW_TRACKING_URI'] = 'sqlite:///mlruns.db'

    # Establece la URI de seguimiento
    mlflow.set_tracking_uri('sqlite:///mlruns.db')

    # Obtenemos todos los experimentos
    experiment_ids = mlflow.search_runs().experiment_id.unique()

    # Imprimimos los experimentos
    for exp_id in experiment_ids:
        print(exp_id)
        
    # Definimos el experimento en el que guardar todas las ejecuciones
    mlflow.set_experiment(experiment_name = experimento)

def registrarResultadosMLFlow(nombreModelo, modelo, X, best_params, index_row, df_results, tags):
    """Registra los resultados en la base de datos con el entorno MLFlow"""

    # Registramos los resultados en MLFlow
    with mlflow.start_run():

        # Almacenamos los valores de los hiperparámetros
        for key, value in best_params.items():
            mlflow.log_param(key, value)

        # Registra las métricas de cada fold para cada métrica
        for metric in METRICS:
            
            M = metric.replace(" ", "_")
            
            # Media
            
            mlflow.log_metric(f"mean_train_{M}", df_results[f"mean_train_{M}"][index_row])
            mlflow.log_metric(f"mean_test_{M}", df_results[f"mean_test_{M}"][index_row])

            # Desviación típica
            mlflow.log_metric(f"std_train_{M}", df_results[f"std_train_{M}"][index_row])
            mlflow.log_metric(f"std_test_{M}", df_results[f"std_test_{M}"][index_row])

            for i in range(CV_FOLDS):

                # Resultados de entrenamiento en cada fold
                mlflow.log_metric(f"train_{M}fold{i}", df_results[f"split{i}_train_{M}"][index_row])
                # Resultados de validación en cada fold
                mlflow.log_metric(f"test_{M}fold{i}", df_results[f"split{i}_test_{M}"][index_row])

        # Clasifica el modelo
        for key, value in tags.items():
            mlflow.set_tag(key, value)

        # Infiere el signature del modelo, que describe el tipo de entrada y salida del modelo
        signature = infer_signature(X, modelo.best_estimator_.predict(X))

        # Registra el modelo
        model_info = mlflow.sklearn.log_model(
            sk_model=modelo,
            artifact_path="model",
            signature=signature,
            input_example=X,
            registered_model_name=nombreModelo,
        )

def registrarBaseline(modelo, scores, X, tags):
    """Registra un modelo baseline en la base de datos"""

    # Registramos los resultados en MlFlow
    with mlflow.start_run():
        
        # Métricas
        m = ["balanced_accuracy", "sensitivity", "specificity"]

        for metric in m:
            
            for fold in range(len(scores[f"train_{metric}"])):
                
                # Obtenemos las métricas de cada fold
                train_fold_metric = scores[f"train_{metric}"][fold]
                test_fold_metric = scores[f"test_{metric}"][fold]
                
                # Log the metric for each fold
                mlflow.log_metric(f"train_{metric}_fold_{fold+1}", train_fold_metric)
                mlflow.log_metric(f"test_{metric}_fold_{fold+1}", test_fold_metric)
                
            # Calculamos la media de los valores
            train_mean = np.mean(scores[f"train_{metric}"])
            test_mean = np.mean(scores[f"test_{metric}"])

            # Log the mean values for train and test sets
            mlflow.log_metric(f"train_{metric}_mean", train_mean)
            mlflow.log_metric(f"test_{metric}_mean", test_mean)

        # Clasifica el modelo
        for key, value in tags.items():
            mlflow.set_tag(key, value)

        # Infiere el signature del modelo, que describe el tipo de entrada y salida del modelo

        signature = infer_signature(X, modelo.predict(X))

        # Registra el modelo
        model_info = mlflow.sklearn.log_model(
            sk_model=modelo,
            artifact_path="rl_model",
            signature=signature,
            input_example=X,
            registered_model_name="BASELINE",
        )


