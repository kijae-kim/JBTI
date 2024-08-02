import pandas as pd
import json
import openai
import logging
import datetime
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
import re  
# from soynlp.normalizer import repeat_normalize
# from soynlp.tokenizer import LTokenizer
import numpy as np  
import os

import certifi

ca = certifi.where()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenAI API 키 설정
openai.api_key = "[API_KEY]"


# MongoDB 연결 설정
def get_mongodb_client(uri: str):
    try:
        client = MongoClient(uri, tlsCAFile=ca)
        logging.info("MongoDB 연결 성공")
        return client
    except Exception as e:
        logging.error(f"MongoDB 연결 실패: {e}")
        raise e

# MongoDB에서 데이터 로드 함수
def load_data_from_mongodb(client: MongoClient, db_name: str, collection_name: str):
    try:
        db = client[db_name]
        collection = db[collection_name]
        data = list(collection.find())
        logging.info(f"{collection_name}에서 데이터 로드 성공")
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"{collection_name}에서 데이터 로드 실패: {e}")
        raise e

# 설정 파일 로드
def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logging.info("설정 파일 로드 성공")
        return config
    except Exception as e:
        logging.error(f"설정 파일 로드 실패: {e}")
        raise e

# 설정 파일 로드
def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logging.info("설정 파일 로드 성공")
        return config
    except Exception as e:
        logging.error(f"설정 파일 로드 실패: {e}")
        raise e

# 텍스트 전처리
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
    text = ' '.join(text.split())
    return text

# 데이터 준비 함수
def prepare_data(config, client):
    try:
        db_name = config['mongodb']['db_name']
        mbti_detail_collection = config['mongodb']['collections']['mbti_detail']
        holland_result_collection = config['mongodb']['collections']['holland_result']
        job_detail_collection = config['mongodb']['collections']['job_detail']
        mbti_holland_collection = config['mongodb']['collections']['mbti_holland']
        
        mbti_detail_df = load_data_from_mongodb(client, db_name, mbti_detail_collection)
        holland_result_df = load_data_from_mongodb(client, db_name, holland_result_collection)
        job_detail_df = load_data_from_mongodb(client, db_name, job_detail_collection)
        mbti_holland_df = load_data_from_mongodb(client, db_name, mbti_holland_collection)
        
        if mbti_detail_df.empty or holland_result_df.empty or job_detail_df.empty or mbti_holland_df.empty:
            raise ValueError("데이터 로딩에 실패했습니다.")
        
        mbti_detail_df = mbti_detail_df.merge(mbti_holland_df, how='left', left_on='유형', right_on='MBTI 명칭')
        
        mbti_detail_df['processed_특징'] = mbti_detail_df['특징'].apply(preprocess_text)
        holland_result_df['processed_상세설명'] = holland_result_df['상세 설명'].apply(preprocess_text)
        job_detail_df['processed_직업 설명'] = job_detail_df['직업 설명'].apply(preprocess_text)
        job_detail_df['processed_직무'] = job_detail_df['직무'].apply(preprocess_text)

        logging.info("데이터 준비 완료")
        return mbti_detail_df, holland_result_df, job_detail_df
    except Exception as e:
        logging.error(f"데이터 준비 중 오류 발생: {e}")
        raise e

# MongoDB에서 임베딩 로드 함수
def load_embeddings_from_mongodb(client, db_name, collection_name):
    try:
        db = client[db_name]
        collection = db[collection_name]
        embeddings_data = collection.find_one()
        mbti_embeddings = np.array(embeddings_data['mbti_embeddings'])
        holland_embeddings = np.array(embeddings_data['holland_embeddings'])
        job_embeddings = np.array(embeddings_data['job_embeddings'])
        logging.info(f"{collection_name}에서 임베딩 로드 성공")
        return mbti_embeddings, holland_embeddings, job_embeddings
    except Exception as e:
        logging.error(f"{collection_name}에서 임베딩 로드 실패: {e}")
        raise e

