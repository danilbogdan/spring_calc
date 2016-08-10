# -*- coding: utf-8 -*-
from materials import material
import os, sys
from units import *
class Spring():
    """Производит расчет пружины:
    Пример использования:
    mat = {'d':0.05, 'G':, 'tensile_strength':50'}
    Входные параметры  mat, d_mid, d_in, d_out, n, nz, dx, F1, h, nu
    """

    def __init__(self, mat, d_mid, d_in, d_out, n, nz, x, F1, h, nu, l1=0):
        """"Производит расчет пружины при создании объекта"""
        self.d = mat['d']                                               #Диаметр проволоки (Импортируется из библиотеки материалов)
        self.G = mat['G']                                               #Модуль сдвига (Импортируется из библиотеки материалов)
        self.taudop = 0.5*mat['tensile_strength']                       #Допустимое касательное напряжение (Импортируется из библиотеки материалов)
        self.d_in = float(d_in)                                           #Внутреннний диаметр
        self.d_out = float(d_out)                                         #Наружный диаметр
        self.d_mid = float(d_mid)                                           #Средний диаметр
        self.n = float(n)                                               #Число рабочих витков пружины
        self.nz = float(nz)                                             #Число опорных витков
        self.x = float(x)                                               #Запас хода
        self.F1 = float(F1)                                             #Усилие при предварительном поджатии (рабочее усилие)
        self.h = float(h)                                               #Ход клапана
        self.nu = float(nu)                                             #Коэффициент устойчивости
        
        if self.d_mid == 0 and self.d_in == 0:
            self.d_out = d_out
            self.d_mid = self.fd_mid1(self.d, self.d_out)
            self.d_in = self.fd_in(self.d, self.d_mid)

        elif self.d_mid == 0 and self.d_out == 0:
            self.d_in = self.d_in
            self.d_mid = self.fd_mid2(self.d, self.d_in)
            self.d_out = self.fd_out(self.d, self.d_mid)

        elif self.d_in == 0 and self.d_out == 0:
            self.d_mid = self.d_mid
            self.d_in = self.fd_in(self.d, self.d_mid)
            self.d_out = self.fd_out(self.d, self.d_mid)
        self.c1 = self.fc1(self.d_mid, self.d)                            #Индекс пружины
        self.K = self.fK(self.c1)                                       #Коэффициент пружины
        self.n1 = self.fn1(self.n, self.nz)                             #Полное число витков
        self.l3 = self.fl3(self.n1, self.d)                             #Длина пружины в полностью поджатом состоянии
        self.dx = self.fdx(self.x, self.n1)                             #Межвитковый зазор
        if l1 == 0:
            self.l1 = self.fl1(self.l3, self.h, self.x)                     #Длина пружины в рабочем положении
        else:
            self.l1 = l1
            self.x = self.fx(self.l1, self.l3, self.h)
        self.s1 = self.fs1(self.F1, self.d_mid, self.n, self.G, self.d)   #Поджатие пружины при F1
        self.C = self.fC(self.s1, self.F1)
        self.l0 = self.fl0(self.l1, self.s1)                            #Длина свободной 
        self.s3 = self.fs3(self.l0, self.l3)                            #Поджатие пружины при F3
        self.F3 = self.fF3(self.F1, self.s3, self.s1)                   #Усилие поджатия до соприкосновения витков
        self.tau = self.ftau(self.K, self.F3, self.d_mid, self.d)         #Фактичесеое касательное напряжение
        self.stable = self.fstable(self.l0, self.d_mid, self.nu)          #Устойчивость пружины
        self.l2 = self.fl2(self.l1, self.h)
        self.F2 = self.fF2(self.h, self.C, self.F1)
                                        #ФУНКЦИИ

    def fc1(self, d_mid, d):
        'Индекс пружины'
        if d_mid > 2*d:
            return d_mid/d
        else:
            return None
    def fK(self, c1):
        'Коэффициент К'
        if c1:
            return ((4*c1-1)/(4*c1-4))+(0.615/c1)
        else:
            return None
    def fn1(self, n, nz):
        'Полное число витков'
        return n+nz

    def fd_in(self, d, d_mid):
        'Внутренний диаметр'
        return d_mid-d

    def fd_out(self, d, d_mid):
        'Наружный диаметр'
        return d_mid+d

    def fd_mid1(self, d, d_out):
        'Средний диаметр 1'
        return d_out-d

    def fd_mid2(self, d, d_in):
        'Средний диаметр 2'
        return d_in+d

    def fl3(self, n1, d):
        'Длина пружины в полностью сжатом состоянии'
        return (n1)*d

    def fdx(self, x, n1):
        'Межвитковый зазор'
        return x/(n1-1)

    def fl1(self, l3, h, dh):
        'Длина пружины в предварительно поджатом состоянии'
        return l3+h+dh
    def fx(self, l1, l3, h):
        'Запас хода'
        return l1-l3-h

    def fs1(self, F1, d_mid, n, G, d):
        'Предварительное поджатие'
        return (8*F1*(d_mid**3)*n)/(G*(d**4))

    def fl0(self, l1, L1):
        'Длина свободной пружины'
        return l1+L1

    def fs3(self, l0, l3):
        'Поджатие пружины до соприкосновения витков'
        return l0-l3

    def fl2(self, l1, h):
        return l1-h

    def fF2(self, h, C, F1):
        return F1+h*C

    def fF3(self, F1, L3, L1):
        'Усилие пружины при соприкосновении витков'
        if L1 > 0:
            return F1*(L3/L1)
        else:
            return 0

    def ftau(self, K, F3, d_mid, d):
        '''
        Возвращает касательное напряжение пружины если оно <= допустимого.
        Возвращает None если касательное напряжение больше допустимого.
        '''
        if K:
            tau = (2.55*K*F3*d_mid)/(d**3)
            #print ('%s <= %s'%(tau, self.taudop))
            if tau <= self.taudop:
                #print (True)
                return tau
            else:
                return None
        else:
            return None


    def fC(self, L1, F1):
        'Жесткость пружины'
        return F1/L1

    def fstable(self, l0, d_mid, nu):
        '''
        fstable(l0, d_mid, nu)
        Проверка устойчивости пружины, возвращает True если пружина устойчива
        '''
        return (l0/d_mid)<(2.62/nu)

                                        #test spring

