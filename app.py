"""
八字排盘系统 - Streamlit 主应用
特性：提交后重置输入，保留上次排盘结果，支持清空结果
"""
import streamlit as st
from datetime import date
from src.bazi_calculator import BaziCalculator
from src.shishen import ShishenAnalyzer

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

# ----------------------------
# 默认值
# ----------------------------
DEFAULT_DATE = date(2006, 3, 26)
DEFAULT_GENDER = "男"
DEFAULT_HOUR = 11
DEFAULT_MINUTE = 30

# 时辰映射
SHICHEN_TO_HOUR = {
    "子时 (23:00-00:59)": 23,
    "丑时 (01:00-02:59)": 1,
    "寅时 (03:00-04:59)": 3,
    "卯时 (05:00-06:59)": 5,
    "辰时 (07:00-08:59)": 7,
    "巳时 (09:00-10:59)": 9,
    "午时 (11:00-12:59)": 11,
    "未时 (13:00-14:59)": 13,
    "申时 (15:00-16:59)": 15,
    "酉时 (17:00-18:59)": 17,
    "戌时 (19:00-20:59)": 19,
    "亥时 (21:00-22:59)": 21,
}

DEFAULT_SHICHEN_LABEL = "午时 (11:00-12:59)"


# ----------------------------
# session_state 初始化
# ----------------------------
def init_state():
    """初始化会话状态"""
    st.session_state.setdefault("birth_date", DEFAULT_DATE)
    st.session_state.setdefault("gender", DEFAULT_GENDER)
    st.session_state.setdefault("birth_hour", DEFAULT_HOUR)
    st.session_state.setdefault("birth_minute", DEFAULT_MINUTE)
    st.session_state.setdefault("use_shichen", True)
    st.session_state.setdefault("shichen_label", DEFAULT_SHICHEN_LABEL)
    
    # 上次结果
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("last_shishen", None)
    st.session_state.setdefault("last_input", None)


def reset_form_to_default():
    """重置表单为默认值"""
    st.session_state["birth_date"] = DEFAULT_DATE
    st.session_state["gender"] = DEFAULT_GENDER
    st.session_state["birth_hour"] = DEFAULT_HOUR
    st.session_state["birth_minute"] = DEFAULT_MINUTE
    st.session_state["use_shichen"] = True
    st.session_state["shichen_label"] = DEFAULT_SHICHEN_LABEL


def clear_last_result():
    """清空上次结果"""
    st.session_state["last_result"] = None
    st.session_state["last_shishen"] = None
    st.session_state["last_input"] = None


init_state()

# ----------------------------
# 页面标题
# ----------------------------
st.markdown('<div class="main-title">🔮 八字排盘系统</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">高精度天文历法算法 · 提交后自动重置输入</div>', unsafe_allow_html=True)


