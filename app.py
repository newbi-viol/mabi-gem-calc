import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# ---------------------------------------------------------
# 1. 페이지 설정 및 브라우저 번역 강제 차단 (최상단 배치)
# ---------------------------------------------------------
st.set_page_config(
    page_title="마비노기 모바일 세공 계산기", 
    page_icon="💎", 
    layout="wide"
)

# [핵심] 자바스크립트를 이용해 스트림릿의 기본 영어 설정을 한국어로 덮어쓰고 번역을 강제 차단합니다.
components.html(
    """
    <script>
        const parentDoc = window.parent.document;
        parentDoc.documentElement.lang = 'ko';
        parentDoc.documentElement.setAttribute("translate", "no");
        parentDoc.documentElement.classList.add('notranslate');
    </script>
    """,
    height=0, width=0
)

# ---------------------------------------------------------
# 2. 기초 데이터 및 유틸리티 함수
# ---------------------------------------------------------
options_list = ["없음", "강타댐", "방해댐", "원소댐", "보조댐", "연타댐", "생존댐", "소환댐", "이동댐",
                "강타쿨", "방해쿨", "원소쿨", "보조쿨", "연타쿨", "생존쿨", "소환쿨", "이동쿨"]

def get_current_gems():
    gems = []
    for i in range(22):
        gem_opts = [
            st.session_state.get(f"gem_{i}_0", "없음"),
            st.session_state.get(f"gem_{i}_1", "없음"),
            st.session_state.get(f"gem_{i}_2", "없음")
        ]
        gems.append(gem_opts)
    return gems

def clear_single_gem(gem_idx):
    st.session_state[f"gem_{gem_idx}_0"] = "없음"
    st.session_state[f"gem_{gem_idx}_1"] = "없음"
    st.session_state[f"gem_{gem_idx}_2"] = "없음"

def clear_all_gems():
    for i in range(22):
        clear_single_gem(i)

