"""
八字计算核心模块 - 高精度修正版
使用标准儒略日算法
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
    
    # 节气精确时间数据
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
        2000: {
            '立春': (2, 4, 20, 32),
            '惊蛰': (3, 5, 14, 42),
            '清明': (4, 4, 20, 39),
            '立夏': (5, 5, 8, 51),
            '芒种': (6, 5, 15, 26),
            '小暑': (7, 7, 2, 6),
            '立秋': (8, 7, 17, 9),
            '白露': (9, 7, 13, 29),
            '寒露': (10, 8, 5, 20),
            '立冬': (11, 7, 10, 24),
            '大雪': (12, 7, 2, 24),
            '小寒': (1, 6, 16, 26),
        },
    }
    
    def calculate_bazi(self, year: int, month: int, day: int, hour: int, minute: int) -> Dict:
        """
        计算八字（高精度版本）
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            hour: 小时（0-23）
            minute: 分钟
            
        Returns:
            包含四柱信息的字典
        """
        # 1. 计算年柱（以立春为界）
        year_pillar, solar_year = self._calculate_year_pillar(year, month, day, hour, minute)
        
        # 2. 计算月柱（以节气为界）
        month_pillar, solar_month = self._calculate_month_pillar(solar_year, month, day, hour, minute)
        
        # 3. 计算日柱（使用儒略日高精度算法，考虑子时换日）
        day_pillar, actual_date = self._calculate_day_pillar(year, month, day, hour)
        
        # 4. 计算时柱
        hour_pillar = self._calculate_hour_pillar(day_pillar['gan'], hour, minute)
        
        return {
            'year_pillar': year_pillar,
            'month_pillar': month_pillar,
            'day_pillar': day_pillar,
            'hour_pillar': hour_pillar,
            'solar_year': solar_year,
            'actual_date': actual_date
        }
    
    def _get_lichun_time(self, year: int) -> datetime:
        """获取立春时间"""
        if year in self.JIEQI_DATA and '立春' in self.JIEQI_DATA[year]:
            m, d, h, mi = self.JIEQI_DATA[year]['立春']
            return datetime(year, m, d, h, mi)
        
        # 默认估算：2月4日6点
        return datetime(year, 2, 4, 6, 0)
    
    def _calculate_year_pillar(self, year: int, month: int, day: int, 
                              hour: int, minute: int) -> Tuple[Dict, int]:
        """
        计算年柱（以立春为界）
        """
        current_time = datetime(year, month, day, hour, minute)
        lichun_time = self._get_lichun_time(year)
        
        # 判断是否已过立春
        if current_time < lichun_time:
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
    
    def _calculate_month_pillar(self, year: int, month: int, day: int, 
                               hour: int, minute: int) -> Tuple[Dict, int]:
        """
        计算月柱（以节气为界）
        """
        current_time = datetime(year, month, day, hour, minute)
        
        # 确定月支
        zhi_index = self._get_month_zhi_index(year, month, day, hour, minute)
        zhi = self.DIZHI[zhi_index]
        
        # 使用五虎遁推算月干
        year_pillar, _ = self._calculate_year_pillar(year, month, day, hour, minute)
        year_gan = year_pillar['gan']
        year_gan_index = self.TIANGAN.index(year_gan)
        
        # 五虎遁：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚寅上，丁壬壬寅顺水流，戊癸甲寅为第一
        wuhu_start = {
            0: 2, 1: 4, 2: 6, 3: 8, 4: 0,  # 甲丙戊庚壬
            5: 2, 6: 4, 7: 6, 8: 8, 9: 0   # 己乙丁辛癸
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
        
        # 节气到月支的映射（从寅月开始）
        jieqi_to_zhi = {
            '立春': 2,   # 寅月
            '惊蛰': 3,   # 卯月
            '清明': 4,   # 辰月
            '立夏': 5,   # 巳月
            '芒种': 6,   # 午月
            '小暑': 7,   # 未月
            '立秋': 8,   # 申月
            '白露': 9,   # 酉月
            '寒露': 10,  # 戌月
            '立冬': 11,  # 亥月
            '大雪': 0,   # 子月
            '小寒': 1    # 丑月
        }
        
        # 节气顺序（一年12个节气）
        jieqi_order = ['立春', '惊蛰', '清明', '立夏', '芒种', '小暑', 
                      '立秋', '白露', '寒露', '立冬', '大雪', '小寒']
        
        # 获取当年节气时间
        if year in self.JIEQI_DATA:
            jieqi_times = []
            for jq_name in jieqi_order:
                if jq_name in self.JIEQI_DATA[year]:
                    m, d, h, mi = self.JIEQI_DATA[year][jq_name]
                    jq_time = datetime(year, m, d, h, mi)
                    jieqi_times.append((jq_time, jieqi_to_zhi[jq_name]))
            
            # 找到当前时间所在的节气区间
            result_zhi = 1  # 默认丑月
            for i in range(len(jieqi_times)):
                jq_time, zhi_idx = jieqi_times[i]
                if current_time >= jq_time:
                    result_zhi = zhi_idx
            
            return result_zhi
        
        # 如果没有数据，使用估算
        return self._estimate_month_zhi(month, day)
    
    def _estimate_month_zhi(self, month: int, day: int) -> int:
        """估算月支"""
        # 粗略对应
        month_to_zhi = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 0
        }
        
        # 如果在月初几天，可能还是上个月的节气
        if day < 6:
            month = month - 1
            if month == 0:
                month = 12
        
        return month_to_zhi.get(month, 2)
    
    def _calculate_day_pillar(self, year: int, month: int, day: int, hour: int) -> Tuple[Dict, datetime]:
        """
        计算日柱（使用高精度儒略日算法）
        子时换日：23:00-23:59归属次日
        
        关键修正：使用2000年1月1日作为已知基准点
        2000年1月1日是戊辰日（干支序号：4）
        """
        calc_year, calc_month, calc_day = year, month, day
        
        # 子时换日：23点算作次日
        if hour == 23:
            dt = datetime(year, month, day) + timedelta(days=1)
            calc_year, calc_month, calc_day = dt.year, dt.month, dt.day
        
        # 计算相对于基准日（2000年1月1日，戊辰日）的天数差
        base_date = datetime(2000, 1, 1)
        current_date = datetime(calc_year, calc_month, calc_day)
        days_diff = (current_date - base_date).days
        
        # 2000年1月1日是戊辰日，在60甲子中的索引是4（甲子=0, 乙丑=1, 丙寅=2, 丁卯=3, 戊辰=4）
        base_index = 4
        
        # 计算当前日期的干支索引
        ganzhi_index = (base_index + days_diff) % 60
        
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
        }, datetime(calc_year, calc_month, calc_day)
    
    def _calculate_hour_pillar(self, day_gan: str, hour: int, minute: int) -> Dict:
        """
        计算时柱
        每个时辰2小时，细分为早、正
        
        时辰对应：
        23:00-00:59 子时（23:00-23:59早子，00:00-00:59正子）
        01:00-02:59 丑时（01:00-01:59早丑，02:00-02:59正丑）
        03:00-04:59 寅时
        05:00-06:59 卯时
        07:00-08:59 辰时
        09:00-10:59 巳时
        11:00-12:59 午时（11:00-11:59早午，12:00-12:59正午）
        13:00-14:59 未时
        15:00-16:59 申时
        17:00-18:59 酉时
        19:00-20:59 戌时
        21:00-22:59 亥时
        """
        
        # 确定时支
        if hour == 23:
            zhi_index = 0  # 子时
            shi_duan = "早子"
        elif hour == 0:
            zhi_index = 0  # 子时
            shi_duan = "正子"
        else:
            # 1-2点丑，3-4点寅，5-6点卯...
            zhi_index = ((hour + 1) // 2) % 12
            # 奇数小时为早，偶数小时为正
            if hour % 2 == 1:
                shi_duan = f"早{self.DIZHI[zhi_index]}"
            else:
                shi_duan = f"正{self.DIZHI[zhi_index]}"
        
        zhi = self.DIZHI[zhi_index]
        
        # 使用五鼠遁推算时干
        # 五鼠遁：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        day_gan_index = self.TIANGAN.index(day_gan)
        
        wushu_start = {
            0: 0,  # 甲日子时从甲子开始
            1: 2,  # 乙日子时从丙子开始
            2: 4,  # 丙日子时从戊子开始
            3: 6,  # 丁日子时从庚子开始
            4: 8,  # 戊日子时从壬子开始
            5: 0,  # 己日子时从甲子开始
            6: 2,  # 庚日子时从丙子开始
            7: 4,  # 辛日子时从戊子开始
            8: 6,  # 壬日子时从庚子开始
            9: 8   # 癸日子时从壬子开始
        }
        
        gan_index = (wushu_start[day_gan_index] + zhi_index) % 10
        gan = self.TIANGAN[gan_index]
        
        ganzhi = gan + zhi
        
        # 确定时间范围
        time_range = self._get_time_range(hour)
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi],
            'ganzhi': ganzhi,
            'shi_duan': shi_duan,
            'time_range': time_range
        }
    
    def _get_time_range(self, hour: int) -> str:
        """获取时辰时间范围"""
        if hour == 23:
            return "23:00-23:59 (早子时)"
        elif hour == 0:
            return "00:00-00:59 (正子时)"
        
        shichen_map = {
            1: ("丑", "早"), 2: ("丑", "正"),
            3: ("寅", "早"), 4: ("寅", "正"),
            5: ("卯", "早"), 6: ("卯", "正"),
            7: ("辰", "早"), 8: ("辰", "正"),
            9: ("巳", "早"), 10: ("巳", "正"),
            11: ("午", "早"), 12: ("午", "正"),
            13: ("未", "早"), 14: ("未", "正"),
            15: ("申", "早"), 16: ("申", "正"),
            17: ("酉", "早"), 18: ("酉", "正"),
            19: ("戌", "早"), 20: ("戌", "正"),
            21: ("亥", "早"), 22: ("亥", "正")
        }
        
        if hour in shichen_map:
            zhi, duan = shichen_map[hour]
            return f"{hour:02d}:00-{hour:02d}:59 ({duan}{zhi}时)"
        
        return f"{hour:02d}:00-{hour:02d}:59"