# ----------------------------
# 结果展示区（保留上次结果）
# ----------------------------
if st.session_state["last_result"] is not None:
    last_result = st.session_state["last_result"]
    last_shishen = st.session_state["last_shishen"]
    last_input = st.session_state["last_input"] or {}

    # 标题 + 清空按钮
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("### ✅ 上次排盘结果")
    with col_btn:
        if st.button("🗑️ 清空", use_container_width=True, key="clear_result_btn"):
            clear_last_result()
            st.rerun()

    # 出生信息
    st.info(
        f"📅 **出生日期**: {last_input.get('date', 'N/A')}\n"
        f"🕐 **出生时间**: {last_input.get('time', 'N/A')}\n"
        f"👤 **性别**: {last_input.get('gender', 'N/A')}"
    )

    # 完整八字
    st.success(
        f"**完整八字**: "
        f"{last_result['year_pillar']['ganzhi']} "
        f"{last_result['month_pillar']['ganzhi']} "
        f"{last_result['day_pillar']['ganzhi']} "
        f"{last_result['hour_pillar']['ganzhi']}"
    )

    # 四柱卡片展示
    st.markdown("#### 📊 四柱八字")
    st.markdown('<div class="pillar-container">', unsafe_allow_html=True)
    st.markdown('<div class="pillar-title">四柱详情</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    pillars_data = [
        ("年柱", last_result['year_pillar']),
        ("月柱", last_result['month_pillar']),
        ("日柱", last_result['day_pillar']),
        ("时柱", last_result['hour_pillar'])
    ]

    for col, (label, pillar) in zip(cols, pillars_data):
        with col:
            wuxing_gan_html = f'<span class="wuxing-badge wuxing-{pillar["gan_wuxing"]}">{pillar["gan_wuxing"]}</span>'
            wuxing_zhi_html = f'<span class="wuxing-badge wuxing-{pillar["zhi_wuxing"]}">{pillar["zhi_wuxing"]}</span>'
            yinyang_gan_html = f'<span class="yinyang-badge yinyang-{pillar["gan_yinyang"]}">{pillar["gan_yinyang"]}</span>'
            yinyang_zhi_html = f'<span class="yinyang-badge yinyang-{pillar["zhi_yinyang"]}">{pillar["zhi_yinyang"]}</span>'

            shi_duan_info = ""
            if label == "时柱":
                shi_duan_info = f'<div style="font-size: 0.7em; color: #7f8c8d; margin-top: 0.5em;">{pillar.get("shi_duan", "")}</div>'

            st.markdown(f"""
                <div class="pillar-item">
                    <div class="pillar-label">{label}</div>
                    <div class="pillar-value">{pillar['gan']}</div>
                    <div>{wuxing_gan_html} {yinyang_gan_html}</div>
                    <div class="pillar-value">{pillar['zhi']}</div>
                    <div>{wuxing_zhi_html} {yinyang_zhi_html}</div>
                    {shi_duan_info}
                </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 日主信息
    st.markdown("#### 🌟 命主信息")
    day_gan = last_result['day_pillar']['gan']
    day_gan_wuxing = last_result['day_pillar']['gan_wuxing']
    day_gan_yinyang = last_result['day_pillar']['gan_yinyang']

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("日主（命主）", day_gan)
    with m_col2:
        st.metric("五行属性", day_gan_wuxing)
    with m_col3:
        st.metric("阴阳属性", day_gan_yinyang)

    # 五行统计
    st.markdown("#### 🎨 五行分析")
    wuxing_count = {}
    for pillar_key in ['year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar']:
        pillar = last_result[pillar_key]
        gan_wuxing = pillar['gan_wuxing']
        zhi_wuxing = pillar['zhi_wuxing']
        wuxing_count[gan_wuxing] = wuxing_count.get(gan_wuxing, 0) + 1
        wuxing_count[zhi_wuxing] = wuxing_count.get(zhi_wuxing, 0) + 1

    wuxing_order = ['木', '火', '土', '金', '水']
    wx_cols = st.columns(5)
    for col, wuxing in zip(wx_cols, wuxing_order):
        with col:
            count = wuxing_count.get(wuxing, 0)
            st.metric(label=wuxing, value=f"{count} 个")

    # 十神分析
    st.markdown("#### 🔍 十神分析")
    shishen_cols = st.columns(4)
    shishen_pillars = [
        ("年柱", last_shishen['year']),
        ("月柱", last_shishen['month']),
        ("日柱", last_shishen['day']),
        ("时柱", last_shishen['hour'])
    ]

    for col, (label, shishen) in zip(shishen_cols, shishen_pillars):
        with col:
            st.markdown(f"**{label}**")
            if label == "日柱":
                st.markdown(f"天干: `{shishen['gan']}` (日主)")
            else:
                st.markdown(f"天干: `{shishen['gan']}`")
            st.markdown(f"地支: `{shishen['zhi']}`")

    # 十神统计
    st.markdown("#### 📈 十神统计")
    shishen_count = {}
    for pillar_name in ['year', 'month', 'hour']:
        gan_shishen = last_shishen[pillar_name]['gan']
        zhi_shishen = last_shishen[pillar_name]['zhi']
        shishen_count[gan_shishen] = shishen_count.get(gan_shishen, 0) + 1
        shishen_count[zhi_shishen] = shishen_count.get(zhi_shishen, 0) + 1

    day_zhi_shishen = last_shishen['day']['zhi']
    shishen_count[day_zhi_shishen] = shishen_count.get(day_zhi_shishen, 0) + 1

    if shishen_count:
        sorted_shishen = sorted(shishen_count.items(), key=lambda x: x[1], reverse=True)
        num_cols = min(len(sorted_shishen), 5)
        ss_cols = st.columns(num_cols)

        for col, (shishen, count) in zip(ss_cols, sorted_shishen[:5]):
            with col:
                st.metric(label=shishen, value=f"{count} 个")

        if len(sorted_shishen) > 5:
            st.markdown("**其他十神**:")
            remaining = sorted_shishen[5:]
            remaining_text = " | ".join([f"{s}: {c}个" for s, c in remaining])
            st.text(remaining_text)

    st.markdown("---")


# ----------------------------
# 输入表单
# ----------------------------
with st.form("bazi_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        birth_date = st.date_input(
            "📅 出生日期（公历）",
            key="birth_date",
            min_value=date(1900, 1, 1),
            max_value=date(2100, 12, 31)
        )

    with col2:
        gender = st.selectbox(
            "👤 性别",
            options=["男", "女"],
            key="gender"
        )

    st.markdown("### ⏰ 出生时间")
    use_shichen = st.toggle("用时辰选择（推荐）", key="use_shichen")

    if use_shichen:
        shichen_label = st.selectbox(
            "时辰",
            options=list(SHICHEN_TO_HOUR.keys()),
            key="shichen_label"
        )
        birth_hour = SHICHEN_TO_HOUR[shichen_label]
        birth_minute = st.number_input(
            "分钟",
            min_value=0,
            max_value=59,
            key="birth_minute"
        )
    else:
        col3, col4 = st.columns(2)
        with col3:
            birth_hour = st.number_input(
                "小时",
                min_value=0,
                max_value=23,
                key="birth_hour"
            )
        with col4:
            birth_minute = st.number_input(
                "分钟",
                min_value=0,
                max_value=59,
                key="birth_minute"
            )

    submitted = st.form_submit_button("🎯 开始排盘", use_container_width=True)


# ----------------------------
# 提交处理
# ----------------------------
if submitted:
    try:
        calculator = BaziCalculator()
        analyzer = ShishenAnalyzer()

        # 确保 hour 和 minute 都是 int
        birth_hour_int = int(birth_hour)
        birth_minute_int = int(birth_minute)

        result = calculator.calculate_bazi(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_hour_int,
            birth_minute_int,
        )
        shishen = analyzer.analyze(result, gender)

        # 保存结果
        st.session_state["last_result"] = result
        st.session_state["last_shishen"] = shishen
        st.session_state["last_input"] = {
            "date": birth_date.strftime("%Y年%m月%d日"),
            "time": f"{birth_hour_int:02d}:{birth_minute_int:02d}",
            "gender": gender,
        }

        # 重置表单
        reset_form_to_default()

        # 重新运行页面
        st.rerun()

    except Exception as e:
        st.error(f"❌ 计算出错：{str(e)}")
        import traceback
        with st.expander("查看错误详情"):
            st.code(traceback.format_exc())