#Initial data




#Material selection
class SpringCalc():
    '''
    Производит расчет пружины
    '''
    def __init__(self, mat=0, F1=0, h=0, dh=0, nz=2,
                    d_in=0, d_mid=0, d_out=0, stable=True, nu=0.5):
        '''
        mat - индекс материала, см. materials.py
        F1 - начальное усилие пружины
        h - ход пружины
        dh - запас хода
        nz - количество зашлифованых витков
        d_in - внутренний диаметр пружины
        d_mid - средний диаметр пружины
        d_out - наружный диаметр пружины
        nu - коэффициент закрепления концов пружины
        '''
        #Исходные данные для расчета
        self.F1 = F1                #Начальное усилие пружины
        self.material = mat    #Индекс материала пружины см. materials.py
        self.h = h                  #Ход пружины
        self.dh = dh                #Запас хода пружины
        self.nz = nz                #Количество зашлифованых витков
        self.d_in = d_in            #Внутренний диаметр пружины
        self.d_mid = d_mid          #Средний диаметр пружины
        self.d_out = d_out          #Наружный диаметр пружины
        self.nu = nu
        self.stable = stable
        self.spring_list = self.calc()
        #расчетные параметры пружины состоят из двух элементов
        #первый элемент массива это минимальное значение
        #второй - максимальное
        self.count = 0      #Количество найденых вариантов пружины
        self.n = [0, 0]     #Количество витков
        self.n1 = [0, 0]    #Полное количество витков
        self.F2 = [0, 0]    #Усилие при совершении хода
        self.F3 = [0, 0]    #Усилие при соприкосновении витков
        self.L1 = [0, 0]    #Длина пружины в поджатом состоянии
        self.L2 = [0, 0]    #Длина пружины при совершении хода
        #self.spring_list = []
        #self.filter_spring_list = []
    def calc(self):
        res = []                                                            #List of springs
        for d in material[self.material]['wire']:
            for i in range(1, 200):                                             #Число витков
                g = Spring({'d':d['d'],
                            'G':material[self.material]['G'],
                            'tensile_strength':d['tensile_strength']},
                            self.d_mid,
                            self.d_in,
                            self.d_out,
                            i/2, 
                            self.nz, 
                            self.dh, 
                            self.F1, 
                            self.h, 
                            self.nu)
                if self.stable:
                   
                    if g.stable: 
                        if g.tau:                                      #Choose requirements
                            res.append(g)
                else:
                    if g.tau:                                                   #Choose requirements
                        res.append(g)
        self.springs = res
        self.count = len(self.springs)
        self.maxmin()
        return self.springs
        
    def maxmin(self):
        '''
        Находит диапазон для расчитаных значений
        '''
        if len(self.springs)> 0:
            self.F2_min = self.springs[0].F2
            self.F2_max = self.springs[0].F2
            self.l1_min = self.springs[0].l1
            self.l1_max = self.springs[0].l1
            self.n_min = self.springs[0].n
            self.n_max = self.springs[0].n
            self.c_min = self.springs[0].C
            self.c_max = self.springs[0].C
            self.d_min = self.springs[0].d
            self.d_max = self.springs[0].d
            for i in self.springs:
                if i.F2 < self.F2_min:
                     self.F2_min = i.F2
                if i.F2 > self.F2_max:
                     self.F2_max = i.F2
                if i.l1 < self.l1_min:
                     self.l1_min = i.l1
                if i.l1 > self.l1_max:
                     self.l1_max = i.l1
                if i.n < self.n_min:
                     self.n_min = i.n
                if i.n > self.n_max:
                     self.n_max = i.n
                if i.C < self.c_min:
                     self.c_min = i.C
                if i.C > self.c_max:
                     self.c_max = i.C
                if i.d < self.d_min:
                     self.d_min = i.d
                if i.d > self.d_max:
                     self.d_max = i.d

        else:
            self.F2_min = 0
            self.F2_max = 0
            self.l1_min = 0
            self.l1_max = 0
            self.n_min = 0
            self.n_max = 0
            self.c_min = 0
            self.c_max = 0
    def filter(self, F2=None, n=None, F3=None, l1=None, l2=None):
        '''
        filter(self, F2=None, n=None, F3=None, l1=None, l2=None)
        F2 -> {'value':0, 'up_tolerance':0, 'un_tolerance':0}
        '''
        filter_springs = []
        for spring in self.springs:
            if l1:
                if l1['value'] and l1['up_tolerance'] == 0 and l1['un_tolerance'] == 0:
                    #нужно пересчитать пружину
                    pass
                    #print('L1=0')
                else:
                    #print ('L1 != 0')
                    if spring.l1 >= l1['value'] + l1['un_tolerance'] and spring.l1 <= l1['value'] + l1['up_tolerance']:
                        filter_springs.append(spring)
        print('l1 filtered')
        tmp = list(filter_springs)
        filter_springs = []
        for spring in tmp:
            if F2:
                if spring.F2 >= F2['value'] + F2['un_tolerance'] and spring.F2 <= F2['value'] + F2['up_tolerance']:
                    filter_springs.append(spring)
        print('F2 filtered')
        return filter_springs
    def find(self, d, n, l1):
        '''
        find(self, d, n, l1) -> Spring
        '''
        print('self.springs=', self.springs)
        if self.springs:
            for spring in self.springs:
                print('%s == %s'%(spring.d, d))
                if round(spring.d, 4) == round(d, 4) and round(spring.n, 1) == n and round(spring.l1, 4) == round(l1, 4):
                    return spring
        else:
            return None

