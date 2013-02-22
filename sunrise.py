# -*- coding: utf-8 -*-

from math import sin, cos, tan, asin, acos, atan
from math import radians, degrees
from math import floor, ceil

import datetime

def opt_degrees(d):
    deg = d
    while deg < 0 or deg > 360:
        if deg < 0: deg += 360
        elif deg > 360: deg -= 360
    return deg

def time_var(hour, minute, second):
    """ 時間の単位を[日]に変換する """
    return hour / 24.0 + minute / 1440.0 + second / 86400.0

def time_var_T(year, month, day, time_var):
    """ 時刻変数 T """
    y = year - 2000
    m = month
    d = day
    if m == 1 or m == 2:
        m += 12
        y -= 1
    k_p = 365 * y + 30 * m + d - 33.875 + floor(3 * (m + 1) / 5) + floor(y / 4)
    k = k_p + time_var + (65 + y) / 86400.0
    return k / 365.25

def oukei_taiyou(t):
    """ 太陽黄経 """
    l = 280.4603 + 360.00769 * t \
            + (1.9146 - 0.00005 * t) * sin(radians(357.538 + 359.991 * t)) \
            + 0.0200 * sin(radians(355.05 + 719.981 * t)) \
            + 0.0048 * sin(radians(234.95 +  19.341 * t)) \
            + 0.0020 * sin(radians(247.1  +  329.64 * t)) \
            + 0.0018 * sin(radians(297.8  + 4452.67 * t)) \
            + 0.0018 * sin(radians(251.3  +    0.20 * t)) \
            + 0.0015 * sin(radians(343.2  +  450.37 * t)) \
            + 0.0013 * sin(radians( 81.4  +  225.18 * t)) \
            + 0.0008 * sin(radians(132.5  +  659.29 * t)) \
            + 0.0007 * sin(radians(153.3  +   90.38 * t)) \
            + 0.0007 * sin(radians(206.8  +   30.35 * t)) \
            + 0.0006 * sin(radians( 29.8  +  337.18 * t)) \
            + 0.0005 * sin(radians(207.4  +    1.50 * t)) \
            + 0.0005 * sin(radians(291.2  +   22.81 * t)) \
            + 0.0004 * sin(radians(234.9  +  315.56 * t)) \
            + 0.0004 * sin(radians(157.3  +  299.30 * t)) \
            + 0.0004 * sin(radians( 21.1  +  720.02 * t)) \
            + 0.0003 * sin(radians(352.5  + 1079.97 * t)) \
            + 0.0003 * sin(radians(329.7  +   44.43 * t))
    return l

def oudou_keikaku(t):
    """ 黄経傾角 ε """
    return 23.439291 - 0.000130042 * t

def kyori_taiyou(t):
    """ 地心距離 """
    q = (0.007256 - 0.0000002 * t) * sin(radians(267.54 + 359.991 * t)) \
            + 0.000091 * sin(radians(265.1 + 719.98 * t)) \
            + 0.000030 * sin(radians(90.0)) \
            + 0.000013 * sin(radians( 27.8 + 4452.67 * t)) \
            + 0.000007 * sin(radians(254.0 + 450.4 * t)) \
            + 0.000007 * sin(radians(156.0 + 329.5 * t))
    r = 10 ** q
    return r

def sekikei_taiyou(t):
    """ 太陽の赤経 """
    #return 0.0017 * d * d + 1.020425 * d + 228.3475016
    oukei = oukei_taiyou(t)
    oukei = opt_degrees(oukei)
    keikaku = oudou_keikaku(t)
    sekikei = degrees(atan(tan(radians(oukei)) * cos(radians(keikaku))))
    sekikei = opt_degrees(sekikei)
    # 象限を補正
    # 黄経λ, 赤経α
    # 0 <= λ < 180 ならば 0 <= α < 180
    # 180 <= λ < 360 ならば 180 <= α < 360
    if (oukei >=0 and oukei < 180):
       if sekikei >= 180: sekikei -= 180
       if sekikei < 0: sekikei += 180
    if (oukei >= 180 and oukei < 360):
        if sekikei <= 180: sekikei += 180
        if sekikei > 360: sekikei -= 180
    return sekikei

def sekii_taiyou(t):
    """ 太陽の赤緯 """
    #return 0.00265 * d * d - 0.266037 * d - 17.94810859
    oukei = oukei_taiyou(t)
    keikaku = oudou_keikaku(t)
    return degrees(asin(sin(radians(oukei)) * sin(radians(keikaku))))

