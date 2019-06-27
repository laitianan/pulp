#from pulp import *
from pulp import LpProblem,LpMinimize,LpVariable,LpStatus,value
import pulp

order_sum =28472
p_location =32
va =125.1
vb = 165.1  
#va=int(va)
#vb=int(vb)
upBound_person=300
s0=4325

opponit_person= LpVariable("opponit_person", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a1 = LpVariable("a1", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a2 = LpVariable("a2", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a3 = LpVariable("a3", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a4 = LpVariable("a4", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a5 = LpVariable("a5", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a6 = LpVariable("a6", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a7 = LpVariable("a7", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)
a8 = LpVariable("a8", lowBound=0,upBound=upBound_person,cat=pulp.LpInteger)

b1 = LpVariable("b1", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b2 = LpVariable("b2", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b3 = LpVariable("b3", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b4 = LpVariable("b4", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b5 = LpVariable("b5", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b6 = LpVariable("b6", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b7 = LpVariable("b7", lowBound=0,upBound=p_location,cat=pulp.LpInteger)
b8 = LpVariable("b8", lowBound=0,upBound=p_location,cat=pulp.LpInteger)

s1=LpVariable("s1", lowBound=0)
s2=LpVariable("s2", lowBound=-va )
s3=LpVariable("s3", lowBound=-va )
s4=LpVariable("s4", lowBound=-va)
s5=LpVariable("s5", lowBound=-va )
s6=LpVariable("s6", lowBound=-va)
s7=LpVariable("s7", lowBound=-va )
s8=LpVariable("s8", upBound=0 )

sum_=LpVariable("sum_", lowBound=-va ,cat=pulp.LpInteger)

z =opponit_person
#z =a1+a2*1.1+a3*1.2+a4*1.3+a5*1.4+a6*1.5+a7*1.6+a8*1.7+b1*1.0+b2*1.1+b3*1.2+b4*1.3+b5*1.4+b6*1.5+b7*1.6+b8*1.7

    
prob = LpProblem('orderperson', LpMinimize)
prob += z
#prob +=a1+a2+a3+a4+a5+a6+a7+a8+b1+b2+b3+b4+b5+b6+b7+b8<=opponit_person*8
prob +=a1*va+a2*va+a3*va+a4*va+a5*va+a6*va+a7*va+a8*va>=order_sum
prob +=b1*vb+b2*vb+b3*vb+b4*vb+b5*vb+b6*vb+b7*vb+b8*vb>=order_sum+s0

prob +=a1+b1<=opponit_person
#prob +=a1+b1>=a2+b2
prob +=a2+b2<=opponit_person
prob +=a3+b3<=opponit_person
prob +=a4+b4<=opponit_person
prob +=a5+b5<=opponit_person
prob +=a6+b6<=opponit_person
prob +=a7+b7<=opponit_person
prob +=a8+b8<=opponit_person
#prob +=b8==0

prob +=b1<=p_location
prob +=b2<=p_location
prob +=b3<=p_location
prob +=b4<=p_location
prob +=b5<=p_location
prob +=b6<=p_location
prob +=b7<=p_location
prob +=b8<=p_location


prob +=s1==s0-b1*vb
prob +=s2==a1*va+s1-b2*vb
prob +=s3==a2*va+s2-b3*vb
prob +=s4==a3*va+s3-b4*vb
prob +=s5==a4*va+s4-b5*vb
prob +=s6==a5*va+s5-b6*vb
prob +=s7==a6*va+s6-b7*vb
prob +=s8==a7*va+s7-b8*vb

prob +=a1>=a2
prob +=a2>=a3
prob +=a3>=a4
prob +=a4>=a5
prob +=a5>=a6
prob +=a6>=a7
prob +=a7>=a8

prob +=sum_==a1+a2+a3+a4+a5+a6+a7+a8+b1+b2+b3+b4+b5+b6+b7+b8


prob +=a8==0
status = prob.solve()

print(status)
print(LpStatus[status])
print(value(prob.objective))  # 计算结果
if status==1:
    for v in prob.variables():
        print(v.name, "=", v.varValue)
    
    
