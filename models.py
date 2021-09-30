import matplotlib
import numpy as np
import pandas as pd
import numpy.random as rdm
from time import time
from functions import *
from scipy.stats import poisson
from scipy.optimize import minimize

def naive_model(*args):
    '''
    Modelo ingênuo, onde cada resultado tem probabilidade de 1/3 
    '''
    p = rdm.random()
    if p <= 1/3:
        return '1 x 0'
    elif p <= 2/3:
        return '0 x 0'
    else:
        return '0 x 1'
    
def seminaive_model(retrospect):
    '''
    Modelo semi-ingênuo.
    
    Recebe uma lista de retrospecto (em relação ao mandante)
    e retorna os placares de acordo com esse retrospecto.
    '''
    w = retrospect[0]
    d = sum(retrospect[:2])
    p = rdm.random()
    if p <= w:
        return '1 x 0'
    elif p <= d:
        return '0 x 0'
    else:
        return '0 x 1'
    
def observer_model(home, away):
    '''
    Modelo observador.
    
    Recebe os retrospectos do mandante e do visitante, retornando
    os resultados de forma proporcional a média dos resultados,
    ou seja, se o mandandante tem probabilidade de vitória de 50%
    em casa, enquanto o visistante tem probabilidade de derrota
    de 40% fora de casa, então o mandante ganha com probabilidade
    45%.
    '''
    home = np.array(home)
    away = np.array(away)
    prob = (home + away) / 2
    w = prob[0]
    d = np.sum(prob[:2])
    p = rdm.random()
    if p <= w:
        return '1 x 0'
    elif p <= d:
        return '0 x 0'
    else:
        return '0 x 1'
        
def simple_poisson_neutral(goals_mean):
    '''
    Modelo de Poisson simples, onde a média de gols de cada
    clube é metade da média de gols por partida, ou seja,
    os dois clubes tem a mesma "força".
    '''
    
    home_goals = poisson.rvs(goals_mean / 2)
    away_goals = poisson.rvs(goals_mean / 2)
    return str(home_goals) + ' x ' + str(away_goals)

def simple_poisson(means):
    '''
    Modelo de Poisson simples, onde a média de gols de cada
    clube depende apenas do mando de campo.
    '''
    
    home_mean, away_mean = means
    home_goals = poisson.rvs(home_mean)
    away_goals = poisson.rvs(away_mean)
    return str(home_goals) + ' x ' + str(away_goals)

def robust_poisson(home, away):
    '''
    Modelo de Poisson robusto, com cada time tendo uma força
    de ataque e uma de defesa, independentemente do mando de
    campo.
    '''
    
    home_atk, home_def = home['Ataque'], home['Defesa']
    away_atk, away_def = away['Ataque'], away['Defesa']
    home_goals = poisson.rvs(home_atk / away_def)
    away_goals = poisson.rvs(away_atk / home_def)
    return str(home_goals) + ' x ' + str(away_goals)

def more_robust_poisson(home, away):
    '''
    Modelo de Poisson mais robusto, com cada time tendo uma
    força de ataque e uma de defesa, dependente do mando de
    campo.
    '''
    
    home_atk, home_def = home['Ataque'], home['Defesa']
    away_atk, away_def = away['Ataque'], away['Defesa']
    home_goals = poisson.rvs(home_atk / away_def)
    away_goals = poisson.rvs(away_atk / home_def)
    return str(home_goals) + ' x ' + str(away_goals)

def forgetting_poisson(home, away):
    '''
    Modelo de Poisson com esquecimento, com cada time tendo
    uma força de ataque e uma de defesa, dependente do mando
    de campo e dos desempenhos recentes.
    '''
    
    home_atk, home_def = home['Ataque'], home['Defesa']
    away_atk, away_def = away['Ataque'], away['Defesa']
    home_goals = poisson.rvs(home_atk / away_def)
    away_goals = poisson.rvs(away_atk / home_def)
    return str(home_goals) + ' x ' + str(away_goals)
    
