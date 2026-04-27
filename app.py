import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

# ---------------------------------------------------------
# 🛑 OCR 및 이미지 처리 라이브러리 로드
# ---------------------------------------------------------
try:
    import easyocr
    import numpy as np
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ---------------------------------------------------------
# 1. 페이지 설정 및 브라우저 번역 강제 차단
# ---------------------------------------------------------
st.set_page_config(page_title="마비노기 모바일 세공 계산기", page_icon="💎", layout="wide")

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
# 2. 기초 데이터 및 판독 로직
# ---------------------------------------------------------
options_list = ["없음", "강타댐", "방해댐", "원소댐", "보조댐", "연타댐", "생존댐", "소환댐", "이동댐",
                "강타쿨", "방해쿨", "원소쿨", "보조쿨", "연타쿨", "생존쿨", "소환쿨", "이동쿨"]

def get_all_state_data(char_name, ess, rec, com):
    gems = []
    for i in range(22):
        gem_opts = [st.session_state.get(f"gem_{i}_0", "없음"),
                    st.session_state.get(f"gem_{i}_1", "없음"),
                    st.session_state.get(f"gem_{i}_2", "없음")]
        gems.append(gem_opts)
    
    return {
        "char_name": char_name,
        "ess_opts": ess,
        "rec_opts": rec,
        "com_opts": com,
        "gems_data": gems
    }

def clear_all_gems():
    for i in range(22):
        for j in range(3): st.session_state[f"gem_{i}_{j}"] = "없음"

def parse_ocr_text_to_option(ocr_text):
    text = ocr_text.replace(" ", "") 
    skills = ["강타", "방해", "원소", "보조", "연타", "생존", "소환", "이동"]
    target_skill = next((s for s in skills if s in text), None)
    if not target_skill: return "없음"
    if any(k in text for k in ["대미지", "강화"]): return target_skill + "댐"
    if any(k in text for k in ["대기시간", "쿨", "감소"]): return target_skill + "쿨"
    return "없음"