#User input data
def inp_data():
    F1 = 180
    d_out = 28E-3
    h = 3E-3
    nu = 0.5
    x = 9E-3
    nz = 2
    d_in = 0
    d_mid = 0
    for i in range(0, len(material)):
        print ('%s - %s'%(i+1, material[i]['name']))

    mat = input('Выберите марку материала (1): ')
    try:
        mat = int(mat)
    except:
        mat = 1
    f1_ = input('Начальное усилие пружины F1, кгс (%s):'%(F1*0.1))
    if f1_:
        F1 = float(f1_)*10
    
    h_ = input('Ход h, мм (%s):'%(h*1000))
    if h_:
        h = float(h_)*1E-3
    
    x_ = input('Запас хода x, мм (%s):'%(x*1000))
    if x_:
        x = float(x_)*1E-3
    
    nz_ = input('Число опорных витков, 1,5 или 2 (%s):'%(nz))
    if nz_:
        nz = float(nz_)
    
    
    #Spring diameters
    
    print ('Диаметр пружины (задайте значение одного из трех диаметров Dвн, Dнар или Dср)')
    d_in_ = input('Dвн, мм (%s):'%(d_in*1000))
    if d_in_:
        d_in = float(d_in_)*1E-3
    d_out_ = input('Dнар, мм (%s):'%(d_out*1000))
    if d_out_:
        d_out = float(d_out_)*1E-3
    d_mid_ = input('Dср, мм (%s):'%(d_mid*1000))
    if d_mid_:
        d_mid = float(d_mid_)*1E-3
    print ("Пружина устойчива?")
    stable_ = input('y/n (n): ')
    if sys.platform == "win32":
        os.system('cls')
    else:
        os.system('clear')
    # (mat, d_mid, d_in, d_out, n, nz, dx, F1, h, nu):
    
    res = []                                                            #List of springs
    for d in material[mat-1]['wire']:
        for i in range(1, 200):                                             #Число витков
            g = Spring({'d':d['d'],
                        'G':material[mat-1]['G'],
                        'tensile_strength':d['tensile_strength']},
                        d_mid,d_in,d_out, i/2, nz, x, F1, h, nu)
            if stable_ == 'y':
                if g.stable and g.tau:                                      #Choose requirements
                    res.append(g)
            else:
                if g.tau:                                                   #Choose requirements
                    res.append(g)
    return res


