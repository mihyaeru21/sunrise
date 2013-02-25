# -*- coding: utf-8 -*-

import math
from math import floor, ceil
import datetime

# 外部から利用する関数
def sunrise(lon, lat, date):
    """日の出時刻"""
    return _sunriseset(lon, lat, date, -1)

def sunset(lon, lat, date):
    """日の入り時刻"""
    return _sunriseset(lon, lat, date, 1)


# 度を使った三角関数
def _sind(deg):
    return math.sin(math.radians(deg))
def _cosd(deg):
    return math.cos(math.radians(deg))
def _tand(deg):
    return math.tan(math.radians(deg))
def _asind(value):
    return math.degrees(math.asin(value))
def _acosd(value):
    return math.degrees(math.acos(value))
def _atand(value):
    return math.degrees(math.atan(value))

def _optimize_degrees(deg):
    """ 角度を0-360にする """
    deg = deg % 360
    if deg < 0:
        deg += 360
    return deg

def _timevar_T(date, timevar):
    """ 時刻変数 T """
    y = int(date.year) - 2000
    m = int(date.month)
    d = int(date.day)
    if m == 1 or m == 2:
        m += 12
        y -= 1
    k_p = 365 * y + 30 * m + d - 33.875 + floor(3 * (m + 1) / 5) + floor(y / 4)
    k = k_p + timevar + (65 + y) / 86400.0
    return k / 365.25

def _sun_ecliptic_longitude(t):
    """ 太陽黄経 """
    l = 280.4603 + 360.00769 * t \
            + (1.9146 - 0.00005 * t) * _sind(357.538 + 359.991 * t) \
            + 0.0200 * _sind(355.05 + 719.981 * t) \
            + 0.0048 * _sind(234.95 +  19.341 * t) \
            + 0.0020 * _sind(247.1  +  329.64 * t) \
            + 0.0018 * _sind(297.8  + 4452.67 * t) \
            + 0.0018 * _sind(251.3  +    0.20 * t) \
            + 0.0015 * _sind(343.2  +  450.37 * t) \
            + 0.0013 * _sind( 81.4  +  225.18 * t) \
            + 0.0008 * _sind(132.5  +  659.29 * t) \
            + 0.0007 * _sind(153.3  +   90.38 * t) \
            + 0.0007 * _sind(206.8  +   30.35 * t) \
            + 0.0006 * _sind( 29.8  +  337.18 * t) \
            + 0.0005 * _sind(207.4  +    1.50 * t) \
            + 0.0005 * _sind(291.2  +   22.81 * t) \
            + 0.0004 * _sind(234.9  +  315.56 * t) \
            + 0.0004 * _sind(157.3  +  299.30 * t) \
            + 0.0004 * _sind( 21.1  +  720.02 * t) \
            + 0.0003 * _sind(352.5  + 1079.97 * t) \
            + 0.0003 * _sind(329.7  +   44.43 * t)
    return _optimize_degrees(l)

def _ecliptic_longitude_inclination(t):
    """ 黄経傾角 ε """
    return 23.439291 - 0.000130042 * t

def _geocentric_distance(t):
    """ 地心距離 """
    q = (0.007256 - 0.0000002 * t) * _sind(267.54 + 359.991 * t) \
        + 0.000091 * _sind(265.1 + 719.98 * t) \
        + 0.000030 * _sind(90.0) \
        + 0.000013 * _sind( 27.8 + 4452.67 * t) \
        + 0.000007 * _sind(254.0 + 450.4 * t) \
        + 0.000007 * _sind(156.0 + 329.5 * t)
    r = 10 ** q
    return r

def _sun_right_ascension(t):
    """ 太陽の赤経 """
    sun_el = _sun_ecliptic_longitude(t)
    inclination = _ecliptic_longitude_inclination(t)
    ascension = _optimize_degrees(_atand(_tand(sun_el) * _cosd(inclination)))
    # 象限を補正 黄経λ, 赤経α
    # 0 <= λ < 180 ならば 0 <= α < 180
    # 180 <= λ < 360 ならば 180 <= α < 360
    if (sun_el >=0 and sun_el < 180):
       if ascension >= 180: ascension -= 180
       if ascension < 0: ascension += 180
    if (sun_el >= 180 and sun_el < 360):
        if ascension <= 180: ascension += 180
        if ascension > 360: ascension -= 180
    return ascension

def _sun_declination(t):
    """ 太陽の赤緯 """
    sun_el = _sun_ecliptic_longitude(t)
    inclination = _ecliptic_longitude_inclination(t)
    return _asind(_sind(sun_el) * _sind(inclination))

def _sidereal_time(t, d, lon):
    """ 恒星時 """
    kj = 325.4606 + 360.007700536 * t + 0.00000003879 * t * t + 360.0 * d + lon
    return _optimize_degrees(kj)

def _appearheight(distance):
    """ 出没高度 """
    s = 0.266994 / distance
    e = 0
    r = 0.585556
    pi = 0.0024428 / distance
    k = - s - e - r + pi
    return k

def _appearheight_to_hourangle(height, declination, lat):
    """ 出没高度 -> 時角 """
    t_k_p = (_sind(height) - _sind(declination) * _sind(lat)) / (_cosd(declination) * _cosd(lat))
    t_k = _acosd(t_k_p)
    return t_k

def _sun_hourangle(sidereal_time, ascension):
    """太陽時角"""
    return sidereal_time - ascension

def _revise(ha_k, ha_t):
    """ 補正値の算出 """
    dd = (ha_k - ha_t) / 360
    # 整数部を削除
    if dd >= 1:
        dd -= floor(dd)
    if dd <= -1:
        dd -= ceil(dd)
    # 絶対値が小さくなる方の補正値を選ぶ
    dd_p = 0
    if dd > 0:
        dd_p = - (1.0 - dd)
    else:
        dd_p = 1.0 + dd

    if abs(dd) < abs(dd_p):
        return dd
    else:
        return dd_p

def _timevar_to_time(d):
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
    return datetime.time(hour=int(hour), minute=int(minute))

def _sunriseset(lon, lat, date, ha_revise):
    h = 12        # 探索の初期値
    d = h / 24.0  # 時間の単位を[日]にする
    dd = 1.0
    while abs(dd) > 0.00005:
        t = _timevar_T(date, d)
        sekikei = _sun_right_ascension(t)
        sekii = _sun_declination(t)
        distance = _geocentric_distance(t)
        kouseiji = _sidereal_time(t, d, lon)
        k = _appearheight(distance)
        ha_k = _appearheight_to_hourangle(k, sekii, lat) * ha_revise
        ha_t = _sun_hourangle(kouseiji, sekikei)
        dd = _revise(ha_k, ha_t)
        d += dd
    return d

if __name__ == "__main__":
    """テスト"""
    # 東京
    lon = 139.7447
    lat = 35.6544
    date = datetime.datetime.now()
    for i in range(366):
        dr = sunrise(lon, lat, date)
        ds = sunset(lon, lat, date)
        sunrise_time = _timevar_to_time(dr)
        sunset_time = _timevar_to_time(ds)
        print date, "%02d:%02d" % (sunrise_time.hour, sunrise_time.minute), "%02d:%02d" % (sunset_time.hour, sunset_time.minute)
        date += datetime.timedelta(days = 1)

