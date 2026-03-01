"""
八字计算核心模块
"""
from typing import Dict, Tuple


class BaziCalculator:
    """八字计算器"""
    
    # 天干
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 月份地支对照（从立春开始算起）
    MONTH_DIZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    
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
        year_pillar = self._calculate_year_pillar(year)
        
        # 计算月柱
        month_pillar = self._calculate_month_pillar(year, month)
        
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
    
    def _calculate_year_pillar(self, year: int) -> Dict[str, str]:
        """计算年柱"""
        # 1984年是甲子年，以此为基准
        base_year = 1984
        offset = (year - base_year) % 60
        
        gan_index = offset % 10
        zhi_index = offset % 12
        
        return {
            'gan': self.TIANGAN[gan_index],
            'zhi': self.DIZHI[zhi_index]
        }
    
    def _calculate_month_pillar(self, year: int, month: int) -> Dict[str, str]:
        """计算月柱"""
        # 简化处理：直接用公历月份对应，实际应考虑节气
        # 调整月份索引（立春为正月寅月）
        if month < 2:
            month_index = month + 10  # 11月子、12月丑
        else:
            month_index = month - 2
        
        zhi = self.MONTH_DIZHI[month_index]
        
        # 年干求月干（五虎遁月）
        year_pillar = self._calculate_year_pillar(year)
        year_gan_index = self.TIANGAN.index(year_pillar['gan'])
        
        # 五虎遁口诀：甲己之年丙作首
        month_gan_bases = [2, 4, 6, 8, 0]  # 甲己年从丙开始，乙庚年从戊开始...
        base = month_gan_bases[year_gan_index % 5]
        gan_index = (base + month_index) % 10
        
        return {
            'gan': self.TIANGAN[gan_index],
            'zhi': zhi
        }
    
    def _calculate_day_pillar(self, year: int, month: int, day: int) -> Dict[str, str]:
        """计算日柱（使用基姆拉尔森公式）"""
        # 简化的日柱计算
        if month < 3:
            month += 12
            year -= 1
        
        # 计算距离基准日的天数
        c = year // 100
        y = year % 100
        m = month
        d = day
        
        # 基姆拉尔森公式
        w = (c // 4 - 2 * c + y + y // 4 + 13 * (m + 1) // 5 + d - 1) % 60
        
        if w < 0:
            w += 60
        
        gan_index = w % 10
        zhi_index = w % 12
        
        return {
            'gan': self.TIANGAN[gan_index],
            'zhi': self.DIZHI[zhi_index]
        }
    
    def _calculate_hour_pillar(self, day_gan: str, hour_index: int) -> Dict[str, str]:
        """计算时柱（五鼠遁时）"""
        zhi = self.DIZHI[hour_index]
        
        # 五鼠遁时：日干求时干
        day_gan_index = self.TIANGAN.index(day_gan)
        
        # 甲己日从甲子开始，乙庚日从丙子开始...
        hour_gan_bases = [0, 2, 4, 6, 8]
        base = hour_gan_bases[day_gan_index % 5]
        gan_index = (base + hour_index) % 10
        
        return {
            'gan': self.TIANGAN[gan_index],
            'zhi': zhi
        }