#results

#print ('Результаты расчета')

def val_range(lis):
    if lis:
        val_list = {'min_n':lis[0].n, 'max_n':lis[0].n,
                    'min_l1':lis[0].l1, 'max_l1':lis[0].l1, 
                    'min_d':lis[0].d, 'max_d':lis[0].d, 
                    'min_c':lis[0].C, 'max_c':lis[0].C, 
                    'min_F2':lis[0].F2, 'max_F2':lis[0].F2}

    
        for i in lis:
            if i.l1 < val_list['min_l1']:
                val_list['min_l1'] = i.l1
            if i.l1 > val_list['max_l1']:
                val_list['max_l1'] = i.l1
            if i.d < val_list['min_d']:
                val_list['min_d'] = i.d
            if i.d > val_list['max_d']:
                val_list['max_d'] = i.d
            if i.C < val_list['min_c']:
                val_list['min_c'] = i.C
            if i.C > val_list['max_c']:
                val_list['max_c'] = i.C
            if i.F2 < val_list['min_F2']:
                val_list['min_F2'] = i.F2
            if i.F2 > val_list['max_F2']:
                val_list['max_F2'] = i.F2
            if i.n < val_list['min_n']:
                val_list['min_n'] = i.n
            if i.n > val_list['max_n']:
                val_list['max_n'] = i.n
        print ("  ")
        print ("Количество пружин: ", len(lis))
        print ("1. Количество витков n (%s..%s) "%(val_list['min_n'], val_list['max_n']))
        print ("2. Диаметр проволоки d, мм (%s..%s) "%(val_list['min_d']*1000, val_list['max_d']*1000))
        print ('3. l1, мм (%s..%s)'%(round(val_list['min_l1']*1000,2), round(val_list['max_l1']*1000,2)))
        print ("4. Жесткость C, кгс/мм (%s..%s)"%(round(val_list['min_c']/10000, 2), round(val_list['max_c']/10000, 2)))
        print ("5. F2, кгс (%s..%s)"%(round(val_list['min_F2']/10, 2), round(val_list['max_F2']/10, 2)))
        print ("0. Сбросить всё")
    else:
        print('Нет результатов для отображения')



