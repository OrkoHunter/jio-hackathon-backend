"""Predict crop fertilizer based on location."""

import csv
import math


def getData(lat, lon) : 
    original_lat = lat
    original_long = lon

    #1. Get nearest loc data

    with open("unnati-data.csv") as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        min_dist = 1000000
        nearest_row = None
        for row in csv_reader:
            line_count += 1
            if line_count == 1:
                continue
            else:
                lat = float(row[3])
                long = float(row[4])
                dist = ((original_lat - lat)**2 + (original_long - long)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_row = row

    sand = float(nearest_row[7])
    clay = float(nearest_row[8])
    pH = float(nearest_row[9])
    carbon = float(nearest_row[10])

    # Predict values

    # For Rice N : P2O5 : K2O = 100:50:60 kg/ha

    BULK_DENSITY= 1.4 #g/cm^3
    DEPTH_RICE = 0.50 #cm

    totalNitorgen =  0.026 + 0.067*carbon



    totalPhosphorous = 0.7927 * math.e**(4.9922*carbon)

    nitrogen_based_fertilizers = {
        "Ammonium Sulphate": 20.7,
        "Urea":	45,
        "Ammonium Chloride": 26,
        "Ammonium Nitrate": 34,
        "Ammonium Sulphate Nitrate": 2.6,
        "Calcium Ammonium Nitrate (CAN)": 25,
        "Sodium Nitrate": 16,
        "Calcium Nitrate": 17,
        "Potassium Nitrate": 13,
        "Calcium cynamide": 212,
    }

    phosphorous_based_fertilizers = {
        "Single Superphosphate": 18,
        "Double Superphosphate": 32.5,
        "Triple Superphosphate": 47.5,
        "Basic Slage (India)": 5.5,
        "Dicalcium Phosphate": 37.5,
        "Rock Phosphate": 22.5,
    }

    nitrogen_based_result = {}

    for key, value in nitrogen_based_fertilizers.items():
        nitrogen_based_result[key] = "{0:.2f}".format(get_fertilizer_amount(20, value))

    phosphorous_based_result = {}

    for key, value in phosphorous_based_fertilizers.items():
        phosphorous_based_result[key] = "{0:.2f}".format(get_fertilizer_amount(10, value))

    return nitrogen_based_result, phosphorous_based_result

def get_fertilizer_amount(rec, nut_in_com):
    return (rec*100)/nut_in_com + (sand+clay+carbon+pH)%50

