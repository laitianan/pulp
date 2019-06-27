from pulp import *
from pulp import LpProblem,LpMinimize,LpVariable,LpStatus,value
import pandas as pd 
import numpy as np 
time_part=[('8:00-9:00',0),('9:00-10:00',0),('10:00-11:00',0),('11:00-12:00',0),('14:00-15:00',0),('15:00-16:00',0),('16:00-17:00',0),('17:00-18:00',0),('18:00-19:00',0),('19:00-20:00',0),('20:00-21:00',0),('21:00-22:00',0)]

time_lpv_map={'8:00-9:00':1,'9:00-10:00':2,'10:00-11:00':3,'11:00-12:00':4,'14:00-15:00':5,'15:00-16:00':6,'16:00-17:00':7,'17:00-18:00':8,'18:00-19:00':9,'19:00-20:00':10,'20:00-21:00':11,'21:00-22:00':12}

order_sum = 14155

p_location =42
va =154
vb = 234

va =142.0471651
vb = 131.5924708

va=int(va)
vb=int(vb)
person_number=21
s0=0

#time_part=[('8:00-9:00', -1), ('9:00-10:00', -1), ('10:00-11:00', -1), ('11:00-12:00', 0), ('14:00-15:00', 0), ('15:00-16:00', 0), ('16:00-17:00', 0), ('17:00-18:00', 0), ('18:00-19:00', 0), ('19:00-20:00', 0), ('20:00-21:00', 0), ('21:00-22:00', 0)]
#order_sum,s0=8902.0, 14780.0

a1 = LpVariable("a01", lowBound=0,upBound=person_number,cat='Integer')
a2 = LpVariable("a02", lowBound=0,upBound=person_number,cat='Integer')
a3 = LpVariable("a03", lowBound=0,upBound=person_number,cat='Integer')
a4 = LpVariable("a04", lowBound=0,upBound=person_number,cat='Integer')
a5 = LpVariable("a05", lowBound=0,upBound=person_number,cat='Integer')
a6 = LpVariable("a06", lowBound=0,upBound=person_number,cat='Integer')
a7 = LpVariable("a07", lowBound=0,upBound=person_number,cat='Integer')
a8 = LpVariable("a08", lowBound=0,upBound=person_number,cat='Integer')
a9 = LpVariable("a09", lowBound=0,upBound=person_number,cat='Integer')
a10 = LpVariable("a10", lowBound=0,upBound=person_number,cat='Integer')
a11 = LpVariable("a11", lowBound=0,upBound=person_number,cat='Integer')
a12 = LpVariable("a12", lowBound=0,upBound=person_number,cat='Integer')

b1 = LpVariable("b01", lowBound=0,upBound=p_location,cat='Integer')
b2 = LpVariable("b02", lowBound=0,upBound=p_location,cat='Integer')
b3 = LpVariable("b03", lowBound=0,upBound=p_location,cat='Integer')
b4 = LpVariable("b04", lowBound=0,upBound=p_location,cat='Integer')
b5 = LpVariable("b05", lowBound=0,upBound=p_location,cat='Integer')
b6 = LpVariable("b06", lowBound=0,upBound=p_location,cat='Integer')
b7 = LpVariable("b07", lowBound=0,upBound=p_location,cat='Integer')
b8 = LpVariable("b08", lowBound=0,upBound=p_location,cat='Integer')
b9 = LpVariable("b09", lowBound=0,upBound=p_location,cat='Integer')
b10 = LpVariable("b10", lowBound=0,upBound=p_location,cat='Integer')
b11 = LpVariable("b11", lowBound=0,upBound=p_location,cat='Integer')
b12 = LpVariable("b12", lowBound=0,upBound=p_location,cat='Integer')