#Уточняем парамеры пружины
def spring_find(res):
    res_2 = list(res)
    while True:
        p = input('Выберите параметр пружины для уточнения:')
    
        if p == '1':
            n_ = float(input('Количество рабочих витков: '))
            tmp = list(res_2)
            for i in range(0,100):
                for j in tmp:
                    if j.n != n_:
                        tmp.remove(j)
            if tmp:
                res_2 = tmp
                val_range(res_2)
            else:
                print('!!! Нет данных для отображения !!!')

        elif p == '2':
            d_ = float(input('d, мм: '))/1000
            tmp = list(res_2)
            for i in range(0,100):
                for j in tmp:
                    if d_!=j.d:
                        tmp.remove(j)
            if tmp:
                res_2 = tmp
                val_range(res_2)
            else:
                print('!!! Нет данных для отображения !!!')

        elif p == '3':
            l1_ = float(input('l1, мм: '))/1000
            tmp = list(res_2)
            for i in range(0,100):
                for j in tmp:
                    delta_l1 = abs(l1_-j.l1)
                    if delta_l1>j.l1*0.1:
                        tmp.remove(j)
            if tmp:
                res_2 = tmp
                val_range(res_2)
            else:
                print('!!! Нет данных для отображения !!!')

        elif p == '4':
            C_ = float(input('C, кгс/мм: '))*10000
            tmp = list(res_2)
            for i in range(0,100):
                for j in tmp:
                    delta_C = abs(C_-j.C)
                    if delta_C>j.C*0.2:
                        tmp.remove(j)
            if tmp:
                res_2 = tmp
                val_range(res_2)
            else:
                print('!!! Нет данных для отображения !!!')
       
        elif p == '5':
            F2_ = float(input('F2, кгс: '))*10
            tmp = list(res_2)
            tol_F2_ = F2_*0.01
            tol_F2 = input('Допуск на F2, кгс (%s): ' % tol_F2_)
            if tol_F2:
                tol_F2 = float(tol_F2)*10
            elif not tol_F2:
                tol_F2 = tol_F2_*10
            for i in range(0,100):
                for j in tmp:
                    delta_F2 = abs(F2_-j.F2)
                    if delta_F2 > tol_F2:
                        tmp.remove(j)
            if tmp:
                res_2 = tmp
                val_range(res_2)
            else:
                print('!!! Нет данных для отображения !!!')
    
        elif p == '0':
            res_2=list(res)
            val_range(res_2)
    
        else:
            break
    return res_2
    
    
    #Найдем для каждого диаметра проволоки значение l1
    
    
def print_result(masive_result):

    for g in masive_result:
        print (" ")
        print ("***************************************************")
        print ("F2: ", g.F2/10, "кгс")
        print ("d: ", g.d*1000, "мм")
        print ("n: ", g.n)
        print ("Dср: ", g.d_mid*1000, "мм")
        print ("Dвнутр: ", g.d_in*1000, "мм")
        print ("Dнар: ", g.d_out*1000, "мм")
        print ("n1: ", g.n1)
        print ("Tau: ", int(g.tau/10000000), "кгс/мм^2")
        print ("C: ", round(g.C/10000, 2), "кгс/мм")
        print ("I: ", round(g.c1,2))
        print ("l3: ", round(g.l3*1000, 2), "мм")
        print ("dh: ", round(g.dx*1000, 2), "мм")
        print ("l1: ", round(g.l1*1000, 2), "мм")
        print ("l0: ", round(g.l0*1000, 2), "мм")
        print ("F3: ", round(g.F3/10, 2), "кгс")
        print ("Устойчивость пружины: ", g.stable)

rep = "y"
if __name__ == '__main__':
    while True:
        if rep == "y":
            res = inp_data()
            val_range(res)
            res_ = spring_find(res)
            if res_:
                print_result(res_)
            else:
                val_range(res)
            print ("Повторить расчет?")
            rep = input("y/n (n)")
            if sys.platform == "win32":
                os.system('cls')
            else:
                os.system('clear')
        else:
            break
    
