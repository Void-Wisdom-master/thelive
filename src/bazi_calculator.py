"""
八字计算核心模块 - 高精度版本
使用天文历法标准和真太阳时校正
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
import math


class BaziCalculator:
    """高精度八字计算器"""
    
    # 天干
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 60甲子表
    JIAZI_60 = []
    for i in range(60):
        gan = TIANGAN[i % 10]
        zhi = DIZHI[i % 12]
        JIAZI_60.append(f"{gan}{zhi}")
    
    # 天干五行
    TIANGAN_WUXING = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    
    # 地支五行
    DIZHI_WUXING = {
        '子': '水', '丑': '土', '寅': '木', '卯': '木',
        '辰': '土', '巳': '火', '午': '火', '未': '土',
        '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }
    
    # 天干阴阳
    TIANGAN_YINYANG = {
        '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
        '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
        '壬': '阳', '癸': '阴'
    }
    
    # 地支阴阳
    DIZHI_YINYANG = {
        '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
        '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
        '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
    }
    
    # 节气精确时间数据（2000-2030年）- 简化版，实际应用需完整数据
    # 格式：{年份: {节气名: (月, 日, 时, 分)}}
    JIEQI_DATA = {
        2006: {
            '立春': (2, 4, 7, 27),
            '惊蛰': (3, 6, 1, 29),
            '清明': (4, 5, 7, 15),
            '立夏': (5, 5, 20, 3),
            '芒种': (6, 6, 2, 29),
            '小暑': (7, 7, 13, 18),
            '立秋': (8, 8, 4, 17),
            '白露': (9, 8, 0, 28),
            '寒露': (10, 8, 16, 22),
            '立冬': (11, 7, 21, 26),
            '大雪': (12, 7, 13, 36),
            '小寒': (1, 6, 3, 16),
        },
        # 可以添加更多年份的数据
    }
    
    def calculate_bazi(self, year: int, month: int, day: int, hour: int, minute: int, 
                      longitude: float = 120.0) -> Dict:
        """
        计算八字（高精度版本）
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            hour: 小时（0-23）
            minute: 分钟
            longitude: 出生地经度（东经为正，默认120度北京时间）
            
        Returns:
            包含四柱信息的字典
        """
        # 1. 真太阳时校正
        solar_time = self._calculate_solar_time(year, month, day, hour, minute, longitude)
        
        # 2. 计算年柱（以立春为界）
        year_pillar, solar_year = self._calculate_year_pillar(year, month, day, hour, minute)
        
        # 3. 计算月柱（以节气为界）
        month_pillar, solar_month = self._calculate_month_pillar(solar_year, month, day, hour, minute)
        
        # 4. 计算日柱（使用儒略日高精度算法，考虑子时换日）
        day_pillar, actual_date = self._calculate_day_pillar(year, month, day, solar_time['hour'], solar_time['minute'])
        
        # 5. 计算时柱（使用真太阳时）
        hour_pillar = self._calculate_hour_pillar(
            day_pillar['gan'], 
            solar_time['hour'], 
            solar_time['minute']
        )
        
        return {
            'year_pillar': year_pillar,
            'month_pillar': month_pillar,
            'day_pillar': day_pillar,
            'hour_pillar': hour_pillar,
            'solar_time': solar_time,
            'solar_year': solar_year,
            'actual_date': actual_date
        }
    
    def _calculate_solar_time(self, year: int, month: int, day: int, 
                            hour: int, minute: int, longitude: float) -> Dict:
        """
        计算真太阳时
        
        东经120度为北京时间标准，每差1度相差4分钟
        东加西减：东经大于120度加时间，小于120度减时间
        """
        # 计算时差（分钟）
        time_diff = (longitude - 120.0) * 4
        
        # 转换为datetime进行计算
        dt = datetime(year, month, day, hour, minute)
        dt_solar = dt + timedelta(minutes=time_diff)
        
        return {
            'year': dt_solar.year,
            'month': dt_solar.month,
            'day': dt_solar.day,
            'hour': dt_solar.hour,
            'minute': dt_solar.minute,
            'longitude': longitude,
            'time_diff': time_diff
        }
    
    def _get_lichun_time(self, year: int) -> datetime:
        """
        获取立春时间（简化版）
        实际应用应使用天文算法或完整的节气表
        """
        # 立春一般在2月3-5日
        if year in self.JIEQI_DATA and '立春' in self.JIEQI_DATA[year]:
            m, d, h, mi = self.JIEQI_DATA[year]['立春']
            return datetime(year, m, d, h, mi)
        
        # 默认估算：2月4日6点
        return datetime(year, 2, 4, 6, 0)
    
    def _calculate_year_pillar(self, year: int, month: int, day: int, 
                              hour: int, minute: int) -> Tuple[Dict, int]:
        """
        计算年柱（以立春为界）
        
        Returns:
            (年柱字典, 实际年份)
        """
        current_time = datetime(year, month, day, hour, minute)
        lichun_time = self._get_lichun_time(year)
        
        # 判断是否已过立春
        if current_time < lichun_time:
            # 未过立春，使用上一年
            actual_year = year - 1
        else:
            actual_year = year
        
        # 计算干支（公元4年为甲子年）
        offset = actual_year - 4
        index = offset % 60
        
        ganzhi = self.JIAZI_60[index]
        gan = ganzhi[0]
        zhi = ganzhi[1]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi],
            'ganzhi': ganzhi
        }, actual_year
    
    def _get_jieqi_for_month(self, year: int, target_month: int) -> list:
        """
        获取某月的节气时间
        返回：[(节气名, datetime对象), ...]
        """
        jieqi_list = []
        
        if year not in self.JIEQI_DATA:
            # 使用估算值
            jieqi_months = {
                1: ('小寒', 6, 0), 2: ('立春', 4, 6), 3: ('惊蛰', 6, 0),
                4: ('清明', 5, 6), 5: ('立夏', 6, 0), 6: ('芒种', 6, 0),
                7: ('小暑', 7, 12), 8: ('立秋', 8, 0), 9: ('白露', 8, 0),
                10: ('寒露', 8, 12), 11: ('立冬', 7, 18), 12: ('大雪', 7, 12)
            }
            if target_month in jieqi_months:
                name, d, h = jieqi_months[target_month]
                jieqi_list.append((name, datetime(year, target_month, d, h, 0)))
        else:
            for name, (m, d, h, mi) in self.JIEQI_DATA[year].items():
                if m == target_month:
                    jieqi_list.append((name, datetime(year, m, d, h, mi)))
        
        return jieqi_list
    
    def _calculate_month_pillar(self, year: int, month: int, day: int, 
                               hour: int, minute: int) -> Tuple[Dict, int]:
        """
        计算月柱（以节气为界）
        
        月支固定对应：
        寅月（立春-惊蛰）、卯月（惊蛰-清明）、辰月（清明-立夏）
        巳月（立夏-芒种）、午月（芒种-小暑）、未月（小暑-立秋）
        申月（立秋-白露）、酉月（白露-寒露）、戌月（寒露-立冬）
        亥月（立冬-大雪）、子月（大雪-小寒）、丑月（小寒-立春）
        """
        current_time = datetime(year, month, day, hour, minute)
        
        # 节气到月支的映射
        jieqi_to_zhi = {
            '立春': 2, '惊蛰': 3, '清明': 4, '立夏': 5, '芒种': 6, '小暑': 7,
            '立秋': 8, '白露': 9, '寒露': 10, '立冬': 11, '大雪': 0, '小寒': 1
        }
        
        # 确定月支
        zhi_index = self._get_month_zhi_index(year, month, day, hour, minute)
        zhi = self.DIZHI[zhi_index]
        
        # 使用五虎遁推算月干
        year_pillar, _ = self._calculate_year_pillar(year, month, day, hour, minute)
        year_gan = year_pillar['gan']
        year_gan_index = self.TIANGAN.index(year_gan)
        
        # 五虎遁：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚寅上，丁壬壬寅顺水流，戊癸甲寅为第一
        wuhu_start = {
            0: 2, 1: 4, 2: 6, 3: 8, 4: 0,  # 甲-戊
            5: 2, 6: 4, 7: 6, 8: 8, 9: 0   # 己-癸
        }
        
        # 寅月为起始（地支index=2），当前月支相对于寅月的偏移
        offset = (zhi_index - 2) % 12
        gan_index = (wuhu_start[year_gan_index] + offset) % 10
        gan = self.TIANGAN[gan_index]
        
        ganzhi = gan + zhi
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi],
            'ganzhi': ganzhi
        }, zhi_index
    
    def _get_month_zhi_index(self, year: int, month: int, day: int, 
                            hour: int, minute: int) -> int:
        """根据节气确定月支索引"""
        current_time = datetime(year, month, day, hour, minute)
        
        # 节气顺序及对应月支
        jieqi_order = [
            ('小寒', 1), ('立春', 2), ('惊蛰', 3), ('清明', 4),
            ('立夏', 5), ('芒种', 6), ('小暑', 7), ('立秋', 8),
            ('白露', 9), ('寒露', 10), ('立冬', 11), ('大雪', 0)
        ]
        
        # 获取当年所有节气
        all_jieqi = []
        if year in self.JIEQI_DATA:
            for name, (m, d, h, mi) in self.JIEQI_DATA[year].items():
                dt = datetime(year, m, d, h, mi)
                for jq_name, zhi_idx in jieqi_order:
                    if jq_name == name:
                        all_jieqi.append((dt, zhi_idx))
                        break
        
        # 如果没有数据，使用估算
        if not all_jieqi:
            return self._estimate_month_zhi(month, day)
        
        # 排序
        all_jieqi.sort(key=lambda x: x[0])
        
        # 找到当前时间所在的节气区间
        for i in range(len(all_jieqi)):
            jq_time, zhi_idx = all_jieqi[i]
            if current_time >= jq_time:
                result_zhi = zhi_idx
            else:
                break
        
        return result_zhi if 'result_zhi' in locals() else self._estimate_month_zhi(month, day)
    
    def _estimate_month_zhi(self, month: int, day: int) -> int:
        """估算月支（当没有精确节气数据时）"""
        # 简化估算：每月6号左右换节气
        adjust = 0 if day >= 6 else -1
        actual_month = month + adjust
        
        if actual_month <= 0:
            actual_month += 12
        
        # 月份到月支的粗略对应
        month_to_zhi = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 0
        }
        
        return month_to_zhi.get(actual_month, 2)
    
    def _calculate_day_pillar(self, year: int, month: int, day: int, 
                             hour: int, minute: int) -> Tuple[Dict, datetime]:
        """
        计算日柱（高精度儒略日算法）
        子时换日：23:00-23:59归属次日
        """
        actual_year, actual_month, actual_day = year, month, day
        
        # 子时换日处理（23:00-23:59算作次日）
        if hour == 23:
            dt = datetime(year, month, day) + timedelta(days=1)
            actual_year, actual_month, actual_day = dt.year, dt.month, dt.day
        
        # 计算儒略日
        jd = self._calculate_julian_day(actual_year, actual_month, actual_day)
        
        # 儒略日转干支
        # 公元前4713年1月1日12时为儒略日0，该日为甲子日
        ganzhi_index = (int(jd + 49) % 60 + 60) % 60
        
        ganzhi = self.JIAZI_60[ganzhi_index]
        gan = ganzhi[0]
        zhi = ganzhi[1]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi],
            'ganzhi': ganzhi
        }, datetime(actual_year, actual_month, actual_day)
    
    def _calculate_julian_day(self, year: int, month: int, day: int) -> float:
        """计算儒略日（标准算法）"""
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + (a // 4)
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        
        return jd
    
    def _calculate_hour_pillar(self, day_gan: str, hour: int, minute: int) -> Dict:
        """
        计算时柱
        每个时辰分为两个时间段（早、正）
        """
        # 确定时支和时段
        # 23:00-23:59 -> 子时（早子时）
        # 00:00-00:59 -> 子时（正子时）
        # 01:00-02:59 -> 丑时
        # ...
        
        if hour == 23:
            zhi_index = 0  # 子时
            shi_duan = "早子时"
        elif hour == 0:
            zhi_index = 0  # 子时
            shi_duan = "正子时"
        else:
            # 其他时辰：1-2点丑时，3-4点寅时...
            zhi_index = ((hour + 1) // 2) % 12
            # 判断早时还是正时
            if hour % 2 == 1:
                shi_duan = f"早{self.DIZHI[zhi_index]}时"
            else:
                shi_duan = f"正{self.DIZHI[zhi_index]}时"
        
        zhi = self.DIZHI[zhi_index]
        
        # 使用五鼠遁推算时干
        day_gan_index = self.TIANGAN.index(day_gan)
        
        # 五鼠遁：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        wushu_start = {
            0: 0, 1: 2, 2: 4, 3: 6, 4: 8,  # 甲-戊
            5: 0, 6: 2, 7: 4, 8: 6, 9: 8   # 己-癸
        }
        
        gan_index = (wushu_start[day_gan_index] + zhi_index) % 10
        gan = self.TIANGAN[gan_index]
        
        ganzhi = gan + zhi
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi],
            'ganzhi': ganzhi,
            'shi_duan': shi_duan,
            'time_range': self._get_time_range(hour)
        }
    
    def _get_time_range(self, hour: int) -> str:
        """获取时辰时间范围"""
        time_ranges = {
            23: "23:00-23:59", 0: "00:00-00:59",
            1: "01:00-01:59", 2: "02:00-02:59",
            3: "03:00-03:59", 4: "04:00-04:59",
            5: "05:00-05:59", 6: "06:00-06:59",
            7: "07:00-07:59", 8: "08:00-08:59",
            9: "09:00-09:59", 10: "10:00-10:59",
            11: "11:00-11:59", 12: "12:00-12:59",
            13: "13:00-13:59", 14: "14:00-14:59",
            15: "15:00-15:59", 16: "16:00-16:59",
            17: "17:00-17:59", 18: "18:00-18:59",
            19: "19:00-19:59", 20: "20:00-20:59",
            21: "21:00-21:59", 22: "22:00-22:59"
        }
        return time_ranges.get(hour, "未知")
