import copy

import numpy as np
import pandas as pd
import xgboost as xgb
from colorama import Fore, Style, init, deinit
from src.Utils import Expected_Value


# from src.Utils.Dictionaries import team_index_current
# from src.Utils.tools import get_json_data, to_data_frame, get_todays_games_json, create_todays_games
init()
xgb_ml = xgb.Booster()
#xgb_ml.load_model('Models/XGBoost_Models/XGBoost_74.5%_ML.json')
xgb_ml.load_model('Models/XGBoost_Models/XGBoost_74.9%_ML-2.json')
xgb_uo = xgb.Booster()
#xgb_uo.load_model('Models/XGBoost_Models/XGBoost_57.9%_UO.json')
xgb_uo.load_model('Models/XGBoost_Models/XGBoost_58.9%_UO-6.json')


def xgb_runner(data, todays_games_uo, frame_ml, games, home_team_odds, away_team_odds):
    xgb_preds = {}
    ml_predictions_array = []

    for row in data:
        ml_predictions_array.append(xgb_ml.predict(xgb.DMatrix(np.array([row]))))

    frame_uo = copy.deepcopy(frame_ml)
    frame_uo['OU'] = np.asarray(todays_games_uo)
    data = frame_uo.values
    data = data.astype(float)

    ou_predictions_array = []

    for row in data:
        ou_predictions_array.append(xgb_uo.predict(xgb.DMatrix(np.array([row]))))

    count = 0
    f = open('/home/admin_/NBA-Machine-Learning-Sports-Betting/output.txt', "w+")
    f.write("---------------XGBoost Model Predictions---------------\n")
    for game in games:
        home_team = game[0]
        away_team = game[1]
        winner = int(np.argmax(ml_predictions_array[count]))
        under_over = int(np.argmax(ou_predictions_array[count]))
        winner_confidence = ml_predictions_array[count]
        un_confidence = ou_predictions_array[count]
        if winner == 1:
            winner_confidence = round(winner_confidence[0][1] * 100, 1)
            xgb_preds[home_team] = {'confidence': winner_confidence}
            if under_over == 0:
                un_confidence = round(ou_predictions_array[count][0][0] * 100, 1)
                f.write(home_team + f" ({winner_confidence}%)" + ' vs ' + away_team + ': ' + 'UNDER ' + str(todays_games_uo[count]) + f" ({un_confidence}%)\n")
                print(
                    Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL + ': ' +
                    Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(
                        todays_games_uo[count]) + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL)
            else:
                un_confidence = round(ou_predictions_array[count][0][1] * 100, 1)
                f.write(home_team + f" ({winner_confidence}%)" + ' vs ' + away_team + ': ' + 'OVER ' + str(todays_games_uo[count]) + f" ({un_confidence}%)\n")
                print(
                    Fore.GREEN + home_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL + ' vs ' + Fore.RED + away_team + Style.RESET_ALL + ': ' +
                    Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(
                        todays_games_uo[count]) + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL)
        else:
            winner_confidence = round(winner_confidence[0][0] * 100, 1)
            xgb_preds[away_team] = {'confidence': winner_confidence}
            if under_over == 0:
                un_confidence = round(ou_predictions_array[count][0][0] * 100, 1)
                f.write(home_team + ' vs ' + away_team + f" ({winner_confidence}%)" + ': ' + 'UNDER ' + str(todays_games_uo[count]) + f" ({un_confidence}%)\n")
                print(
                    Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL + ': ' +
                    Fore.MAGENTA + 'UNDER ' + Style.RESET_ALL + str(
                        todays_games_uo[count]) + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL)
            else:
                un_confidence = round(ou_predictions_array[count][0][1] * 100, 1)
                f.write(home_team + ' vs ' + away_team + f" ({winner_confidence}%)" + ': ' + 'OVER ' + str(todays_games_uo[count]) + f" ({un_confidence}%)\n")
                print(
                    Fore.RED + home_team + Style.RESET_ALL + ' vs ' + Fore.GREEN + away_team + Style.RESET_ALL + Fore.CYAN + f" ({winner_confidence}%)" + Style.RESET_ALL + ': ' +
                    Fore.BLUE + 'OVER ' + Style.RESET_ALL + str(
                        todays_games_uo[count]) + Style.RESET_ALL + Fore.CYAN + f" ({un_confidence}%)" + Style.RESET_ALL)
        count += 1
    print("--------------------Expected Value---------------------")
    f.write("--------------------Expected Value---------------------\n")
    count = 0
    for game in games:
        home_team = game[0]
        away_team = game[1]
        ev_home = float(Expected_Value.expected_value(ml_predictions_array[count][0][1], int(home_team_odds[count])))
        ev_away = float(Expected_Value.expected_value(ml_predictions_array[count][0][0], int(away_team_odds[count])))
        if home_team in xgb_preds:
                xgb_preds[home_team]['ev'] = ev_home
        if away_team in xgb_preds:
                xgb_preds[away_team]['ev'] = ev_away
        if ev_home > 0:
            f.write(home_team + ' EV: ' + str(ev_home) + '\n')
            print(home_team + ' EV: ' + Fore.GREEN + str(ev_home) + Style.RESET_ALL)
        else:
            f.write(home_team + ' EV: ' + str(ev_home) + '\n')
            print(home_team + ' EV: ' + Fore.RED + str(ev_home) + Style.RESET_ALL)

        if ev_away > 0:
            f.write(away_team + ' EV: ' + str(ev_away) + '\n')
            print(away_team + ' EV: ' + Fore.GREEN + str(ev_away) + Style.RESET_ALL)
        else:
            f.write(away_team + ' EV: ' + str(ev_away) + '\n')
            print(away_team + ' EV: ' + Fore.RED + str(ev_away) + Style.RESET_ALL)
        count += 1

    deinit()
    return xgb_preds