# 결과 생성 및 출력 함수
def generate_results(mbti_detail_df, holland_result_df, mbti_embeddings, holland_embeddings, fine_tuned_model):
    results = []
    for mbti_idx, mbti_row in mbti_detail_df.iterrows():
        best_match = None
        best_score = 0
        best_model = None
        mbti_emb = mbti_embeddings[mbti_idx].reshape(1, -1)
        similarities = cosine_similarity(mbti_emb, holland_embeddings).flatten()
        max_sim_idx = np.argmax(similarities)
        max_sim = similarities[max_sim_idx]
        if max_sim > best_score:
            best_score = max_sim
            best_match = holland_result_df.iloc[max_sim_idx]
            best_model = fine_tuned_model
        result = {
            'MBTI': mbti_row['유형'],
            'Best Match Holland Code': best_match.get('검사 코드 조합', 'N/A'),
            'Best Match Description': best_match.get('상세 설명', 'N/A'),
            'Best Model': best_model,
            'Similarity Score': best_score
        }
        results.append(result)
        logging.info(f"Generated result for MBTI {result['MBTI']}: {result}")
    logging.info(f"Total results generated: {len(results)}")
    return results

# 최종 결과 생성 함수
def final_results(user_mbti, user_job, mbti_detail_df, job_detail_df, mbti_embeddings, job_embeddings, results, client, config, ttl_seconds):
    logging.debug(f"최종 결과 생성 중, 사용자 MBTI: {user_mbti}, 사용자 직업: {user_job}")

    user_result = next((result for result in results if result['MBTI'].upper() == user_mbti.upper()), None)
    if not user_result:
        available_mbti = [result['MBTI'] for result in results]
        return f"사용자의 MBTI({user_mbti})에 해당하는 결과를 찾을 수 없습니다. 사용 가능한 MBTI 유형: {', '.join(available_mbti)}"

    logging.info(f"Found user result for MBTI {user_mbti}: {user_result}")

    user_mbti_indices = mbti_detail_df.index[mbti_detail_df['유형'].str.upper() == user_mbti.upper()].tolist()
    
    if not user_mbti_indices:
        return f"사용자의 MBTI({user_mbti})에 해당하는 결과를 찾을 수 없습니다."
    user_mbti_idx = user_mbti_indices[0]
    logging.info(f"Found MBTI index: {user_mbti_idx}")

    user_mbti_emb = mbti_embeddings[user_mbti_idx].reshape(1, -1)
    similarities = cosine_similarity(user_mbti_emb, job_embeddings).flatten()

    logging.info(f"Calculated similarities for {user_mbti}: min={min(similarities)}, max={max(similarities)}, mean={sum(similarities) / len(similarities)}")

    processed_user_job = preprocess_text_soynlp(user_job)

    user_job_idx = job_detail_df.index[job_detail_df['processed_직무'] == processed_user_job].tolist()
    
    if user_job_idx:
        user_job_idx = user_job_idx[0]
        user_job_similarity = similarities[user_job_idx] * 100  # Convert to percentage
    else:
        most_similar_job_idx = np.argmax(similarities)
        user_job_similarity = similarities[most_similar_job_idx] * 100

    top_3_jobs_idx = np.argsort(similarities)[-3:][::-1]
    top_3_jobs = job_detail_df.iloc[top_3_jobs_idx]

    top_3_jobs_list = [row['직무'] for _, row in top_3_jobs.iterrows()]
    top_3_similarities = similarities[top_3_jobs_idx] * 100  # Convert to percentage

    logging.info(f"Top 3 jobs: {top_3_jobs_list}")
    logging.info(f"Top 3 similarities: {top_3_similarities}")

    initial_response = [
        f"사용자님의 MBTI {user_mbti}는 {user_job} 직업과 {user_job_similarity:.2f}% 정도의 유사도를 보여줍니다.",
        f"사용자님의 성향 중 {user_result['Best Match Description']}한 부분들이 이 직업에 도움을 줄 수 있습니다."
    ]

    additional_response = [
        f"사용자님의 {user_mbti} MBTI와 어울리는 상위 3개 직업은 다음과 같습니다:",
        f"1. {top_3_jobs_list[0]} (유사도: {top_3_similarities[0]:.2f}%)",
        f"2. {top_3_jobs_list[1]} (유사도: {top_3_similarities[1]:.2f}%)",
        f"3. {top_3_jobs_list[2]} (유사도: {top_3_similarities[2]:.2f}%)"
    ]

    response = {
        'user_mbti': user_mbti,
        'user_job': user_job,
        'initial_response': initial_response,
        'additional_response': additional_response,
    }

    # Save results to MongoDB
    save_results_to_collection(client, config['mongodb']['db_name'], 'results_collection', response, ttl_seconds)

    return initial_response, additional_response

