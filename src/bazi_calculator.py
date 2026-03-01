"""
八字计算核心模块 - 完全修正版
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
    
    # 节气精确时间数据（需要扩展更多年份）
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
        2007: {
            '小寒': (2007, 1, 6, 8, 57),
            '立春': (2007, 2, 4, 13, 18),
            '惊蛰': (2007, 3, 6, 7, 18),
            '清明': (2007, 4, 5, 13, 4),
            '立夏': (2007, 5, 6, 1, 51),
            '芒种': (2007, 6, 6, 8, 18),
            '小暑': (2007, 7, 7, 19, 7),
            '立秋': (2007, 8, 8, 10, 6),
            '白露': (2007, 9, 8, 6, 18),
            '寒露': (2007, 10, 8, 22, 13),
            '立冬': (2007, 11, 8, 3, 17),
            '大雪': (2007, 12, 7, 19, 28),
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
        """
        计算月柱（以节气为界）
        月支由节气确定，月干由年干推算（五虎遁）
        """
        current_time = datetime(year, month, day, hour, minute)
        
        # 确定月支（根据节气）
        zhi_index = self._get_month_zhi_by_jieqi(year, month, day, hour, minute)
        zhi = self.DIZHI[zhi_index]
        
        # 使用五虎遁推算月干
        year_pillar, _ = self._calculate_year_pillar(year, month, day, hour, minute)
        year_gan = year_pillar['gan']
        year_gan_index = self.TIANGAN.index(year_gan)
        
        # 五虎遁：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚寅上，丁壬壬寅顺水流，戊癸甲寅为第一
        # 意思是：甲年和己年，寅月从丙寅开始；乙年和庚年，寅月从戊寅开始...
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
        """
        根据节气精确确定月支
        
        节气与月支对应关系：
        立春-惊蛰：寅月(2)
        惊蛰-清明：卯月(3)
        清明-立夏：辰月(4)
        立夏-芒种：巳月(5)
        芒种-小暑：午月(6)
        小暑-立秋：未月(7)
        立秋-白露：申月(8)
        白露-寒露：酉月(9)
        寒露-立冬：戌月(10)
        立冬-大雪：亥月(11)
        大雪-小寒：子月(0)
        小寒-立春：丑月(1)
        """
        current_time = datetime(year, month, day, hour, minute)
        
        # 节气列表（按时间顺序）
        jieqi_list = [
            ('立春', 2), ('惊蛰', 3), ('清明', 4), ('立夏', 5),
            ('芒种', 6), ('小暑', 7), ('立秋', 8), ('白露', 9),
            ('寒露', 10), ('立冬', 11), ('大雪', 0), ('小寒', 1)
        ]
        
        # 获取当年的节气时间
        if year in self.JIEQI_DATA:
            # 从当年节气中找到当前时间所在的月份
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
        """估算月支（当没有精确节气数据时）"""
        # 粗略对应（节气一般在每月4-8日）
        adjust_month = month
        if day < 6:  # 节气前，算上个月
            adjust_month = month - 1
            if adjust_month == 0:
                adjust_month = 12
        
        month_to_zhi = {
            1: 1,   # 丑月（小寒-立春）
            2: 2,   # 寅月（立春-惊蛰）
            3: 3,   # 卯月（惊蛰-清明）
            4: 4,   # 辰月（清明-立夏）
            5: 5,   # 巳月（立夏-芒种）
            6: 6,   # 午月（芒种-小暑）
            7: 7,   # 未月（小暑-立秋）
            8: 8,   # 申月（立秋-白露）
            9: 9,   # 酉月（白露-寒露）
            10: 10, # 戌月（寒露-立冬）
            11: 11, # 亥月（立冬-大雪）
            12: 0   # 子月（大雪-小寒）
        }
        
        return month_to_zhi.get(adjust_month, 2)
    
    def _calculate_day_pillar(self, year: int, month: int, day: int, hour: int) -> Tuple[Dict, datetime]:
        """
        计算日柱（使用高精度基准日算法）
        
        关键：使用已知准确的基准日
        2000年1月1日 = 庚辰日（干支序号：16）
        
        验证：
        - 甲子 = 0, 乙丑 = 1, ..., 庚辰 = 16
        """
        calc_year, calc_month, calc_day = year, month, day
        
        # 子时换日：23点算作次日
        if hour == 23:
            dt = datetime(year, month, day) + timedelta(days=1)
            calc_year, calc_month, calc_day = dt.year, dt.month, dt.day
        
        # 计算相对于基准日的天数差
        # 基准日：2000年1月1日为庚辰日
        base_date = datetime(2000, 1, 1)
        current_date = datetime(calc_year, calc_month, calc_day)
        days_diff = (current_date - base_date).days
        
        # 2000年1月1日是庚辰日
        # 在60甲子中：甲子=0, 乙丑=1, 丙寅=2, ..., 庚辰=16
        # 庚是第7个天干(index=6)，辰是第5个地支(index=4)
        # 60甲子索引 = 天干index*6 + 地支调整
        # 更直接：查表得知庚辰在60甲子中的序号
        base_ganzhi = '庚辰'
        base_index = self.JIAZI_60.index(base_ganzhi)  # = 16
        
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
