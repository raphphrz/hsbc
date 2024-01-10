import numpy as np
import pandas as pd
import yfinance as yf

# Définir les poids pour chaque actif dans le portefeuille
weights = np.array([0.117214, 0.098225, 0.009114, 0.095910, 0.010035,0.079172,0.026196,0.040515,0.106378,0.055886,0.009404,0.165652,0.004722,0.014132,0.026346,0.005200,0.135899]) # Exemple de pondérations pour un portefeuille de 3 actifs

# Définir les symboles boursiers des actifs dans le portefeuille
symbols = ["aapl", "zs", "amzn", "avgo", "crm", "ddog", "googl", "crwd", "net","msft", "mdb", "nvda", "qcom", "tsm", "txn","amd","orcl"] # Exemple de symboles pour un portefeuille de 3 actifs

# Définir la date de début et de fin pour extraire les données de prix des actifs
start_date = '2020, 2, 28' # Exemple de date de début
end_date = '2023, 2, 28' # Exemple de date de fin

# Extraire les données de prix des actifs à partir de Yahoo Finance
prices = yf.download(symbols, start=start_date, end=end_date)['Adj Close']

# Calculer les rendements pour chaque actif
returns = prices.pct_change().dropna()

# Calculer les rendements pondérés pour le portefeuille
portfolio_returns = np.dot(returns, weights)

# Définir le niveau de confiance pour la VaR
confidence_level = 0.95 # Exemple de niveau de confiance de 95%

# Définir le nombre d'itérations pour la simulation de Monte Carlo
num_iterations = 10000

# Calculer la VaR à l'aide d'une simulation de Monte Carlo
var = np.percentile(portfolio_returns, 100 * (1 - confidence_level))

# Enregistrer les résultats dans un fichier CSV
results = pd.DataFrame({'VaR': [var]})
results.to_csv('var_results.csv', index=False)