import streamlit as st
import replicate
import requests
from PIL import Image
from io import BytesIO
import os
import glob
import random

# 화면 기본 설정
st.set_page_config(page_title="스마트 사원증 프로필 스튜디오", page_icon="📸")

st.title("📸 사내 스마트 프로필 사진 생성기")
st.write("내 사진만 올리면 AI가 랜덤으로 멋진 정장 템플릿을 골라 합성해 줍니다!")

# [핵심 1] API 키를 프로그램 안에 숨겨서 고정합니다. (화면에는 보이지 않습니다)
# 주의: 아래 "r8_..." 부분에 매니저님의 실제 API 키를 넣어주세요.
API_KEY = "r8_KZgw8z8PnlGnQkV0pERQkTuDiGFfA9T4JL7jH"

# 1. 성별 선택
st.subheader("1. 성별 선택")
gender = st.radio("성별을 선택하세요.", ["남성", "여성"])

# 2. 내 얼굴 사진 업로드
st.subheader("2. 사진 업로드")
st.info("💡 꿀팁: 무표정보다는 입꼬리를 살짝 올린 옅은 미소의 셀카가 가장 자연스럽습니다.")
face_file = st.file_uploader("🧑 내 얼굴 사진 업로드", type=["png", "jpg", "jpeg"])

if face_file is not None:
    st.image(face_file, caption="합성할 내 얼굴", width=250)
    
    if st.button("✨ 랜덤 정장 프로필 만들기 (약 15초 소요)", use_container_width=True):
        with st.spinner("최적의 템플릿을 랜덤으로 선택하여 합성하고 있습니다..."):
            try:
                # 성별에 맞는 템플릿 목록 불러오기
                gender_prefix = "male" if gender == "남성" else "female"
                
                available_templates = []
                for ext in [".jpg", ".jpeg", ".png"]:
                    available_templates.extend(glob.glob(f"{gender_prefix}*suit{ext}"))
                
                if not available_templates:
                    st.error(f"오류: 프로그램 폴더에 '{gender_prefix}'용 정장 파일이 없습니다.")
                    st.stop()

                # [핵심 2] 템플릿 중 하나를 무작위(랜덤)로 선택합니다.
                selected_template = random.choice(available_templates)
                
                st.success(f"🎲 랜덤 뽑기 완료! [{selected_template}] 템플릿이 선택되었습니다.")
                
                # 고정된 API_KEY를 사용하여 AI 엔진 호출
                client = replicate.Client(api_token=API_KEY)
                
                with open("temp_face.jpg", "wb") as f:
                    f.write(face_file.getvalue())
                    
                output = client.run(
                    "lucataco/faceswap:9a4298548422074c3f57258c5d544497314ae4112df80d116f0d2109e843d20d",
                    input={
                        "target_image": open(selected_template, "rb"), 
                        "swap_image": open("temp_face.jpg", "rb")        
                    }
                )
                
                response = requests.get(output)
                result_image = Image.open(BytesIO(response.content))
                
                st.success("완성! 무작위로 선택된 정장이 완벽하게 어우러집니다.")
                st.image(result_image, caption="랜덤 매칭 사내 프로필", width=400)
                
                buf = BytesIO()
                result_image.save(buf, format="PNG")
                st.download_button(
                    label="💾 이 사진 내 컴퓨터에 저장하기",
                    data=buf.getvalue(),
                    file_name="random_matched_profile.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
