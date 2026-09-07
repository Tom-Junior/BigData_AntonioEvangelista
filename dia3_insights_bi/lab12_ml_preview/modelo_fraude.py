"""Modelos de fraude: Regressão Logística e Random Forest."""
from pathlib import Path
import duckdb
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "bigdata" / "techpay.duckdb"
OUT = ROOT / "avaliacao_final" / "etapa4_ml"

FEATURES = ["amount", "risk_score", "credit_score", "segment_idx", "channel_idx", "merchant_idx"]


def load_data():
    con = duckdb.connect(str(DB), read_only=True)
    try:
        return con.execute("""
            SELECT amount, risk_score, credit_score, segment, channel,
                   merchant_category, is_fraud
            FROM silver_transactions
        """).df()
    finally:
        con.close()


def prepare_features(df):
    result = df.copy()
    for source, target in [("segment", "segment_idx"), ("channel", "channel_idx"),
                           ("merchant_category", "merchant_idx")]:
        categories = {value: index for index, value in enumerate(sorted(result[source].unique()))}
        result[target] = result[source].map(categories).astype(float)
    X = result[FEATURES]
    y = result["is_fraud"].astype(int)
    return X, y


def train_models():
    data = load_data()
    X, y = prepare_features(data)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logistic = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    logistic.fit(X_train_scaled, y_train)
    logistic_prob = logistic.predict_proba(X_test_scaled)[:, 1]
    logistic_pred = (logistic_prob >= 0.5).astype(int)

    forest = RandomForestClassifier(
        n_estimators=30, random_state=42, class_weight="balanced", n_jobs=-1
    )
    forest.fit(X_train, y_train)
    forest_prob = forest.predict_proba(X_test)[:, 1]
    forest_pred = (forest_prob >= 0.5).astype(int)

    metrics = pd.DataFrame([
        {"modelo": "Regressão Logística", "auc": roc_auc_score(y_test, logistic_prob)},
        {"modelo": "Random Forest (numTrees=30)", "auc": roc_auc_score(y_test, forest_prob)},
    ])
    confusion = pd.DataFrame(
        confusion_matrix(y_test, logistic_pred, labels=[0, 1]),
        index=["Real 0 — não fraude", "Real 1 — fraude"],
        columns=["Predito 0", "Predito 1"],
    ).reset_index().rename(columns={"index": "classe"})
    coefficients = pd.DataFrame({"feature": FEATURES, "coefficient": logistic.coef_[0]})
    importances = pd.DataFrame({"feature": FEATURES, "importance": forest.feature_importances_})
    return metrics, confusion, coefficients, importances


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    metrics, confusion, coefficients, importances = train_models()
    metrics.to_csv(OUT / "metricas_modelos.csv", index=False)
    confusion.to_csv(OUT / "matriz_confusao_logistica.csv", index=False)
    coefficients.to_csv(OUT / "coeficientes_logistica.csv", index=False)
    importances.to_csv(OUT / "importancias_random_forest.csv", index=False)
    # Mantém o nome histórico usado na documentação.
    metrics.to_csv(OUT / "metricas.csv", index=False)
    coefficients.to_csv(OUT / "coeficientes.csv", index=False)
    print(metrics.to_string(index=False))
    print("\nMatriz de confusão — Regressão Logística (limiar 0.5):")
    print(confusion.to_string(index=False))
    print("\nCoeficientes:")
    print(coefficients.to_string(index=False))


if __name__ == "__main__":
    main()