def train_naive_model(*args):
    '''
    Retorna um vetor de probabilidades para o modelo
    ingênuo (tudo igual a 1/3).
    '''
    return [1/3, 1/3, 1/3]

def train_seminaive_model(games, *args):
    '''
    Recebe um dataframe de jogos e retorna a proporção
    de jogos com cada resultado, na visão do mandante.
    '''
    
    results = [0, 0, 0]
    for i in games.index:
        result = games.loc[i, 'Result']
        if int(result[0]) > int(result[4]):
            results[0] += 1
        elif int(result[0]) == int(result[4]):
            results[1] += 1
        else:
            results[2] += 1
            
    results = np.array(results)
    return results / np.sum(results)

def train_observer_model(games, *args):
    '''
    Recebe um dataframe de jogos e retorna a proporção
    de jogos com cada resultado, por clube, separando
    os jogos em casa e fora, sempre na visão do mandante.
    '''
    
    results = {}
    for i in games.index:
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        if home not in results:
            results[home] = {'Casa' : [0, 0, 0], 'Fora' : [0, 0, 0]}
        
        if away not in results:
            results[away] = {'Casa' : [0, 0, 0], 'Fora' : [0, 0, 0]}
            
        result = games.loc[i, 'Result']
        if int(result[0]) > int(result[4]):
            results[home]['Casa'][0] += 1
            results[away]['Fora'][0] += 1
        elif int(result[0]) == int(result[4]):
            results[home]['Casa'][1] += 1
            results[away]['Fora'][1] += 1
        else:
            results[home]['Casa'][2] += 1
            results[away]['Fora'][2] += 1
            
    for club in results:
        for local in results[club]:
            results[club][local] = np.array(results[club][local])
            results[club][local] = results[club][local] / np.sum(results[club][local])
    
    return results

def train_simple_poisson_neutral(games, *args):
    '''
    Recebe um dataframe de jogos e retorna a média de
    gols por partida
    '''
    
    goals = 0
    for i in games.index:
        result = games.loc[i, 'Result']
        goals += int(result[0])
        goals += int(result[4])
        
    n_games = len(games)
    return goals / n_games

def train_simple_poisson_non_neutral(games, *args):
    '''
    Recebe um dataframe de jogos e retorna a média de
    gols por partida do mandante e do visitante
    '''
    
    home_goals = 0
    away_goals = 0
    for i in games.index:
        result = games.loc[i, 'Result']
        home_goals += int(result[0])
        away_goals += int(result[4])
        
    n_games = len(games)
    home_goals = home_goals / n_games
    away_goals = away_goals / n_games
    return [home_goals, away_goals]
    
def vet2force2(x, clubs):
    forces = {}
    for club in clubs:
        forces[club] = {'Ataque' : x[0], 'Defesa' : x[1]}
        x = x[2:]
        
    return forces

def force22vet(forces):
    x = []
    for club in forces:
        for force in forces[club]:
            x.append(forces[club][force])
    
    return x


def likelihood_simple_poisson(x, clubs, games):
    '''
    Recebe um vetor x de forças, onde a cada duas forças
    temos um time, e retorna a log verossimilhança
    negativa dessas forças com os dados
    '''
    
    forces = vet2force2(x, clubs)
    log_ver_neg = 0
    for i in games.index:
        result = games.loc[i, 'Result']
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        
        mu = forces[home]['Ataque'] / forces[away]['Defesa']
        log_ver_neg -= poisson.logpmf(int(result[0]), mu)
        
        mu = forces[away]['Ataque'] / forces[home]['Defesa']
        log_ver_neg -= poisson.logpmf(int(result[4]), mu)
        
    return log_ver_neg

def vet2force4(x, clubs):
    forces = {}
    for club in clubs:
        forces[club] = {'Casa' : {'Ataque' : x[0], 'Defesa' : x[1]},
                        'Fora' : {'Ataque' : x[2], 'Defesa' : x[3]}}
        x = x[4:]
        
    return forces

def force42vet(forces):
    x = []
    for club in forces:
        for local in forces[club]:
            for force in forces[club][local]:
                x.append(forces[club][local][force])
    
    return x

