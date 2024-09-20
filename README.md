# **👨🏻‍💻 JBTI**
### 유저의 MBTI유형을 바탕으로 직업을 추천해주는 어플리케이션 서비스
* 인원 : 4명
* 기간 : 2024.06.24 ~ 2024.08.02
![1](https://github.com/user-attachments/assets/3f4098bd-66bc-466f-b68d-87b8ae02041b)

<br>

# 💡프로젝트 기획
‘한국경영자총협회’에서 실시한 『2023년 신규채용 실태조사』와 JOBKOREA의 『첫 직장 유지-퇴사 이유 조사』에서 취업을 했던 구직자들은 업무가 적성에 맞지 않아 퇴사를 하고
적상이 맞아 직장을 유지하고 있다는 것을 알 수 있었습니다. 또한 구직 플랫폼에서도 적성과 직무를 연관지어주는 프로그램을 이행하는 추세를 보였습니다.
MBTI는 개인의 성격과 적성을 잘 보여주고 있는 지표이자 신뢰하고 있는 지표와 Holland 직업 적성검사, 한국고용정보원에서 제공하는 <재직자조사_성격_지식>을 활용하여 간단하게 직업을 추천해주어 
사용자에게 직업에 대한 고민을 해소하고자 위 프로젝트를 기획하게 되었습니다.

<br>

# **✅ Process&Roll**
### Process
- 기획, 데이터 전처리-구성, 모델학습, 프론트구현, 서버구현, 서버배포, PPT제작, 발표
### 🔑 My Role
- 기획, 데이터 전처리-구성, 모델학습, 배포, PPT제작, 발표
<br>

# 💾 DataSet & Model
### DataSet
![7](https://github.com/user-attachments/assets/4d639428-b09f-4de3-8a97-259c9a7d8d30)
### Model



# **📖 Service Explain**
![6](https://github.com/user-attachments/assets/fb9bd1f1-2a8d-4050-aa24-3e7e053e53ef)
![10](https://github.com/user-attachments/assets/d3b4e10f-c720-451c-b628-1229888fb0c9)
![11](https://github.com/user-attachments/assets/29b7a985-97e9-4b6e-8229-070b609c4f06)
![12](https://github.com/user-attachments/assets/93c78014-3192-48f0-8c42-da40b27326c8)

<br>

# **📍 Result**
- 처음 기획을 할때 정확한 결과를 도출하기 위해 KoBert, jhagn, klue 한국어 자연어처리 모델을 동시에 사용하여 유사도를 계산 했을 때 기준치(70%)를 넘은 모델을 이용하여 임베딩과 문장 생성을 하도록 설계를 하였습니다. 하지만 생각보다 모델의 성능이 좋지 못했고 원인을 찾다보니 데이터의 양이 부족하여 유사도를 계산하는 과정에서 원하는 기준치를 못 넘는 다는 것을 알게 되었습니다. 그래서 데이터를 추가하고 데이터 전처리 과정에서 활용할 데이터와 그렇지 않은 데이터에 대해 분류하니 값이 생성되는 것을 볼 수 있었습니다. 하지만 배포를 진행할 때 모델을 3개를 사용하다보니 서버에서 모델이 무거워 배포가 잘 안되고 문장 생성시 시간이 오래 걸리는 점을 발견했습니다. 해결책을 찾기 위해 finetuning을 지원하는 text-embedding-ada-002모델로 임베딩을 진행하고 임베딩 코드를 분리하여 MongoDB에 저장을 한 후 문장을 생성하는 creat.py에서 임베딩 값을 가져와 사전에 미리 finetuning을 진행한 GPT3-turbo-pro모델을 이용하여 유사도 계산과 문장 생성을 하여 배포와 문장 생성 시간을 단축할 수 있었습니다.
- 결과적으로 팀장이라는 역할을 처음 맡았지만 저를 믿고 따라와준 팀원들과 함께 여러번의 고비가 있었지만 함께 이겨내는 과정에서 보람을 느꼈습니다. 무엇보다 자연어 전처리-학습으로 이어지는 과정에서 원하는 결과가 제대로 도출되지 않았던 부분에서 데이터의 양과 전처리가 얼마나 중요한지 깨달을 수 있었습니다. 비록 공모전에 참가하여 수상이라는 결과를 받지는 못했지만 프로젝트를 진행하고 팀원들과 소통-극복해가는 과정에서 눈에 띄는 성과를 얻어 매우 보람있었던 프로젝트였습니다.


<br>

# **🛠️ Skill&Tool**
<img alt="Html" src ="https://img.shields.io/badge/HTML5-E34F26.svg?&style=for-the-badge&logo=HTML5&logoColor=white"/> <img alt="Css" src ="https://img.shields.io/badge/CSS3-1572B6.svg?&style=for-the-badge&logo=CSS3&logoColor=white"/> <img alt="JavaScript" src ="https://img.shields.io/badge/JavaScriipt-F7DF1E.svg?&style=for-the-badge&logo=JavaScript&logoColor=black"/> <img alt="Python" src ="https://img.shields.io/badge/Python-3776AB.svg?&style=for-the-badge&logo=Python&logoColor=white"/> <img alt="FastAPI" src ="https://img.shields.io/badge/fastapi-009688.svg?&style=for-the-badge&logo=Python&logoColor=white"/>
<br>
<img alt="MongoDB" src ="https://img.shields.io/badge/MongoDB-47A248.svg?&style=for-the-badge&logo=Python&logoColor=white"/>
<img alt="AWS" src ="https://img.shields.io/badge/amazonec2-FF9900.svg?&style=for-the-badge&logo=Python&logoColor=white"/>
<img alt="googleplay" src ="https://img.shields.io/badge/googleplay-414141.svg?&style=for-the-badge&logo=Python&logoColor=white"/>