# ---------------------------------------------------------
# 3. 사이드바 구성 
# ---------------------------------------------------------
with st.sidebar:
    st.header("👤 기본 설정")
    char_name = st.text_input("캐릭터명", value="캐릭명을 입력하세요")
    
    st.divider()

    st.header("📸 보석세공 사진 업로드")
    uploaded_images = st.file_uploader("인게임 스크린샷 선택 (다중 가능)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_images:
        st.success(f"✅ {len(uploaded_images)}장의 이미지 로드됨")
        if st.button("🔍 분석 및 자동 채우기", use_container_width=True):
            mock_data = ["강타댐", "방해댐", "없음"] * 22
            opt_idx = 0
            for i in range(22):
                for j in range(3):
                    if opt_idx < len(mock_data):
                        st.session_state[f"gem_{i}_{j}"] = mock_data[opt_idx]
                        opt_idx += 1
            st.rerun()

    st.divider()

    st.header("💾 세공데이터 저장/불러오기")
    uploaded_file = st.file_uploader("📂 저장 파일(.json) 불러오기", type=["json"])
    if uploaded_file is not None:
        try:
            saved_data = json.load(uploaded_file)
            for i in range(22):
                for j in range(3):
                    st.session_state[f"gem_{i}_{j}"] = saved_data[i][j]
            st.success("데이터 로드 완료!")
        except:
            st.error("올바른 형식이 아닙니다.")

    current_data = get_current_gems()
    json_string = json.dumps(current_data, ensure_ascii=False)
    st.download_button("📥 현재 세공 데이터 저장", data=json_string, file_name=f"gem_{char_name}.json", mime="application/json", use_container_width=True)

    st.divider()
    
    st.header("🎯 옵션 가중치 설정")
    valid_opts_for_select = [opt for opt in options_list if opt != "없음"]
    essential_opts = st.multiselect("🔴 필수 (10점)", valid_opts_for_select, default=["강타댐", "방해댐"])
    recommended_opts = st.multiselect("🟡 권장 (5점)", valid_opts_for_select, default=["연타댐", "소환댐"])
    compromise_opts = st.multiselect("🟢 타협 (2점)", valid_opts_for_select, default=[])
    valid_priorities = essential_opts + recommended_opts + compromise_opts

# ---------------------------------------------------------
# 4. 메인 화면: 데이터 입력 영역
# ---------------------------------------------------------
st.title(f"💎 [{char_name}] 보석 세공 관리기")

with st.expander("📝 현재 보석 세공 상태 입력 / 수정하기", expanded=True):
    st.button("🗑️ 전체 데이터 초기화", on_click=clear_all_gems, use_container_width=True)
    cols = st.columns(6)
    for i in range(22):
        col_idx = i % 6
        with cols[col_idx]:
            st.markdown(f"**보석 {i+1}**")
            st.selectbox(f"옵션 1", options_list, key=f"gem_{i}_0", index=0, label_visibility="collapsed")
            st.selectbox(f"옵션 2", options_list, key=f"gem_{i}_1", index=0, label_visibility="collapsed")
            st.selectbox(f"옵션 3", options_list, key=f"gem_{i}_2", index=0, label_visibility="collapsed")
            st.button("❌ 비우기", key=f"clear_btn_{i}", on_click=clear_single_gem, args=(i,), use_container_width=True)
            st.write("")

current_gems = get_current_gems()
flat_gems = [opt for gem in current_gems for opt in gem]
counts_dict = pd.Series(flat_gems).value_counts().to_dict()

# ---------------------------------------------------------
# 5. 보유 현황 및 통계
# ---------------------------------------------------------
st.divider()
st.header("📊 중요도별 옵션 보유 현황")
ce, cr, cc = st.columns(3)
with ce:
    st.markdown("#### 🔴 필수 옵션")
    for p in essential_opts: st.metric(label=p, value=f"{counts_dict.get(p, 0)} 개")
with cr:
    st.markdown("#### 🟡 권장 옵션")
    for p in recommended_opts: st.metric(label=p, value=f"{counts_dict.get(p, 0)} 개")
with cc:
    st.markdown("#### 🟢 타협 옵션")
    for p in compromise_opts: st.metric(label=p, value=f"{counts_dict.get(p, 0)} 개")

with st.expander("🗑️ 기타 잡옵션 현황"):
    others = {o: counts_dict[o] for o in counts_dict if o not in valid_priorities and o != "없음"}
    st.caption(" | ".join([f"{o}: {c}개" for o, c in others.items()]) if others else "잡옵션이 없습니다.")

# ---------------------------------------------------------
# 6. 보석 스왑 추천 (AI 경로 안내)
# ---------------------------------------------------------
st.divider()
st.header("💡 보석 스왑 추천")
st.markdown("점수 상승 폭이 가장 큰 최적의 교체 경로를 제안합니다.")

def get_opt_score(opt):
    if opt in essential_opts: return 10
    if opt in recommended_opts: return 5
    if opt in compromise_opts: return 2
    return 0

curr_counts = counts_dict.copy()
seq_swaps = []
for step in range(1, 4):
    bg, bs, bst = 0, None, None
    for i in range(len(valid_opts_for_select)):
        for j in range(i + 1, len(valid_opts_for_select)):
            oa, ob = valid_opts_for_select[i], valid_opts_for_select[j]
            if ("댐" in oa and "쿨" in ob) or ("쿨" in oa and "댐" in ob): continue
            ca, cb = curr_counts.get(oa, 0), curr_counts.get(ob, 0)
            sa, sb = get_opt_score(oa), get_opt_score(ob)
            gn = (ca * sb + cb * sa) - (ca * sa + cb * sb)
            if gn > bg:
                bg = gn
                d, k = (oa, ob) if sb > sa else (ob, oa)
                new_c = curr_counts.copy()
                new_c[oa], new_c[ob] = cb, ca
                bs = {"단계": f"{step}순위 추천", "교체 대상(많음)": f"{d} ({curr_counts.get(d, 0)}개)", "교체 결과(적음)": f"{k} ({curr_counts.get(k, 0)}개)", "기대 점수 상승": f"+{gn}점"}
                bst = new_c
    if bs:
        seq_swaps.append(bs)
        curr_counts = bst
    else: break

if seq_swaps:
    st.success("✨ **추천된 경로를 아래 시뮬레이터에 적용하여 결과를 확인하세요.**")
    st.dataframe(pd.DataFrame(seq_swaps), use_container_width=True)
else:
    st.info("이미 최적화된 상태입니다.")

# ---------------------------------------------------------
# 7. 시뮬레이터 & 개별 추천 가이드 (통합 Expander)
# ---------------------------------------------------------
with st.expander("🔄 교차 변경 시뮬레이터 & 개별 추천 가이드", expanded=True):
    st.markdown("#### 1️⃣ 시뮬레이터 직접 테스트")
    sc = st.columns(3); sws = []
    for i in range(3):
        with sc[i]:
            sa = st.selectbox(f"이 옵션을...", ["선택안함"]+valid_opts_for_select, key=f"sa_{i}")
            sb = st.selectbox(f"...이 옵션과 교체", ["선택안함"]+valid_opts_for_select, key=f"sb_{i}")
            if sa != "선택안함" and sb != "선택안함" and sa != sb:
                if ("댐" in sa and "쿨" in sb) or ("쿨" in sa and "댐" in sb): st.error("⚠️ 댐/쿨 교체 불가")
                else: sws.append((sa, sb))
    
    if sws:
        sim_f = list(flat_gems)
        for a, b in sws:
            for k in range(len(sim_f)):
                if sim_f[k] == a: sim_f[k] = b
                elif sim_f[k] == b: sim_f[k] = a
        scnt = pd.Series(sim_f).value_counts().reindex(options_list, fill_value=0)
        cdf = pd.DataFrame({"현재 개수": pd.Series(flat_gems).value_counts().reindex(options_list, fill_value=0), "변경 후 개수": scnt})
        cdf["변화량"] = cdf["변경 후 개수"] - cdf["현재 개수"]
        st.markdown("**📊 시뮬레이션 데이터 결과**")
        st.dataframe(cdf[(cdf["현재 개수"]>0)|(cdf["변경 후 개수"]>0)], use_container_width=True)

    st.divider()
    
    st.markdown("#### 2️⃣ 개별 보석 세공 추천 가이드")
    st.caption("가치가 낮은 보석부터 정렬됩니다.")

    def evaluate_gem(opts):
        if opts == ["없음", "없음", "없음"]: return 999 
        s = 0
        for o in opts:
            if o in essential_opts: s += 10
            elif o in recommended_opts: s += 5
            elif o in compromise_opts: s += 2
        return s

    gem_eval = [{"보석 번호": f"보석 {i+1}", "옵션 1": g[0], "옵션 2": g[1], "옵션 3": g[2], "가치 점수": evaluate_gem(g)} for i, g in enumerate(current_gems)]
    df = pd.DataFrame(gem_eval).sort_values(by="가치 점수", ascending=True).reset_index(drop=True)

    def act(s):
        if s >= 999: return "🔒 고정 (유료보석)"
        if s == 0: return "🔴 1순위 교체"
        if s < 5: return "🟠 2순위 교체"
        if s < 10: return "🟡 타협 유지"
        return "🟢 종결 세팅"

    df["추천 행동"] = df["가치 점수"].apply(act)
    df["가치 점수"] = df["가치 점수"].apply(lambda x: "-" if x >= 999 else x)
    st.dataframe(df, use_container_width=True)