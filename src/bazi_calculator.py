"""
八字计算核心模块 - 修复版
"""
from typing import Dict, Tuple
from datetime import datetime


class BaziCalculator:
    """八字计算器"""
    
    # 天干
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
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
        '甲': '阳', '乙': '阴',
        '丙': '阳', '丁': '阴',
        '戊': '阳', '己': '阴',
        '庚': '阳', '辛': '阴',
        '壬': '阳', '癸': '阴'
    }
    
    # 地支阴阳
    DIZHI_YINYANG = {
        '子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
        '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
        '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'
    }
    
    def calculate_bazi(self, year: int, month: int, day: int, hour_index: int) -> Dict:
        """
        计算八字
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            hour_index: 时辰索引 (0-11, 对应子时到亥时)
            
        Returns:
            包含四柱信息的字典
        """
        # 计算年柱
        year_pillar = self._calculate_year_pillar(year, month, day)
        
        # 计算月柱
        month_pillar = self._calculate_month_pillar(year, month, day)
        
        # 计算日柱
        day_pillar = self._calculate_day_pillar(year, month, day)
        
        # 计算时柱
        hour_pillar = self._calculate_hour_pillar(day_pillar['gan'], hour_index)
        
        return {
            'year_pillar': year_pillar,
            'month_pillar': month_pillar,
            'day_pillar': day_pillar,
            'hour_pillar': hour_pillar
        }
    
    def _calculate_year_pillar(self, year: int, month: int, day: int) -> Dict[str, str]:
        """
        计算年柱
        注意：立春前算上一年
        """
        # 简化处理：2月4日前算上一年
        actual_year = year
        if month < 2 or (month == 2 and day < 4):
            actual_year = year - 1
        
        # 计算干支（公元4年是甲子年）
        offset = actual_year - 4
        
        gan_index = offset % 10
        zhi_index = offset % 12
        
        gan = self.TIANGAN[gan_index]
        zhi = self.DIZHI[zhi_index]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi]
        }
    
    def _calculate_month_pillar(self, year: int, month: int, day: int) -> Dict[str, str]:
        """
        计算月柱
        使用节气月份
        """
        # 简化的节气月份对照（实际应该精确计算节气时间）
        # 这里假设每月的节气在固定日期附近
        jieqi_days = [6, 4, 6, 5, 6, 6, 7, 8, 8, 8, 7, 7]  # 各月节气大概日期
        
        actual_month = month
        actual_year = year
        
        # 如果在节气前，算上个月
        if day < jieqi_days[month - 1]:
            actual_month -= 1
            if actual_month == 0:
                actual_month = 12
                actual_year -= 1
        
        # 月支（从寅月开始，对应农历正月）
        # 正月寅，二月卯，三月辰...
        month_zhi_map = {
            1: 2,   # 正月寅
            2: 3,   # 二月卯
            3: 4,   # 三月辰
            4: 5,   # 四月巳
            5: 6,   # 五月午
            6: 7,   # 六月未
            7: 8,   # 七月申
            8: 9,   # 八月酉
            9: 10,  # 九月戌
            10: 11, # 十月亥
            11: 0,  # 十一月子
            12: 1   # 十二月丑
        }
        
        zhi_index = month_zhi_map[actual_month]
        zhi = self.DIZHI[zhi_index]
        
        # 月干推算（五虎遁）
        # 年干推月干：甲己之年丙作首，乙庚之年戊为头，丙辛之年庚寅上，丁壬壬寅顺水流，戊癸甲寅为第一
        year_pillar = self._calculate_year_pillar(actual_year, month, day)
        year_gan_index = self.TIANGAN.index(year_pillar['gan'])
        
        # 五虎遁口诀对应的起始天干
        month_gan_start = {
            0: 2,  # 甲年从丙开始（丙寅）
            1: 4,  # 乙年从戊开始（戊寅）
            2: 6,  # 丙年从庚开始（庚寅）
            3: 8,  # 丁年从壬开始（壬寅）
            4: 0,  # 戊年从甲开始（甲寅）
            5: 2,  # 己年从丙开始（丙寅）
            6: 4,  # 庚年从戊开始（戊寅）
            7: 6,  # 辛年从庚开始（庚寅）
            8: 8,  # 壬年从壬开始（壬寅）
            9: 0   # 癸年从甲开始（甲寅）
        }
        
        start_gan = month_gan_start[year_gan_index]
        # 从寅月（index=2）开始算起
        gan_index = (start_gan + (zhi_index - 2)) % 10
        gan = self.TIANGAN[gan_index]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi]
        }
    
    def _calculate_day_pillar(self, year: int, month: int, day: int) -> Dict[str, str]:
        """
        计算日柱
        使用改进的公元纪年日干支计算公式
        """
        # 计算距离基准日的天数
        # 使用公元元年1月1日为基准（该日为癸酉日，干支序号为 9, 9）
        
        # 计算儒略日数
        if month <= 2:
            month += 12
            year -= 1
        
        # 计算公式
        a = year // 100
        b = a // 4
        c = 2 - a + b
        e = int(365.25 * (year + 4716))
        f = int(30.6001 * (month + 1))
        jd = c + day + e + f - 1524.5
        
        # 转换为干支
        # 公元前4713年1月1日12时为儒略日0，是甲子日
        gan_index = int((jd + 49) % 10)
        zhi_index = int((jd + 1) % 12)
        
        gan = self.TIANGAN[gan_index]
        zhi = self.DIZHI[zhi_index]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi]
        }
    
    def _calculate_hour_pillar(self, day_gan: str, hour_index: int) -> Dict[str, str]:
        """
        计算时柱
        使用五鼠遁时法
        """
        zhi = self.DIZHI[hour_index]
        
        # 五鼠遁时：日干求时干
        # 甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
        day_gan_index = self.TIANGAN.index(day_gan)
        
        hour_gan_start = {
            0: 0,  # 甲日从甲开始（甲子）
            1: 2,  # 乙日从丙开始（丙子）
            2: 4,  # 丙日从戊开始（戊子）
            3: 6,  # 丁日从庚开始（庚子）
            4: 8,  # 戊日从壬开始（壬子）
            5: 0,  # 己日从甲开始（甲子）
            6: 2,  # 庚日从丙开始（丙子）
            7: 4,  # 辛日从戊开始（戊子）
            8: 6,  # 壬日从庚开始（庚子）
            9: 8   # 癸日从壬开始（壬子）
        }
        
        start_gan = hour_gan_start[day_gan_index]
        gan_index = (start_gan + hour_index) % 10
        gan = self.TIANGAN[gan_index]
        
        return {
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': self.TIANGAN_WUXING[gan],
            'zhi_wuxing': self.DIZHI_WUXING[zhi],
            'gan_yinyang': self.TIANGAN_YINYANG[gan],
            'zhi_yinyang': self.DIZHI_YINYANG[zhi]
        }
