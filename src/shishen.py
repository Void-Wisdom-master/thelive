"""
十神分析模块（优化版）
"""
from typing import Dict


class ShishenAnalyzer:
    """十神分析器"""
    
    # 五行属性（从 BaziCalculator 同步）
    WUXING = {
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
    
    # 阴阳属性
    YINYANG = {
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
    
    # 地支藏干（本气）
    DIZHI_CANGAN = {
        '子': '癸', '丑': '己', '寅': '甲', '卯': '乙',
        '辰': '戊', '巳': '丙', '午': '丁', '未': '己',
        '申': '庚', '酉': '辛', '戌': '戊', '亥': '壬'
    }
    
    def analyze(self, bazi_result: Dict, gender: str) -> Dict:
        """
        分析八字十神
        
        Args:
            bazi_result: 八字计算结果
            gender: 性别
            
        Returns:
            十神分析结果
        """
        day_gan = bazi_result['day_pillar']['gan']
        
        return {
            'year': {
                'gan': self._get_shishen(day_gan, bazi_result['year_pillar']['gan']),
                'zhi': self._get_dizhi_shishen(day_gan, bazi_result['year_pillar']['zhi'])
            },
            'month': {
                'gan': self._get_shishen(day_gan, bazi_result['month_pillar']['gan']),
                'zhi': self._get_dizhi_shishen(day_gan, bazi_result['month_pillar']['zhi'])
            },
            'day': {
                'gan': '日主',
                'zhi': self._get_dizhi_shishen(day_gan, bazi_result['day_pillar']['zhi'])
            },
            'hour': {
                'gan': self._get_shishen(day_gan, bazi_result['hour_pillar']['gan']),
                'zhi': self._get_dizhi_shishen(day_gan, bazi_result['hour_pillar']['zhi'])
            }
        }
    
    def _get_shishen(self, day_gan: str, target_gan: str) -> str:
        """
        获取十神关系
        
        Args:
            day_gan: 日干（我）
            target_gan: 目标天干
            
        Returns:
            十神名称
        """
        if day_gan == target_gan:
            return '比肩'
        
        day_wuxing = self.WUXING[day_gan]
        target_wuxing = self.WUXING[target_gan]
        day_yinyang = self.YINYANG[day_gan]
        target_yinyang = self.YINYANG[target_gan]
        
        # 同阴阳还是异阴阳
        same_yinyang = (day_yinyang == target_yinyang)
        
        # 判断五行关系
        relation = self._get_wuxing_relation(day_wuxing, target_wuxing)
        
        # 根据关系和阴阳确定十神
        if relation == 'same':
            return '比肩' if same_yinyang else '劫财'
        elif relation == 'generate_me':  # 生我者为印
            return '正印' if not same_yinyang else '偏印'
        elif relation == 'i_generate':  # 我生者为食伤
            return '伤官' if not same_yinyang else '食神'
        elif relation == 'i_restrict':  # 我克者为财
            return '正财' if not same_yinyang else '偏财'
        elif relation == 'restrict_me':  # 克我者为官杀
            return '正官' if not same_yinyang else '七杀'
        
        return '未知'
    
    def _get_dizhi_shishen(self, day_gan: str, dizhi: str) -> str:
        """获取地支藏干的十神（取本气）"""
        cangan = self.DIZHI_CANGAN.get(dizhi, '甲')
        return self._get_shishen(day_gan, cangan)
    
    def _get_wuxing_relation(self, my_wuxing: str, target_wuxing: str) -> str:
        """
        获取五行关系
        
        Args:
            my_wuxing: 我的五行
            target_wuxing: 目标五行
            
        Returns:
            关系类型
        """
        if my_wuxing == target_wuxing:
            return 'same'
        
        # 五行相生关系：木生火，火生土，土生金，金生水，水生木
        sheng_relations = {
            '木': '火',
            '火': '土',
            '土': '金',
            '金': '水',
            '水': '木'
        }
        
        # 五行相克关系：木克土，土克水，水克火，火克金，金克木
        ke_relations = {
            '木': '土',
            '土': '水',
            '水': '火',
            '火': '金',
            '金': '木'
        }
        
        # 判断关系
        if sheng_relations.get(target_wuxing) == my_wuxing:
            return 'generate_me'  # 他生我
        elif sheng_relations.get(my_wuxing) == target_wuxing:
            return 'i_generate'  # 我生他
        elif ke_relations.get(my_wuxing) == target_wuxing:
            return 'i_restrict'  # 我克他
        elif ke_relations.get(target_wuxing) == my_wuxing:
            return 'restrict_me'  # 他克我
        
        return 'unknown'
