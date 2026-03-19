"""
八字排盘系统 - Streamlit 主应用
特性：提交后重置输入，但保留上次排盘结果展示
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

# ----------------------------
# 默认值（按需修改）
# ----------------------------
DEFAULT_DATE = date(2006, 3, 26)
DEFAULT_GENDER = "男"
DEFAULT_HOUR = 11
DEFAULT_MINUTE = 30

# （可选）用时辰快速选择：这里只负责“帮你填小时”，分钟仍可输入
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
    # 表单控件状态
    st.session_state.setdefault("birth_date", DEFAULT_DATE)
    st.session_state.setdefault("gender", DEFAULT_GENDER)
    st.session_state.setdefault("birth_hour", DEFAULT_HOUR)
    st.session_state.setdefault("birth_minute", DEFAULT_MINUTE)
    st.session_state.setdefault("use_shichen", True)
    st.session_state.setdefault("shichen_label", DEFAULT_SHICHEN_LABEL)

    # 上次结果（用于“重置但保留展示”）
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("last_shishen", None)
    st.session_state.setdefault("last_input", None)


def reset_form_to_default():
    st.session_state["birth_date"] = DEFAULT_DATE
    st.session_state["gender"] = DEFAULT_GENDER
    st.session_state["birth_hour"] = DEFAULT_HOUR
    st.session_state["birth_minute"] = DEFAULT_MINUTE
    st.session_state["use_shichen"] = True
    st.session_state["shichen_label"] = DEFAULT_SHICHEN_LABEL


init_state()

# ----------------------------
# 页面标题
# ----------------------------
st.markdown("## 🔮 八字排盘系统")
st.caption("提交后输入项会重置为默认，但页面会保留上一次排盘结果��")


# ----------------------------
# 结果展示区（放在表单之前，rerun 后也能显示）
# ----------------------------
if st.session_state["last_result"] is not None:
    last_result = st.session_state["last_result"]
    last_input = st.session_state["last_input"] or {}

    st.markdown("### ✅ 上次排盘结果")
    st.info(
        f"出生：{last_input.get('date')} {last_input.get('time')}（性别：{last_input.get('gender')}）"
    )

    st.success(
        "八字："
        f"{last_result['year_pillar']['ganzhi']} "
        f"{last_result['month_pillar']['ganzhi']} "
        f"{last_result['day_pillar']['ganzhi']} "
        f"{last_result['hour_pillar']['ganzhi']}"
    )

    # 四柱五行展示（简洁版）
    with st.expander("��看四柱五行/阴阳", expanded=False):
        for label, key in [("年柱", "year_pillar"), ("月柱", "month_pillar"), ("日柱", "day_pillar"), ("时柱", "hour_pillar")]:
            p = last_result[key]
            st.write(
                f"{label}：{p['ganzhi']} | "
                f"干({p['gan']}:{p['gan_wuxing']}/{p['gan_yinyang']}) "
                f"支({p['zhi']}:{p['zhi_wuxing']}/{p['zhi_yinyang']})"
            )

    st.markdown("---")


# ----------------------------
# 输入表单
# ----------------------------
with st.form("bazi_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        birth_date = st.date_input("📅 出生日期（公历）", key="birth_date")

    with col2:
        gender = st.selectbox("👤 性别", options=["男", "女"], key="gender")

    st.markdown("### ⏰ 出生时间")
    use_shichen = st.toggle("用时辰选择（推荐）", key="use_shichen")

    if use_shichen:
        shichen_label = st.selectbox("时辰", options=list(SHICHEN_TO_HOUR.keys()), key="shichen_label")
        # 这里将 hour 由时辰决定，但仍允许用户改分钟
        birth_hour = SHICHEN_TO_HOUR[shichen_label]
        birth_minute = st.number_input("分钟", min_value=0, max_value=59, key="birth_minute")
    else:
        col3, col4 = st.columns(2)
        with col3:
            birth_hour = st.number_input("小时", min_value=0, max_value=23, key="birth_hour")
        with col4:
            birth_minute = st.number_input("分钟", min_value=0, max_value=59, key="birth_minute")

    submitted = st.form_submit_button("🎯 开始排盘", use_container_width=True)


# ----------------------------
# 提交处理：保存结果 -> 重置输入 -> rerun
# ----------------------------
if submitted:
    try:
        calculator = BaziCalculator()
        analyzer = ShishenAnalyzer()

        result = calculator.calculate_bazi(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            int(birth_hour),
            int(birth_minute),
        )
        shishen = analyzer.analyze(result, gender)

        # 1) 先保存“上次结果”（用于 rerun 后继续展示）
        st.session_state["last_result"] = result
        st.session_state["last_shishen"] = shishen
        st.session_state["last_input"] = {
            "date": birth_date.strftime("%Y-%m-%d"),
            "time": f"{int(birth_hour):02d}:{int(birth_minute):02d}",
            "gender": gender,
        }

        # 2) 再重置表单输入
        reset_form_to_default()

        # 3) rerun：让 UI 立刻显示默认输入，同时展示 last_result
        st.rerun()

    except Exception as e:
        st.error(f"计算出错：{e}")


if __name__ == "__main__":
    main()