def likelihood_complex_poisson(x, clubs, games):
    '''
    Recebe um vetor x de forças, onde a cada quatro forças
    temos um time, e retorna a log verossimilhança negativa
    dessas forças com os dados
    '''
    
    forces = vet2force4(x, clubs)
    log_ver_neg = 0
    for i in games.index:
        result = games.loc[i, 'Result']
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        
        mu = forces[home]['Casa']['Ataque'] / forces[away]['Fora']['Defesa']
        log_ver_neg -= poisson.logpmf(int(result[0]), mu)
        
        mu = forces[away]['Fora']['Ataque'] / forces[home]['Casa']['Defesa']
        log_ver_neg -= poisson.logpmf(int(result[4]), mu)
        
    return log_ver_neg

def forgetting(t, c, k):
    return k / (c * np.log(t) + k)

def vet2force4getting(x, clubs):
    forces = {}
    for club in clubs:
        forces[club] = {'Casa' : {'Ataque' : x[0], 'Defesa' : x[1]},
                        'Fora' : {'Ataque' : x[2], 'Defesa' : x[3]}}
        x = x[4:]
    
    k, c = x
    
    return forces, k, c

def force4getting2vet(forces, k, c):
    x = []
    for club in forces:
        for local in forces[club]:
            for force in forces[club][local]:
                x.append(forces[club][local][force])
    
    x.append(k)
    x.append(c)
    
    return x

def likelihood_forgetting_poisson(x, clubs, games, date):
    '''
    Recebe um vetor x de forças, onde a cada quatro forças
    temos um time, e retorna a log verossimilhança negativa
    dessas forças com os dados
    '''
    
    games['New_Date_Num'] = date - matplotlib.dates.date2num(pd.to_datetime(games['New_Date'], dayfirst = True))
    
    forces, k, c = vet2force4getting(x, clubs)
    log_ver_neg = 0
    for i in games.index:
        result = games.loc[i, 'Result']
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        date = games.loc[i, 'New_Date_Num']
        if date > 0:
            weight = forgetting(date, c, k)

            mu = forces[home]['Casa']['Ataque'] / forces[away]['Fora']['Defesa']
            log_ver_neg -= poisson.logpmf(int(result[0]), mu) - np.log(weight)

            mu = forces[away]['Fora']['Ataque'] / forces[home]['Casa']['Defesa']
            log_ver_neg -= poisson.logpmf(int(result[4]), mu) - np.log(weight)
        
    return log_ver_neg
    
def train_simple_poisson(games, x0 = None, *args):
    clubs = []
    for i in games.index:
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        if home not in clubs:
            clubs.append(home)
            
        if away not in clubs:
            clubs.append(away)
            
        if len(clubs) == 20:
            break
            
    if x0 == None:
        x0 = [1 for i in range(40)]
    bounds = [(0, np.inf) for i in range(40)]
    res = minimize(likelihood_simple_poisson,
                   x0,
                   args = (clubs, games),
                   method = 'SLSQP',
                   bounds = bounds)

    x = res.x
    x = x / x[0]
    forces = vet2force2(x, clubs)

    return forces
    
def train_complex_poisson(games, x0 = None, *args):
    clubs = []
    for i in games.index:
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        if home not in clubs:
            clubs.append(home)
            
        if away not in clubs:
            clubs.append(away)
            
        if len(clubs) == 20:
            break
    
    if x0 == None:
        x0 = [1 for i in range(80)]
    bounds = [(0, np.inf) for i in range(80)]
    res = minimize(likelihood_complex_poisson,
                   x0,
                   args = (clubs, games),
                   method = 'SLSQP',
                   bounds = bounds)

    x = res.x
    x = x / x[0]
    forces = vet2force4(x, clubs)

    return forces
    
