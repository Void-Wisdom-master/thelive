"""
日历工具模块 - 处理公历与农历转换
"""
from lunarcalendar import Converter, Solar, Lunar
from datetime import datetime


class CalendarConverter:
    """日历转换器"""
    
    @staticmethod
    def solar_to_lunar(year: int, month: int, day: int) -> tuple:
        """
        公历转农历
        
        Args:
            year: 公历年
            month: 公历月
            day: 公历日
            
        Returns:
            (农历年, 农历月, 农历日, 是否闰月)
        """
        try:
            solar = Solar(year, month, day)
            lunar = Converter.Solar2Lunar(solar)
            return lunar.year, lunar.month, lunar.day, lunar.isleap
        except Exception as e:
            raise ValueError(f"日期转换失败: {str(e)}")
    
    @staticmethod
    def get_jieqi_info(year: int, month: int) -> dict:
        """
        获取节气信息（简化版本，实际应用中需要更精确的节气计算）
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            节气信息字典
        """
        # 这里使用简化的节气对应关系
        # 实际应用中应该使用精确的天文算法
        jieqi_map = {
            1: "小寒",
            2: "立春",
            3: "惊蛰",
            4: "清明",
            5: "立夏",
            6: "芒种",
            7: "小暑",
            8: "立秋",
            9: "白露",
            10: "寒露",
            11: "立冬",
            12: "大雪"
        }
        
        return {
            "jieqi": jieqi_map.get(month, "未知"),
            "month": month
        }