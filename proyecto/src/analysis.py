import pandas as pd
import numpy as np
from typing import Dict, Tuple
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

def project_level_summary(projects: pd.DataFrame, issuance: pd.DataFrame) -> pd.DataFrame:
    agg = issuance.groupby("project_id").agg(
        true_total=("true_reduction_tCO2", "sum"),
        reported_total=("reported_reduction_tCO2", "sum"),
        issued_total=("issued_credits", "sum"),
        retired_total=("retired_credits", "sum"),
        buffer_total=("buffer_credits", "sum"),
        over_total=("overcrediting_tCO2", "sum"),
        risk_events=("delivery_risk_flag", "sum"),
    ).reset_index()

    df = projects.merge(agg, on="project_id", how="left")

    df["over_rate"] = np.where(df["reported_total"] > 0, df["over_total"] / df["reported_total"], 0.0)
    df["retire_rate"] = np.where(df["issued_total"] > 0, df["retired_total"] / df["issued_total"], 0.0)

    # Score simple de “riesgo reputacional / calidad”
    df["integrity_risk_score"] = (
        0.45 * (1 - df["mrv_quality"]) +
        0.25 * (1 - df["additionality_score"]) +
        0.20 * df["permanence_risk"] +
        0.10 * df["leakage_rate"]
    )

    return df.sort_values(["integrity_risk_score", "over_rate"], ascending=False)

def market_revenue(issuance: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    df = issuance.merge(prices, on="month", how="left")
    df["gross_revenue_usd"] = (df["retired_credits"] * df["price_usd"]).round(2)
    return df


def regression_analysis(df: pd.DataFrame, target: str, features: list, 
                       test_size: float = 0.2, model_type: str = 'linear',
                       random_state: int = 42) -> Dict:
    """
    Realiza análisis de regresión sobre un conjunto de datos.
    
    Args:
        df: DataFrame con los datos
        target: Nombre de la columna objetivo
        features: Lista de nombres de columnas a usar como características
        test_size: Proporción del conjunto de prueba (default: 0.2)
        model_type: Tipo de modelo ('linear', 'ridge', 'lasso')
        random_state: Semilla aleatoria para reproducibilidad
    
    Returns:
        Diccionario con resultados del modelo, métricas y predicciones
    """
    # Preparar datos
    X = df[features].copy()
    y = df[target].copy()
    
    # Eliminar valores nulos
    mask = ~(X.isnull().any(axis=1) | y.isnull())
    X = X[mask]
    y = y[mask]
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Escalar características
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Seleccionar modelo
    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'ridge':
        model = Ridge(alpha=1.0)
    elif model_type == 'lasso':
        model = Lasso(alpha=0.01)
    else:
        raise ValueError("model_type debe ser 'linear', 'ridge' o 'lasso'")
    
    # Entrenar modelo
    model.fit(X_train_scaled, y_train)
    
    # Predicciones
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Métricas de entrenamiento
    train_r2 = r2_score(y_train, y_pred_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_mae = mean_absolute_error(y_train, y_pred_train)
    
    # Métricas de prueba
    test_r2 = r2_score(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    # Validación cruzada
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, 
                                scoring='r2')
    
    # Coeficientes e importancia
    coefficients = pd.DataFrame({
        'feature': features,
        'coefficient': model.coef_,
        'abs_coefficient': np.abs(model.coef_)
    }).sort_values('abs_coefficient', ascending=False)
    
    # DataFrame con predicciones
    predictions = pd.DataFrame({
        'actual': y_test.values,
        'predicted': y_pred_test,
        'residual': y_test.values - y_pred_test,
        'abs_residual': np.abs(y_test.values - y_pred_test)
    })
    
    # Métricas consolidadas
    metrics = pd.DataFrame({
        'metric': ['R²', 'RMSE', 'MAE', 'CV_R²_mean', 'CV_R²_std'],
        'train': [train_r2, train_rmse, train_mae, np.nan, np.nan],
        'test': [test_r2, test_rmse, test_mae, cv_scores.mean(), cv_scores.std()]
    })
    
    return {
        'model': model,
        'scaler': scaler,
        'coefficients': coefficients,
        'metrics': metrics,
        'predictions': predictions,
        'feature_names': features,
        'target_name': target,
        'intercept': model.intercept_
    }


def multiple_regression_models(df: pd.DataFrame, 
                               regression_configs: list) -> Dict[str, Dict]:
    """
    Ejecuta múltiples modelos de regresión con diferentes configuraciones.
    
    Args:
        df: DataFrame con los datos
        regression_configs: Lista de diccionarios con configuraciones de regresión.
                          Cada dict debe tener 'name', 'target' y 'features'
    
    Returns:
        Diccionario con resultados de todos los modelos
    """
    results = {}
    
    for config in regression_configs:
        name = config['name']
        target = config['target']
        features = config['features']
        model_type = config.get('model_type', 'linear')
        
        print(f"\n🔄 Entrenando modelo: {name}")
        print(f"   Target: {target}")
        print(f"   Features: {len(features)} variables")
        
        try:
            result = regression_analysis(
                df=df,
                target=target,
                features=features,
                model_type=model_type
            )
            results[name] = result
            print(f"   ✓ R² test: {result['metrics'].loc[result['metrics']['metric']=='R²', 'test'].values[0]:.4f}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results[name] = {'error': str(e)}
    
    return results


def compare_models(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compara métricas de diferentes modelos de regresión.
    
    Args:
        results: Diccionario con resultados de modelos
    
    Returns:
        DataFrame comparativo con métricas de todos los modelos
    """
    comparison = []
    
    for name, result in results.items():
        if 'error' in result:
            continue
            
        metrics = result['metrics']
        test_r2 = metrics.loc[metrics['metric']=='R²', 'test'].values[0]
        test_rmse = metrics.loc[metrics['metric']=='RMSE', 'test'].values[0]
        test_mae = metrics.loc[metrics['metric']=='MAE', 'test'].values[0]
        cv_r2 = metrics.loc[metrics['metric']=='CV_R²_mean', 'test'].values[0]
        
        comparison.append({
            'model': name,
            'target': result['target_name'],
            'n_features': len(result['feature_names']),
            'test_R²': test_r2,
            'test_RMSE': test_rmse,
            'test_MAE': test_mae,
            'CV_R²': cv_r2
        })
    
    return pd.DataFrame(comparison).sort_values('test_R²', ascending=False)