"""
八字排盘系统 - Streamlit 主应用
"""
import streamlit as st
from datetime import datetime, time
from src.bazi_calculator import BaziCalculator
from src.shishen import ShishenAnalyzer

# 页面配置
st.set_page_config(
    page_title="八字排盘系统",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义样式
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1em;
        margin-bottom: 2em;
    }
    .pillar-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2em;
        border-radius: 15px;
        margin: 1em 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .pillar-title {
        color: white;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
    }
    .pillar-item {
        background: white;
        padding: 1em;
        border-radius: 10px;
        text-align: center;
        margin: 0.5em;
    }
    .pillar-label {
        color: #7f8c8d;
        font-size: 0.9em;
    }
    .pillar-value {
        color: #2c3e50;
        font-size: 1.8em;
        font-weight: bold;
    }
    .shishen-tag {
        background: #ecf0f1;
        color: #e74c3c;
        padding: 0.3em 0.8em;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin-top: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-title">🔮 八字排盘系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">输入出生信息，获取您的八字命盘</div>', unsafe_allow_html=True)
    
    # 创建表单
    with st.form("bazi_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input(
                "📅 出生日期（公历）",
                value=datetime(2000, 1, 1),
                min_value=datetime(1900, 1, 1),
                max_value=datetime(2100, 12, 31)
            )
        
        with col2:
            gender = st.selectbox(
                "👤 性别",
                options=["男", "女"],
                index=0
            )
        
        # 时辰选择
        shichen_options = {
            "子时 (23:00-00:59)": 0,
            "丑时 (01:00-02:59)": 1,
            "寅时 (03:00-04:59)": 2,
            "卯时 (05:00-06:59)": 3,
            "辰时 (07:00-08:59)": 4,
            "巳时 (09:00-10:59)": 5,
            "午时 (11:00-12:59)": 6,
            "未时 (13:00-14:59)": 7,
            "申时 (15:00-16:59)": 8,
            "酉时 (17:00-18:59)": 9,
            "戌时 (19:00-20:59)": 10,
            "亥时 (21:00-22:59)": 11
        }
        
        shichen = st.selectbox(
            "🕐 出生时辰",
            options=list(shichen_options.keys()),
            index=0
        )
        
        submit_button = st.form_submit_button("🎯 开始排盘", use_container_width=True)
    
    # 处理提交
    if submit_button:
        with st.spinner("正在计算八字..."):
            try:
                # 创建计算器实例
                calculator = BaziCalculator()
                
                # 获取时辰索引
                hour_index = shichen_options[shichen]
                
                # 计算八字
                bazi_result = calculator.calculate_bazi(
                    birth_date.year,
                    birth_date.month,
                    birth_date.day,
                    hour_index
                )
                
                # 十神分析
                analyzer = ShishenAnalyzer()
                shishen_result = analyzer.analyze(bazi_result, gender)
                
                # 显示结果
                display_results(bazi_result, shishen_result)
                
            except Exception as e:
                st.error(f"计算出错：{str(e)}")


def display_results(bazi_result: dict, shishen_result: dict):
    """显示排盘结果"""
    
    st.markdown("---")
    st.markdown("### 📊 排盘结果")
    
    # 四柱展示
    st.markdown('<div class="pillar-container">', unsafe_allow_html=True)
    st.markdown('<div class="pillar-title">四柱八字</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    pillars = [
        ("年柱", bazi_result['year_pillar']),
        ("月柱", bazi_result['month_pillar']),
        ("日柱", bazi_result['day_pillar']),
        ("时柱", bazi_result['hour_pillar'])
    ]
    
    for col, (label, pillar) in zip(cols, pillars):
        with col:
            st.markdown(f"""
                <div class="pillar-item">
                    <div class="pillar-label">{label}</div>
                    <div class="pillar-value">{pillar['gan']}</div>
                    <div class="pillar-value">{pillar['zhi']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 日主信息
    st.markdown("### 🌟 命主信息")
    day_gan = bazi_result['day_pillar']['gan']
    st.info(f"**日主（命主）**: {day_gan}  \n**五行属性**: {get_wuxing(day_gan)}")
    
    # 十神分析
    st.markdown("### 🔍 十神分析")
    
    cols = st.columns(4)
    shishen_pillars = [
        ("年柱", shishen_result['year']),
        ("月柱", shishen_result['month']),
        ("日柱", shishen_result['day']),
        ("时柱", shishen_result['hour'])
    ]
    
    for col, (label, shishen) in zip(cols, shishen_pillars):
        with col:
            st.markdown(f"**{label}**")
            st.markdown(f"天干: `{shishen['gan']}`")
            st.markdown(f"地支: `{shishen['zhi']}`")
    
    # 十神统计
    st.markdown("### 📈 十神统计")
    shishen_count = {}
    for pillar_name in ['year', 'month', 'hour']:  # 不统计日柱
        gan_shishen = shishen_result[pillar_name]['gan']
        zhi_shishen = shishen_result[pillar_name]['zhi']
        shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
        shishen_count[zhi_shishen] = shishen_count.get(zhi_shishen, 0) + 1
    
    if shishen_count:
        cols = st.columns(len(shishen_count))
        for col, (shishen, count) in zip(cols, shishen_count.items()):
            with col:
                st.metric(label=shishen, value=f"{count} 个")


def get_wuxing(gan: str) -> str:
    """获取天干五行属性"""
    wuxing_map = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    return wuxing_map.get(gan, '未知')


if __name__ == "__main__":
    main()