# ---------------------------------------------------------
# 3. 사이드바 
# ---------------------------------------------------------
with st.sidebar:
    st.header("👤 기본 설정")
    char_name = st.text_input("캐릭터명", value=st.session_state.get("char_name", ""), placeholder="캐릭터명을 입력하세요")
    st.session_state["char_name"] = char_name
    
    st.divider()
    
    st.header("📸 보석세공 사진 업로드")
    uploaded_images = st.file_uploader("인게임 스크린샷 (다중 가능)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    if uploaded_images and st.button("🔍 분석 및 자동 채우기", use_container_width=True):
        if OCR_AVAILABLE:
            with st.spinner("AI가 옵션을 정밀 분석 중입니다..."):
                reader = easyocr.Reader(['ko', 'en'])
                extracted = []
                for img_file in uploaded_images:
                    result = reader.readtext(np.array(Image.open(img_file)))
                    for (_, text, _) in result:
                        parsed = parse_ocr_text_to_option(text)
                        if parsed != "없음": extracted.append(parsed)
                for i in range(22):
                    for j in range(3):
                        if (i*3 + j) < len(extracted): st.session_state[f"gem_{i}_{j}"] = extracted[i*3 + j]
            st.rerun()

    st.divider()
    
    st.header("💾 세공데이터 저장/불러오기")
    uploaded_file = st.file_uploader("📂 저장 파일(.json) 불러오기", type=["json"])
    
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            st.session_state["char_name"] = data.get("char_name", "")
            st.session_state["ess_save"] = data.get("ess_opts", [])
            st.session_state["rec_save"] = data.get("rec_opts", [])
            st.session_state["com_save"] = data.get("com_opts", [])
            
            gems = data.get("gems_data", [])
            for i in range(22):
                for j in range(3):
                    st.session_state[f"gem_{i}_{j}"] = gems[i][j]
            st.success("모든 세팅 정보 로드 완료!")
        except Exception:
            st.error("파일 형식 오류")

# ---------------------------------------------------------
# 4. 메인 화면 (탭 구성)
# ---------------------------------------------------------
tab_main, tab_guide = st.tabs(["💎 보석 세공 계산기", "📖 사용 설명서"])

with tab_main:
    st.title("보석세공 가이드(ver 1.0)")
    if char_name:
        st.caption(f"현재 관리 중인 캐릭터: **{char_name}**")
    
    with st.expander("📝 현재 보석 상태 (수동 수정 가능)", expanded=False):
        st.button("🗑️ 전체 데이터 초기화", on_click=clear_all_gems)
        cols = st.columns(6)
        for i in range(22):
            with cols[i%6]:
                st.markdown(f"**보석 {i+1}**")
                for j in range(3): st.selectbox(f"L{j}", options_list, key=f"gem_{i}_{j}", index=0, label_visibility="collapsed")

    st.subheader("🎯 타겟 옵션 설정")
    v_opts = [o for o in options_list if o != "없음"]
    col_w1, col_w2, col_w3 = st.columns(3)
    
    with col_w1: 
        ess = st.multiselect("🔴 필수(10점)", v_opts, default=st.session_state.get("ess_save", []))
    with col_w2: 
        rec = st.multiselect("🟡 권장(5점)", v_opts, default=st.session_state.get("rec_save", []))
    with col_w3: 
        com = st.multiselect("🟢 타협(2점)", v_opts, default=st.session_state.get("com_save", []))
    
    current_full_state = get_all_state_data(char_name, ess, rec, com)
    with st.sidebar:
        st.download_button("📥 세공 데이터 저장", 
                           data=json.dumps(current_full_state, ensure_ascii=False), 
                           file_name=f"MabiGem_{char_name}.json", 
                           use_container_width=True)

    flat_gems = []
    for i in range(22):
        for j in range(3): flat_gems.append(st.session_state.get(f"gem_{i}_{j}", "없음"))
    cnts = pd.Series(flat_gems).value_counts().to_dict()
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("필수 옵션", f"{sum(cnts.get(o,0) for o in ess)}개")
    c2.metric("권장 옵션", f"{sum(cnts.get(o,0) for o in rec)}개")
    c3.metric("타협 옵션", f"{sum(cnts.get(o,0) for o in com)}개")

    st.subheader("💡 보석 스왑 추천")
    def get_s(o): return 10 if o in ess else 5 if o in rec else 2 if o in com else 0
    
    curr_counts = cnts.copy()
    seq_swaps = []
    for step in range(1, 4):
        bg, bs, bst = 0, None, None
        for i in range(len(v_opts)):
            for j in range(i + 1, len(v_opts)):
                oa, ob = v_opts[i], v_opts[j]
                if ("댐" in oa and "쿨" in ob) or ("쿨" in oa and "댐" in ob): continue
                ca, cb = curr_counts.get(oa, 0), curr_counts.get(ob, 0)
                sa, sb = get_s(oa), get_s(ob)
                gn = (ca * sb + cb * sa) - (ca * sa + cb * sb)
                if gn > bg:
                    bg = gn
                    d, k = (oa, ob) if sb > sa else (ob, oa)
                    new_c = curr_counts.copy()
                    new_c[oa], new_c[ob] = cb, ca
                    bs = {"단계": f"{step}순위", "교체 대상": f"{d} ({curr_counts.get(d, 0)}개)", "교체 결과": f"{k} ({curr_counts.get(k, 0)}개)", "이득": f"+{gn}점"}
                    bst = new_c
        if bs:
            seq_swaps.append(bs)
            curr_counts = bst
        else: break

    if seq_swaps: st.table(pd.DataFrame(seq_swaps))
    else: st.info("모든 옵션이 최적화되어 있거나 타겟 옵션이 설정되지 않았습니다.")
    
    with st.expander("🔄 시뮬레이터 & 개별 추천 가이드", expanded=True):
        st.info("시뮬레이션을 통해 옵션 교체 후의 예상 데이터를 확인하세요.")
        sc = st.columns(3); sws = []
        for i in range(3):
            with sc[i]:
                sa = st.selectbox(f"이 옵션을... ({i+1})", ["선택안함"]+v_opts, key=f"sa_{i}")
                sb = st.selectbox(f"...이걸로 변경 ({i+1})", ["선택안함"]+v_opts, key=f"sb_{i}")
                if sa != "선택안함" and sb != "선택안함" and sa != sb:
                    if ("댐" in sa and "쿨" in sb) or ("쿨" in sa and "댐" in sb): st.error("댐/쿨 교체 불가")
                    else: sws.append((sa, sb))
        
        if sws:
            sim_f = list(flat_gems)
            for a, b in sws:
                for k in range(len(sim_f)):
                    if sim_f[k] == a: sim_f[k] = b
                    elif sim_f[k] == b: sim_f[k] = a
            scnt = pd.Series(sim_f).value_counts().reindex(options_list, fill_value=0)
            cdf = pd.DataFrame({"현재": pd.Series(flat_gems).value_counts().reindex(options_list, fill_value=0), "변경 후": scnt})
            cdf["증감"] = cdf["변경 후"] - cdf["현재"]
            st.dataframe(cdf[(cdf["현재"]>0)|(cdf["변경 후"]>0)], use_container_width=True)

        st.divider()
        st.markdown("#### 🛠️ 개별 보석 세공 추천 가이드")
        def eval_gem(opts):
            if opts == ["없음", "없음", "없음"]: return 999 
            s = sum(get_s(o) for o in opts)
            return s
            
        gem_eval = []
        for i in range(22):
            g = [st.session_state.get(f"gem_{i}_{j}", "없음") for j in range(3)]
            gem_eval.append({"보석 번호": f"보석 {i+1}", "옵션 1": g[0], "옵션 2": g[1], "옵션 3": g[2], "점수": eval_gem(g)})
        
        df = pd.DataFrame(gem_eval).sort_values(by="점수", ascending=True).reset_index(drop=True)
        def act(s):
            if s >= 999: return "🔒 고정 (유료)"
            if s >= 22: return "🌟 종결"
            if s >= 20: return "✨ 준종결"
            if s >= 15: return "🟢 타협"
            if s >= 10: return "🟡 최소"
            return "🔴 변경"
        df["추천 행동"] = df["점수"].apply(act)
        df["점수"] = df["점수"].apply(lambda x: "-" if x >= 999 else x)
        st.dataframe(df, use_container_width=True)

# --- [탭 2: 사용 설명서] ---
with tab_guide:
    st.title("📖 사용 설명서")
    
    st.header("1. 빠른 실행 순서")
    st.markdown("""
    1. 왼쪽 사이드바 **캐릭터명** 입력 
    2. 사이드바 **사진 업로드** 후 **🔍 분석 및 자동 채우기** 클릭
    3. 메인 화면 **🎯 타겟 옵션 설정**에서 본인 직업의 유효 옵션 선택
    4. **💡 보석 스왑 추천**과 **🛠️ 추천 가이드**를 보고 세팅 최적화
    5. 세팅이 끝나면 **📥 세공 데이터 저장**을 눌러 파일로 보관
    """)
    
    st.header("2. 스크린샷 촬영 가이드")
    st.write("아이템 가방에서 장비를 클릭했을 때 나오는 상세 옵션 창을 캡처해 주세요.")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.info("✅ **올바른 캡처 예시**")
        # 📸 깃허브에 '예시.png' 이름으로 파일이 잘 올라가 있어야 이미지가 뜹니다!
        try:
            st.image("예시.png", caption="이렇게 캡처해 주세요!", use_container_width=True) 
        except:
            st.error("이미지 파일을 찾을 수 없습니다. 깃허브에 '예시.png' 파일이 있는지 확인해 주세요.")
            
        st.markdown("- **스타프리즘**의 상세 옵션이 선명하게 보여야 합니다.\n- 옵션 텍스트(#연타, #생존 등)가 잘리지 않게 찍어주세요.\n- 여러 장의 보석을 한 번에 찍은 긴 스크린샷도 지원합니다.")
        
    with col_g2:
        st.warning("⚠️ **주의 사항**\n- UI가 너무 작으면 인식이 어려울 수 있음\n- 여러 장을 한 번에 올리면 1번 보석부터 순서대로 채워짐\n- 배경이 너무 밝거나 글자가 겹치면 인식이 안 될 수 있습니다.")

    st.header("3. 평가 등급 (추천 행동)")
    st.markdown("""
    - **🌟 종결 (22점↑)**: 베스트 옵션 2개에 유효 옵션이 하나 더 붙은 최상급 상태
    - **✨ 준종결 (20점↑)**: 베스트 옵션 2개가 붙은 아주 훌륭한 상태
    - **🟢 타협 (15점↑)**: 필수 1개와 권장 옵션이 적절히 섞인 상태
    - **🟡 최소 (10점↑)**: 필수 옵션이 1개라도 붙어 있는 최소한의 세이브 라인
    - **🔴 변경**: 유효 옵션이 부족하여 다시 세공하는 것을 권장
    """)