s1=LpVariable("s1", lowBound=-va,upBound=order_sum+s0,cat='Integer')
s2=LpVariable("s2", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s3=LpVariable("s3", lowBound=-va,upBound=order_sum+s0,cat='Integer')
s4=LpVariable("s4", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s5=LpVariable("s5", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s6=LpVariable("s6", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s7=LpVariable("s7", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s8=LpVariable("s8", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s9=LpVariable("s9", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s10=LpVariable("s10", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s11=LpVariable("s11", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
s12=LpVariable("s12", lowBound=-va,upBound=order_sum+s0 ,cat='Integer')
sum_p=LpVariable("sum_p", lowBound=0,cat='Integer')
#    sum_calc=LpVariable("sum_calc", lowBound=0,cat='Integer')



xa=[0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12]
xb=[0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12]
s=[s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12]

z =a1+a2*1.1+a3*1.2+a4*1.3+a5*1.4+a6*1.5+a7*1.6+a8*1.7+a9*1.8+a10*1.9+a11*2.0+a12*2.1+b1*1.0+b2*1.1+b3*1.2+b4*1.3+b5*1.4+b6*1.5+b7*1.6+b8*1.7+b9*1.8+b10*1.9+b11*2.0+b12*2.1

#    z =a1+a2+a3+a4+a5+a6+a7+a8+a9*1.8+a10*1.9+a11*2.0+a12*2.1+b1+b2+b3+b4+b5+b6+b7+b8+b9*1.8+b10*1.9+b11*2.0+b12*2.1

#for i in range(len(X)):
#    z += X[i]
    
prob = LpProblem('myPro', LpMinimize)
prob += z
que_restrain=[time_lpv_map[e[0]] for e in time_part if e[1]!=-1]

que_finish=[time_lpv_map[e[0]] for e in time_part if e[1]==-1]

for i in que_finish:
    prob +=xa[i]==0
    prob +=xb[i]==0
throld=True     
for index,i in enumerate(que_restrain):
    if index==len(que_restrain)-1:break
    prob +=xa[i]>=xa[que_restrain[(index+1)]]
    
    if throld:
        j=que_restrain[(index+1)]
#            prob +=xa[i]+xb[i]>=xa[j]+xb[j]
        
#        prob +=xa[j]<=xb[j]*2
        throld=False
#        if i>=6 :
#            prob +=xb[i]>=xb[que_restrain[(index+1)]]

prob +=sum_p==a1+a2+a3+a4+a5+a6+a7+a8+a9+a10+a11+a12+b1+b2+b3+b4+b5+b6+b7+b8+b9+b10+b11+b12
prob +=a1*va+a2*va+a3*va+a4*va+a5*va+a6*va+a7*va+a8*va+a9*va+a10*va+a11*va+a12*va>=order_sum
prob +=b1*vb+b2*vb+b3*vb+b4*vb+b5*vb+b6*vb+b7*vb+b8*vb+b9*vb+b10*vb+b11*vb+b12*vb>=order_sum+s0
#prob +=b1*vb+b2*vb+b3*vb+b4*vb+b5*vb+b6*vb+b7*vb+b8*vb+b9*vb+b10*vb+b11*vb+b12*vb-a1*va-a2*va-a3*va-a4*va-a5*va-a6*va-a7*va-a8*va-a9*va-a10*va-a11*va-a12*va>=0
prob +=a1+b1<=person_number
prob +=a2+b2<=person_number
prob +=a3+b3<=person_number
prob +=a4+b4<=person_number
prob +=a5+b5<=person_number
prob +=a6+b6<=person_number
prob +=a7+b7<=person_number
prob +=a8+b8<=person_number
prob +=a9+b9<=person_number
prob +=a10+b10<=person_number
prob +=a11+b11<=person_number
prob +=a12+b12<=person_number

prob +=a12==0
prob +=b1<=p_location
prob +=b2<=p_location
prob +=b3<=p_location
prob +=b4<=p_location
prob +=b5<=p_location
prob +=b6<=p_location
prob +=b7<=p_location
prob +=b8<=p_location
prob +=b9<=p_location
prob +=b10<=p_location
prob +=b11<=p_location
prob +=b12<=p_location

prob +=s1==s0-b1*vb
prob +=s2==a1*va+s1-b2*vb
prob +=s3==a2*va+s2-b3*vb
prob +=s4==a3*va+s3-b4*vb;
prob +=s5==a4*va+s4-b5*vb
prob +=s6==a5*va+s5-b6*vb
prob +=s7==a6*va+s6-b7*vb

prob +=s8==a7*va+s7-b8*vb
prob +=s9==a8*va+s8-b9*vb
prob +=s10==a9*va+s9-b10*vb
prob +=s11==a10*va+s10-b11*vb
prob +=s12==a11*va+s11-b12*vb

#    pct=0.8
#    prob +=b6<=p_location*pct
#    prob +=b7<=p_location*pct
#    prob +=b8<=p_location*pct
#    prob +=b9<=p_location*pct
#    prob +=b10<=p_location*pct
#    prob +=b11<=p_location*pct
#    prob +=b12<=p_location*pct

#    prob +=b6>=b7
#    prob +=b7>=b8
#    prob +=b8>=b9
#    prob +=b9>=b10
#    prob +=b10>=b11
#    prob +=b11>=b12


#prob +=sum_calc==b1*vb+b2*vb+b3*vb+b4*vb+b5*vb+b6*vb+b7*vb+b8*vb
#prob +=sum_calc>=0.99*order_sum+0.99*s0

#status =prob.solve(GUROBI(timeLimit=1200))
status = prob.solve()
#status =prob.solve(CPLEX_CMD(options=['set mip tolerances mipgap 0.25'])) 
print(status)
print(LpStatus[status])
print(value(prob.objective))  # 计算结果

for v in prob.variables():
    print(v.name, "=", v.varValue)