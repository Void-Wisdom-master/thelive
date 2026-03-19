"""
八字排盘系统 - Streamlit 主应用（修正版）
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
        margin-bottom: 0.3em;
    }
    .pillar-value {
        color: #2c3e50;
        font-size: 2em;
        font-weight: bold;
        margin: 0.2em 0;
    }
    .wuxing-badge {
        display: inline-block;
        padding: 0.2em 0.6em;
        border-radius: 12px;
        font-size: 0.75em;
        font-weight: bold;
        margin: 0.2em;
    }
    .wuxing-木 { background: #27ae60; color: white; }
    .wuxing-火 { background: #e74c3c; color: white; }
    .wuxing-土 { background: #f39c12; color: white; }
    .wuxing-金 { background: #95a5a6; color: white; }
    .wuxing-水 { background: #3498db; color: white; }
    .yinyang-badge {
        display: inline-block;
        padding: 0.15em 0.5em;
        border-radius: 10px;
        font-size: 0.7em;
        margin: 0.2em;
    }
    .yinyang-阳 { background: #fff3cd; color: #856404; }
    .yinyang-阴 { background: #d1ecf1; color: #0c5460; }
    </style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 标题
    st.markdown('<div class="main-title">🔮 八字排盘系统</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">高精度儒略日算法 · 标准天文历法</div>', unsafe_allow_html=True)
    
    # 创建表单
    with st.form("bazi_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input(
                "📅 出生日期（公历）",
                value=datetime(2006, 3, 26),
                min_value=datetime(1900, 1, 1),
                max_value=datetime(2100, 12, 31)
            )
        
        with col2:
            gender = st.selectbox(
                "👤 性别",
                options=["男", "女"],
                index=0
            )
        
        # 时间选择
        col3, col4 = st.columns(2)
        with col3:
            birth_hour = st.number_input("⏰ 出生小时", min_value=0, max_value=23, value=11)
        with col4:
            birth_minute = st.number_input("⏰ 出生分钟", min_value=0, max_value=59, value=30)
        
        submit_button = st.form_submit_button("🎯 开始排盘", use_container_width=True)
    
    # 处理提交
    if submit_button:
        with st.spinner("正在计算八字..."):
            try:
                # 创建计算器实例
                calculator = BaziCalculator()
                
                # 计算八字
                bazi_result = calculator.calculate_bazi(
                    birth_date.year,
                    birth_date.month,
                    birth_date.day,
                    birth_hour,
                    birth_minute
                )
                
                # 十神分析
                analyzer = ShishenAnalyzer()
                shishen_result = analyzer.analyze(bazi_result, gender)
                
                # 显示结果
                display_results(bazi_result, shishen_result, birth_date, birth_hour, birth_minute)
                
            except Exception as e:
                st.error(f"计算出错：{str(e)}")
                import traceback
                st.error(traceback.format_exc())


def display_results(bazi_result: dict, shishen_result: dict, birth_date, birth_hour: int, birth_minute: int):
    """显示排盘结果"""
    
    st.markdown("---")
    
    # 显示时间信息
    st.info(f"**📅 出生时间（公历）**: {birth_date.strftime('%Y年%m月%d日')} {birth_hour:02d}:{birth_minute:02d}")
    
    # 四柱展示
    st.markdown("### 📊 四柱八字")
    st.markdown('<div class="pillar-container">', unsafe_allow_html=True)
    
    cols = st.columns(4)
    pillars = [
        ("年柱", bazi_result['year_pillar']),
        ("月柱", bazi_result['month_pillar']),
        ("日柱", bazi_result['day_pillar']),
        ("时柱", bazi_result['hour_pillar'])
    ]
    
    for col, (label, pillar) in zip(cols, pillars):
        with col:
            wuxing_gan_html = f'<span class="wuxing-badge wuxing-{pillar["gan_wuxing"]}">{pillar["gan_wuxing"]}</span>'
            wuxing_zhi_html = f'<span class="wuxing-badge wuxing-{pillar["zhi_wuxing"]}">{pillar["zhi_wuxing"]}</span>'
            yinyang_gan_html = f'<span class="yinyang-badge yinyang-{pillar["gan_yinyang"]}">{pillar["gan_yinyang"]}</span>'
            yinyang_zhi_html = f'<span class="yinyang-badge yinyang-{pillar["zhi_yinyang"]}">{pillar["zhi_yinyang"]}</span>'
            
            extra_info = ""
            if label == "时柱":
                extra_info = f'<div style="font-size: 0.7em; color: #7f8c8d; margin-top: 0.5em;">{pillar.get("shi_duan", "")}</div>'
            
            st.markdown(f"""
                <div class="pillar-item">
                    <div class="pillar-label">{label}</div>
                    <div class="pillar-value">{pillar['gan']}</div>
                    <div>{wuxing_gan_html} {yinyang_gan_html}</div>
                    <div class="pillar-value">{pillar['zhi']}</div>
                    <div>{wuxing_zhi_html} {yinyang_zhi_html}</div>
                    {extra_info}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 显示完整干支
    st.success(f"**完整八字**: {bazi_result['year_pillar']['ganzhi']} {bazi_result['month_pillar']['ganzhi']} {bazi_result['day_pillar']['ganzhi']} {bazi_result['hour_pillar']['ganzhi']}")
    
    # 日主信息
    st.markdown("### 🌟 命主信息")
    day_gan = bazi_result['day_pillar']['gan']
    day_gan_wuxing = bazi_result['day_pillar']['gan_wuxing']
    day_gan_yinyang = bazi_result['day_pillar']['gan_yinyang']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("日主（命主）", day_gan)
    with col2:
        st.metric("五行属性", day_gan_wuxing)
    with col3:
        st.metric("阴阳属性", day_gan_yinyang)
    
    # 五行统计
    st.markdown("### 🎨 五行分析")
    wuxing_count = {}
    for pillar_key in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
        pillar = bazi_result[pillar_key]
        gan_wuxing = pillar['gan_wuxing']
        zhi_wuxing = pillar['zhi_wuxing']
        wuxing_count[gan_wuxing] = wuxing_count.get(gan_wuxing, 0) + 1
        wuxing_count[zhi_wuxing] = wuxing_count.get(zhi_wuxing, 0) + 1
    
    # 按照五行顺序显示
    wuxing_order = ['木', '火', '土', '金', '水']
    cols = st.columns(5)
    for col, wuxing in zip(cols, wuxing_order):
        with col:
            count = wuxing_count.get(wuxing, 0)
            st.metric(label=wuxing, value=f"{count} 个")
    
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
            if label == "日柱":
                st.markdown(f"天干: `{shishen['gan']}` (日主)")
            else:
                st.markdown(f"天干: `{shishen['gan']}`")
            st.markdown(f"地支: `{shishen['zhi']}`")
    
    # 十神统计
    st.markdown("### 📈 十神统计")
    shishen_count = {}
    for pillar_name in ['year', 'month', 'hour']:
        gan_shishen = shishen_result[pillar_name]['gan']
        zhi_shishen = shishen_result[pillar_name]['zhi']
        shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
        shishen_count[zhi_shishen] = shishen_count.get(zhi_shishen, 0) + 1
    
    day_zhi_shishen = shishen_result['day']['zhi']
    shishen_count[day_zhi_shishen] = shishen_count.get(day_zhi_shishen, 0) + 1
    
    if shishen_count:
        sorted_shishen = sorted(shishen_count.items(), key=lambda x: x[1], reverse=True)
        num_cols = min(len(sorted_shishen), 5)
        cols = st.columns(num_cols)
        
        for col, (shishen, count) in zip(cols, sorted_shishen[:5]):
            with col:
                st.metric(label=shishen, value=f"{count} 个")
        
        # 如果超过5个，显示剩余的
        if len(sorted_shishen) > 5:
            st.markdown("**其他十神**:")
            remaining = sorted_shishen[5:]
            remaining_text = " | ".join([f"{s}: {c}个" for s, c in remaining])
            st.text(remaining_text)


if __name__ == "__main__":
    main()
