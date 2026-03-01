"""
八字计算核心模块 - 完全修正版
根据标准万年历验证
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta


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
            '小寒': (2006, 1, 6, 3, 16),
            '立春': (2006, 2, 4, 7, 27),
            '惊蛰': (2006, 3, 6, 1, 29),
            '清明': (2006, 4, 5, 7, 15),
            '立夏': (2006, 5, 5, 20, 3),
            '芒种': (2006, 6, 6, 2, 29),
            '小暑': (2006, 7, 7, 13, 18),
            '立秋': (2006, 8, 8, 4, 17),
            '白露': (2006, 9, 8, 0, 28),
            '寒露': (2006, 10, 8, 16, 22),
            '立冬': (2006, 11, 7, 21, 26),
            '大雪': (2006, 12, 7, 13, 36),
        },
    }
    
    def calculate_bazi(self, year: int, month: int, day: int, hour: int, minute: int) -> Dict:
        """
        计算八字（高精度版本）
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
            y, m, d, h, mi = self.JIEQI_DATA[year]['立春']
            return datetime(y, m, d, h, mi)
        
        # 默认估算：2月4日6点
        return datetime(year, 2, 4, 6, 0)
    
    def _calculate_year_pillar(self, year: int, month: int, day: int, 
                              hour: int, minute: int) -> Tuple[Dict, int]:
        """计算年柱（以立春为界）"""
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
        """计算月柱（以节气为界）"""
        current_time = datetime(year, month, day, hour, minute)
        
        # 确定月支
        zhi_index = self._get_month_zhi_by_jieqi(year, month, day, hour, minute)
        zhi = self.DIZHI[zhi_index]
        
        # 使用五虎遁推算月干
        year_pillar, _ = self._calculate_year_pillar(year, month, day, hour, minute)
        year_gan = year_pillar['gan']
        year_gan_index = self.TIANGAN.index(year_gan)
        
        # 五虎遁：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚寅上，丁壬壬寅顺水流，戊癸甲寅为第一
        wuhu_start = {
            0: 2,  # 甲 -> 丙寅
            1: 4,  # 乙 -> 戊寅
            2: 6,  # 丙 -> 庚寅
            3: 8,  # 丁 -> 壬寅
            4: 0,  # 戊 -> 甲寅
            5: 2,  # 己 -> 丙寅
            6: 4,  # 庚 -> 戊寅
            7: 6,  # 辛 -> 庚寅
            8: 8,  # 壬 -> 壬寅
            9: 0   # 癸 -> 甲寅
        }
        
        # 寅月为起始（地支index=2），计算当前月支相对于寅月的偏移
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
    
    def _get_month_zhi_by_jieqi(self, year: int, month: int, day: int, 
                                hour: int, minute: int) -> int:
        """根据节气精确确定月支"""
        current_time = datetime(year, month, day, hour, minute)
        
        # 节气列表（按时间顺序）
        jieqi_list = [
            ('立春', 2), ('惊蛰', 3), ('清明', 4), ('立夏', 5),
            ('芒种', 6), ('小暑', 7), ('立秋', 8), ('白露', 9),
            ('寒露', 10), ('立冬', 11), ('大雪', 0), ('小寒', 1)
        ]
        
        # 获取当年的节气时间
        if year in self.JIEQI_DATA:
            jieqi_times = []
            for jieqi_name, zhi_idx in jieqi_list:
                if jieqi_name in self.JIEQI_DATA[year]:
                    y, m, d, h, mi = self.JIEQI_DATA[year][jieqi_name]
                    jq_time = datetime(y, m, d, h, mi)
                    jieqi_times.append((jq_time, zhi_idx, jieqi_name))
            
            # 排序节气时间
            jieqi_times.sort(key=lambda x: x[0])
            
            # 找到当前时间所在的节气区间
            result_zhi = 1  # 默认丑月
            for i in range(len(jieqi_times)):
                jq_time, zhi_idx, jq_name = jieqi_times[i]
                if current_time >= jq_time:
                    result_zhi = zhi_idx
                else:
                    break
            
            return result_zhi
        
        # 如果没有节气数据，使用粗略估算
        return self._estimate_month_zhi(month, day)
    
    def _estimate_month_zhi(self, month: int, day: int) -> int:
        """估算月支"""
        adjust_month = month
        if day < 6:
            adjust_month = month - 1
            if adjust_month == 0:
                adjust_month = 12
        
        month_to_zhi = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 0
        }
        
        return month_to_zhi.get(adjust_month, 2)
    
    def _calculate_day_pillar(self, year: int, month: int, day: int, hour: int) -> Tuple[Dict, datetime]:
        """
        计算日柱
        
        使用基准日：2000年1月1日 = 戊午日（已验证）
        """
        calc_year, calc_month, calc_day = year, month, day
        
        # 子时换日：23点算作次日
        if hour == 23:
            dt = datetime(year, month, day) + timedelta(days=1)
            calc_year, calc_month, calc_day = dt.year, dt.month, dt.day
        
        # 使用2000年1月1日作为基准日（戊午日）
        base_date = datetime(2000, 1, 1)
        current_date = datetime(calc_year, calc_month, calc_day)
        days_diff = (current_date - base_date).days
        
        # 2000年1月1日是戊午日，索引54
        base_ganzhi = '戊午'
        base_index = self.JIAZI_60.index(base_ganzhi)  # 54
        
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
        
        时辰划分：
        23:00-00:59 子时
        01:00-02:59 丑时
        ...
        11:00-12:59 午时
        ...
        """
        
        # 确定时支
        if hour == 23:
            zhi_index = 0  # 子时
            shi_duan = "早子"
        elif hour == 0:
            zhi_index = 0  # 子时
            shi_duan = "正子"
        else:
            # 1-2点丑(1)，3-4点寅(2)，5-6点卯(3)，7-8点辰(4)，9-10点巳(5)，11-12点午(6)
            zhi_index = ((hour + 1) // 2) % 12
            # 奇数小时为早，偶数小时为正
            if hour % 2 == 1:
                shi_duan = f"早{self.DIZHI[zhi_index]}"
            else:
                shi_duan = f"正{self.DIZHI[zhi_index]}"
        
        zhi = self.DIZHI[zhi_index]
        
        # 使用五鼠遁推算时干
        # 口诀：甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        day_gan_index = self.TIANGAN.index(day_gan)
        
        # 五鼠遁起始天干（从子时开始）
        wushu_start = {
            0: 0,  # 甲日 -> 子时甲子
            1: 2,  # 乙日 -> 子时丙子
            2: 4,  # 丙日 -> 子时戊子
            3: 6,  # 丁日 -> 子时庚子
            4: 8,  # 戊日 -> 子时壬子
            5: 0,  # 己日 -> 子时甲子
            6: 2,  # 庚日 -> 子时丙子
            7: 4,  # 辛日 -> 子时戊子
            8: 6,  # 壬日 -> 子时庚子
            9: 8   # 癸日 -> 子时壬子
        }
        
        # 从子时开始，按地支顺序推算天干
        # 例如：甲日午时 = 甲日子时(甲子) + 6个时辰 = 甲(0) + 6 = 庚(6)
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