def get_kouseiji(t, d, keido):
    """ 恒星時 """
    #return 57.027999 + 360.9856474 * d
    kj = 325.4606 + 360.007700536 * t + 0.00000003879 * t * t + 360.0 * d + keido
    return opt_degrees(kj)

def shutubotu_koudo(kyori):
    """ 出没高度 """
    s = 0.266994 / kyori
    e = 0
    r = 0.585556
    pi = 0.0024428 / kyori
    k = - s - e - r + pi
    return k

def _koudo_jikaku(koudo, sekii, ido):
    """ 出没高度 -> 時角 """
    t_k_p = (sin(radians(koudo)) - sin(radians(sekii)) * sin(radians(ido))) \
            / (cos(radians(sekii)) * cos(radians(ido)))
    t_k = degrees(acos(t_k_p))
    return t_k

def hinode_jikaku(koudo, sekii, ido):
    return - (_koudo_jikaku(koudo, sekii, ido))

def hinoiri_jikaku(koudo, sekii, ido):
    return _koudo_jikaku(koudo, sekii, ido)

def taiyou_jikaku(kouseiji, sekikei):
    t = kouseiji - sekikei
    return t

def hosei(jikaku_k, jikaku_t):
    dd = (jikaku_k - jikaku_t) / 360
    # 整数部を削除
    if dd >= 1: dd -= floor(dd)
    if dd <= -1: dd -= ceil(dd)
    # 絶対値が小さくなる方の補正値を選ぶ
    dd_p = 0
    if dd > 0: dd_p = - (1.0 - dd)
    else: dd_p = 1.0 + dd

    if abs(dd) < abs(dd_p):
        return dd
    else:
        return dd_p

def jikan(d):
    """ 時刻変数 -> 通常の時間 """
    h = d * 24
    hour = floor(h)
    m = h - floor(h)
    minute = m * 60
    minute = round(minute)
    # 丸めた結果60分になったら時間に換算する
    if minute >= 60:
        hour += 1
        minute = 0
    return hour, minute

def _hinode_hinoiri(keido, ido, year, month, day, is_hinode):
    if is_hinode: h = 6
    else: h = 18
    d = time_var(h, 0, 0)
    dd = 1.0
    while abs(dd) > 0.00005:
        t = time_var_T(year, month, day, d)
        sekikei = sekikei_taiyou(t)
        sekii = sekii_taiyou(t)
        kyori = kyori_taiyou(t)
        kouseiji = get_kouseiji(t, d, keido)
        k = shutubotu_koudo(kyori)
        if is_hinode:
            jikaku_k = hinode_jikaku(k, sekii, ido)
        else:
            jikaku_k = hinoiri_jikaku(k, sekii, ido)
        jikaku_t = taiyou_jikaku(kouseiji, sekikei)
        dd = hosei(jikaku_k, jikaku_t)
        #print "赤経", sekikei
        #print "赤緯", sekii
        #print "距離", kyori
        #print "恒星時", kouseiji
        #print "出没高度", k
        #print "時角", jikaku_k
        #print "太陽時角", jikaku_t
        #print "Δd", dd
        #print
        d += dd
    return d

def  hinode(keido, ido, year, month, day):
    return _hinode_hinoiri(keido, ido, year, month, day, True)

def hinoiri(keido, ido, year, month, day):
    return _hinode_hinoiri(keido, ido, year, month, day, False)


def main():
    keido = 139.7447
    ido = 35.6544
    
    #d = hinode(keido, ido, 2012, 9, 12)
    #hour, minute = jikan(d)
    #print "%d:%d" % (hour, minute)
    #print
    #d = hinoiri(keido, ido, 2012, 9, 12)
    #hour, minute = jikan(d)
    #print "%d:%d" % (hour, minute)
    #print
    
    date = datetime.date(2013, 1, 1)
    for i in range(366):
        year = int(date.year)
        month = int(date.month)
        day = int(date.day)
        dr = hinode(keido, ido, year, month, day)
        ds = hinoiri(keido, ido, year, month, day)
        hr, mr = jikan(dr)
        hs, ms = jikan(ds)
        print date, "%02d:%02d" % (hr, mr), "%02d:%02d" % (hs, ms)
        date += datetime.timedelta(days = 1)

if __name__ == "__main__":
    main()

