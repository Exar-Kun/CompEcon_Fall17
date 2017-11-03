#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 18:19:15 2017

@author: Alexandria
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from statsmodels.formula.api import ols
from sklearn import linear_model

#We now read in the data#
Fatal = pd.read_csv("Fatalities.csv")

#We now clean the Fatalities data 

Fatal = Fatal[Fatal["Subject's race"] != "Race unspecified"]

#We now create dummies for race on each police induced death
Fatal = pd.get_dummies(Fatal, columns=["Subject's race"])

#We now rename the zip code and year of death variable for the impending merge
Fatal["zipcode"] = Fatal["Location of death (zip code)"] 
Fatal["yr"] = Fatal['Date (Year)']

#We not read in the minority report dataset#
min_repot = pd.read_csv("GPSS Min rights Relations Final GA Aggregate.csv")

#We now drop the missing values for all our important variables#
min_repot = min_repot[min_repot.econ1.isnull() !=True]
min_repot = min_repot[min_repot.econ2.isnull() !=True]
min_repot = min_repot[min_repot.treat_hispanics.isnull() !=True]
min_repot = min_repot[min_repot.treat_blacks.isnull() !=True]
min_repot = min_repot[min_repot.treat_arabs.isnull() !=True]
min_repot = min_repot[min_repot.race_dialogue.isnull() !=True]


#Having done these things we now look to further clean the data#

#We now create specific race variables#
min_repot['raceban2'] = min_repot['raceban2'].where(min_repot['raceban2'] != 9)

min_repot = pd.get_dummies(min_repot, columns=['raceban2'])

min_repot['white'] = min_repot['raceban2_1.0']
min_repot['black'] = min_repot['raceban2_2.0']
min_repot['hispanic'] = min_repot['raceban2_3.0']
min_repot['asian'] = min_repot['raceban2_4.0']
min_repot['other'] = min_repot['raceban2_7.0']

#We now merge the datasets by zip code. The logic here being that one can now
#determine whether or not there was a police induced fatality near said person
#which might affect their responses#

Full = Fatal.merge(min_repot, on=('zipcode', "yr"), how='left')

#We now generate a death variable equal to 1 if there was a police related
#death in the same zipcode. 

Full["id"].fillna(value=0, inplace=True)

#We now create the Death Variable
Full['Death'] = (Full['id'] > 0).astype(int)


#Having done this we now create the dummy variables we will use as outcomes

#Blacks being treated fairly by the police
Full = Full[Full.bl_unfair_police.isnull() != True]
Full = pd.get_dummies(Full, columns=["bl_unfair_police"])

Full["Unfair_2_Blacks"] = Full["bl_unfair_police_2"]
Full["Fair_2_Blacks"] = Full["bl_unfair_police_1"]

#Having done this we now create yet another dummy variables we will use as an
#outcome (whether the problem between blacks and whites will be resolved)
Full = Full[Full.problem_blacks_whites.isnull() != True]
Full = pd.get_dummies(Full, columns=["problem_blacks_whites"])

Full["problem_forever"] = Full["problem_blacks_whites_1"]
Full["problem_resolved"] = Full["bl_unfair_police_2"]

#We also create dummy variables for urban status
Full = pd.get_dummies(Full, columns=["urban"])
Full["city"] = Full["urban_1"]
Full["suburbia"] = Full["urban_2"]
Full["rural"] = Full["urban_3"]


#Having created this variable, we now use it as the difference variable, to 
#run our difference in difference analysis.

##The logit model for fair treatment of blacks is below

y = Full["Unfair_2_Blacks"]

model = sm.Logit(y, Full[["Death", "age", "black", "white"]])

result = model.fit()

result.summary()

#We now perform another specification with the fairness of the police as the
#explanatory varibale and city level controls

model1 = sm.Logit(y, Full[["Death", "age", "black", "rural", "city", "suburbia"]])

result1 = model1.fit()

result1.summary()
    
#We now look at whether or not Death has any effect on the idea that there
#will always be black white racial tension

y3 = Full["problem_forever"]

X = Full[["age", "black", "white", "hispanic", "Death"]]

model2 = sm.Logit(y3, Full[["Death", "age", "black", "white"]])

result2 = model2.fit()

result2.summary()

#We now begin to output our results to Latex

#The first model
beginningtex = """\\documentclass{report}
\\usepackage{booktabs}
\\begin{document}"""
endtex = "\end{document}"

f = open('myreg.tex', 'w')
f.write(beginningtex)
f.write(result.summary().as_latex())
f.write(endtex)
f.close()

#The Second
beginningtex1 = """\\documentclass{report}
\\usepackage{booktabs}
\\begin{document}"""
endtex = "\end{document}"

f = open('myreg1.tex', 'w')
f.write(beginningtex1)
f.write(result1.summary().as_latex())
f.write(endtex)
f.close()

#The Third
beginningtex2 = """\\documentclass{report}
\\usepackage{booktabs}
\\begin{document}"""
endtex = "\end{document}"

f = open('myreg2.tex', 'w')
f.write(beginningtex2)
f.write(result2.summary().as_latex())
f.write(endtex)
f.close()