def train_forgetting_poisson(games, x0 = None, date = '01/01/2021', *args):
    clubs = []
    if type(date) == str:
    	date = matplotlib.dates.date2num(pd.to_datetime(date, dayfirst = True))
    
    for i in games.index:
        home = games.loc[i, 'Team 1']
        away = games.loc[i, 'Team 2']
        if home not in clubs:
            clubs.append(home)
            
        if away not in clubs:
            clubs.append(away)
            
        if len(clubs) == 20:
            break
            
    if x0 == None:
        x0 = [1 for i in range(82)]
    bounds = [(0, np.inf) for i in range(82)]
    res = minimize(likelihood_forgetting_poisson,
                   x0,
                   args = (clubs, games, date),
                   method = 'SLSQP',
                   bounds = bounds)

    x = res.x
    x = x / x[0]
    forces, k, c = vet2force4getting(x, clubs)
    
    return forces, k, c
    
def run_models(model, years, rounds, games, n_sims = 10000):
    '''
    Treina e executa os modelos dados para os anos e
    rodadas dadas.
    '''
    results = {}
    exe_times = {}
    if type(model) == list:
        for i in range(len(model)):
            result, exe_time = run_models(model[i], years, rounds, games, n_sims = n_sims)
            results[model[i][0]] = result
            exe_times[model[i][0]] = exe_time
            
        return results, exe_times
    
    name, model, train = model
    print(name)
    if model == forgetting_poisson:
        games['New_Date_Num'] = matplotlib.dates.date2num(pd.to_datetime(games['New_Date'],
                                                                         dayfirst = True))
        with_date = True
    else:
        with_date = False

    for year in years:
        print(year)
        if year not in results:
            results[year] = {}
            exe_times[year] = {}
        
        x0 = None
        for rd in rounds:
            if rd not in results[year]:
                results[year][rd] = {}
                exe_times[year][rd] = {}
            
            fit_games = pd.DataFrame()
            test_games = pd.DataFrame()
            
            train_time_i = time()
            if with_date:
                date = min(games.loc[((games['Round'] == rd) * (games['Year'] == year)), 'New_Date_Num'])
                fit_games = pd.concat([fit_games, games.loc[((games['New_Date_Num'] < date) * (games['Year'] == year))]],
                                    ignore_index = True)
                test_games = pd.concat([test_games, games.loc[((games['New_Date_Num'] >= date) * (games['Year'] == year))]],
                                    ignore_index = True)
                forces, k, c = train(fit_games, x0, date)
            else:
                fit_games = pd.concat([fit_games, games.loc[((games['Round'] <= rd) * (games['Year'] == year))]],
                                    ignore_index = True)
                test_games = pd.concat([test_games, games.loc[((games['Round'] > rd) * (games['Year'] == year))]],
                                    ignore_index = True)
                forces = train(fit_games, x0)
                
            train_time_f = time()
            exe_times[year][rd]['Treino'] = train_time_f - train_time_i
            
            sim_time_i = time()
            for i in range(n_sims):
                if type(forces) != dict:
                    for game in test_games.index:
                        test_games.loc[game, 'Result'] = model(forces)
                else:
                    for game in test_games.index:
                        home = forces[test_games.loc[game, 'Team 1']]
                        away = forces[test_games.loc[game, 'Team 2']]
                        if 'Casa' in home:
                            home = forces[test_games.loc[game, 'Team 1']]['Casa']
                            away = forces[test_games.loc[game, 'Team 2']]['Fora']
                            
                        test_games.loc[game, 'Result'] = model(home, away)
                        
                final = pd.concat([fit_games, test_games], ignore_index = True)
                table = classification(final)
                count = 1
                for club in table.index:
                    if club not in results[year][rd]:
                        results[year][rd][club] = {}
                        for pos in range(1, 21):
                            results[year][rd][club][pos] = 0
                            
                    results[year][rd][club][count] += 1
                    count += 1
                    
            sim_time_f = time()
            exe_times[year][rd]['Simulações'] = sim_time_f - sim_time_i
            
            if model == forgetting_poisson:
                x0 = force4getting2vet(forces, k, c)
            elif model == more_robust_poisson:
                x0 = force42vet(forces)
            elif model == robust_poisson:
                x0 = force22vet(forces)
            
    return results, exe_times
                