# MongoDB에 결과 저장 함수
def save_results_to_collection(client: MongoClient, db_name: str, collection_name: str, response: dict, ttl_seconds: int):
    db = client[db_name]
    collection = db[collection_name]
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)
    response['expireAt'] = expire_at
    try:
        collection.insert_one(response)
        logging.info(f"Saved response to MongoDB collection '{collection_name}' in database '{db_name}'")
    except Exception as e:
        logging.error(f"MongoDB 컬렉션 '{collection_name}'에 응답 저장 실패: {e}")
        raise e

# 메인 함수
def main(user_mbti, user_job):
    try:
        config = load_config('./json/config.json')
        mongodb_uri = config['mongodb']['uri']
        client = get_mongodb_client(mongodb_uri)

        logging.info("1. 데이터 로딩 및 전처리 시작")
        mbti_detail_df, holland_result_df, job_detail_df = prepare_data(config, client)

        logging.info("2. 임베딩 로드 및 유사도 계산 시작")

        mbti_embeddings, holland_embeddings, job_embeddings = load_embeddings_from_mongodb(client, config['mongodb']['db_name'], 'embeddings_collection')
        
        # 파인튜닝된 모델 ID 설정
        fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::9qa3DaXk"
        
        results = generate_results(mbti_detail_df, holland_result_df, mbti_embeddings, holland_embeddings, fine_tuned_model)
        logging.info(f"Generated results for MBTI types: {[r['MBTI'] for r in results]}")

        logging.info("3. 사용자 입력 받기")
        user_mbti = user_mbti.upper()

        logging.info("4. 최종 결과 생성 및 MongoDB에 저장")
        ttl_seconds = 3600
        initial_response, additional_response = final_results(user_mbti, user_job, mbti_detail_df, job_detail_df, mbti_embeddings, job_embeddings, results, client, config, ttl_seconds)
        logging.info("결과가 MongoDB에 저장되었습니다.")
        logging.info(initial_response)
        logging.info(additional_response)

        return {
            "line1": initial_response[0] if len(initial_response) > 0 else "",
            "line2": initial_response[1] if len(initial_response) > 1 else "",
            "line3": additional_response[0] if len(additional_response) > 0 else "",
            "line4": additional_response[1] if len(additional_response) > 1 else "",
            "line5": additional_response[2] if len(additional_response) > 2 else "",
            "line6": additional_response[3] if len(additional_response) > 3 else "",
            "line7": additional_response[4] if len(additional_response) > 4 else ""
        }
    except Exception as e:
        logging.error(f"메인 함수 실행 중 오류 발생: {e}")
        raise e

if __name__ == "__main__":
    try:
        # 사용자 입력 받기
        user_mbti = input("사용자의 MBTI를 입력하세요: ")
        user_job = input("사용자의 직업을 입력하세요: ")
        main(user_mbti, user_job)
    except Exception as e:
        logging.error(f"프로그램 실행 중 오류 발생: {e}")
