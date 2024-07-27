import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import re
import json
import torch
from transformers import AutoTokenizer, AutoModel
from soynlp.normalizer import *
from soynlp.tokenizer import LTokenizer
from soynlp.word import WordExtractor
import unicodedata
import logging
from typing import List, Dict, Any, Tuple
from pymongo import MongoClient
import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 몽고 연결 설정
def get_mongodb_client(uri: str):
    return MongoClient(uri)

# MongoDB에서 데이터 로드 함수
def load_data_from_mongodb(client: MongoClient, db_name: str, collection_name: str):
    db = client[db_name]
    collection = db[collection_name]
    data = list(collection.find())
    return pd.DataFrame(data)

# 설정 파일 로드
def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return json.load(f)

# 한국어 불용어 목록 정의
korean_stopwords = set("""
이 그 저 것 수 등 더 의 에 를 에서 그리고 그러나 그래서 그러므로 그렇지만 그러나
""".split())

# 텍스트 전처리
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKC', text)
    text = emoticon_normalize(text, num_repeats=2)
    text = repeat_normalize(text, num_repeats=2)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\d+', lambda m: num_to_kor(int(m.group())), text)
    words = text.split()
    text = ' '.join([word for word in words if word not in korean_stopwords])
    text = ' '.join(text.split())
    return text

def num_to_kor(num):
    units = [''] + list('십백천')
    nums = '일이삼사오육칠팔구'
    result = ''
    i = 0
    while num > 0:
        n = num % 10
        if n:
            result = nums[n-1] + units[i] + result
        i += 1
        num //= 10
    return result if result else '영'

# soynlp를 이용한 토큰화
def tokenize_text(text, tokenizer):
    return ' '.join(tokenizer.tokenize(text))

# BERT 모델을 위한 임베딩 생성 함수
def create_bert_embedding(texts, model, tokenizer):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()  # CLS 토큰의 임베딩만 사용

def prepare_data(config, client):
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
    # MBTI와 Holland Code 매핑 병합
    mbti_detail_df = mbti_detail_df.merge(mbti_holland_df, how='left', left_on='유형', right_on='MBTI 명칭')
    # 전처리 적용
    mbti_detail_df['processed_특징'] = mbti_detail_df['특징'].apply(preprocess_text)
    holland_result_df['processed_상세설명'] = holland_result_df['상세 설명'].apply(preprocess_text)
    job_detail_df['processed_직업 설명'] = job_detail_df['직업 설명'].apply(preprocess_text)
    # 전처리 결과 샘플 출력
    print("전처리된 MBTI 데이터 샘플:")
    print(mbti_detail_df[['유형', 'processed_특징']].sample(5))
    print("\n전처리된 Holland 데이터 샘플:")
    print(holland_result_df[['검사 코드 조합', 'processed_상세설명']].sample(5))
    print("\n전처리된 직업 데이터 샘플:")
    print(job_detail_df[['직무', 'processed_직업 설명']].sample(5))
    # soynlp 워드 익스트랙터 학습
    text_for_training = mbti_detail_df['processed_특징'].tolist() + holland_result_df['processed_상세설명'].tolist()
    word_extractor = WordExtractor()
    word_extractor.train(text_for_training)
    words = word_extractor.extract()
    # LTokenizer 초기화
    scores = {word: score.cohesion_forward for word, score in words.items()}
    tokenizer = LTokenizer(scores=scores)
    # 토큰화 적용
    mbti_detail_df['tokenized_특징'] = mbti_detail_df['processed_특징'].apply(lambda x: tokenize_text(x, tokenizer))
    holland_result_df['tokenized_상세설명'] = holland_result_df['processed_상세설명'].apply(lambda x: tokenize_text(x, tokenizer))
    job_detail_df['tokenized_직업 설명'] = job_detail_df['processed_직업 설명'].apply(lambda x: tokenize_text(x, tokenizer))
    # 토큰화 결과 샘플 출력
    print("토큰화된 MBTI 데이터 샘플:")
    print(mbti_detail_df[['유형', 'tokenized_특징']].sample(5))
    print("\n토큰화된 Holland 데이터 샘플:")
    print(holland_result_df[['검사 코드 조합', 'tokenized_상세설명']].sample(5))
    print("\n토큰화된 직업 데이터 샘플:")
    print(job_detail_df[['직무', 'tokenized_직업 설명']].sample(5))
    return mbti_detail_df, holland_result_df, job_detail_df

# 모델 정의 및 로딩
models = {
    'snunlp/KR-SBERT-V40K-klueNLI-augSTS': SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS'),
    'jhgan/ko-sroberta-multitask': SentenceTransformer('jhgan/ko-sroberta-multitask'),
    'klue/bert-base': AutoModel.from_pretrained('klue/bert-base'),
}
tokenizers = {
    'klue/bert-base': AutoTokenizer.from_pretrained('klue/bert-base'),
}

# 유사도 계산 함수 (코사인 유사도)
def calculate_similarity(emb1, emb2):
    return cosine_similarity(emb1, emb2)

# 결과 생성 및 출력 함수
mbti_embeddings = {}  # 전역 변수로 선언

# 임베딩 생성 및 유사도 계산 함수
def generate_results(mbti_detail_df, holland_result_df):
    global mbti_embeddings
    holland_embeddings = {}
    for model_name, model in models.items():
        if isinstance(model, SentenceTransformer):
            mbti_embeddings[model_name] = model.encode(mbti_detail_df['tokenized_특징'].tolist())
            holland_embeddings[model_name] = model.encode(holland_result_df['tokenized_상세설명'].tolist())
        else:  # BERT 모델의 경우
            tokenizer = tokenizers[model_name]
            mbti_embeddings[model_name] = create_bert_embedding(mbti_detail_df['tokenized_특징'].tolist(), model, tokenizer)
            holland_embeddings[model_name] = create_bert_embedding(holland_result_df['tokenized_상세설명'].tolist(), model, tokenizer)
        # 임베딩 생성 결과 출력
        print(f"Model {model_name} MBTI 임베딩 벡터 크기: {mbti_embeddings[model_name].shape}")
        print(f"Model {model_name} Holland 임베딩 벡터 크기: {holland_embeddings[model_name].shape}")
    results = []
    for mbti_idx, mbti_row in mbti_detail_df.iterrows():
        best_match = None
        best_score = 0
        best_model = None
        for model_name in models.keys():
            mbti_emb = mbti_embeddings[model_name][mbti_idx].reshape(1, -1)
            holland_embs = holland_embeddings[model_name]
            similarities = calculate_similarity(mbti_emb, holland_embs).flatten()
            max_sim_idx = np.argmax(similarities)
            max_sim = similarities[max_sim_idx]
            if max_sim > best_score:
                best_score = max_sim
                best_match = holland_result_df.iloc[max_sim_idx]
                best_model = model_name
        result = {
            'MBTI': mbti_row['유형'],
            'Best Match Holland Code': best_match['검사 코드 조합'],
            'Best Match Description': best_match['상세 설명'],
            'Best Model': best_model,
            'Similarity Score': best_score
        }
        results.append(result)
        logging.info(f"Generated result for MBTI {result['MBTI']}: {result}")
    logging.info(f"Total results generated: {len(results)}")
    return results

# MongoDB에 결과 저장 함수
def save_results_to_collection(client: MongoClient, db_name: str, collection_name: str, response: Dict[str, Any], ttl_seconds: int):
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

# 최종 결과 생성 함수
def final_results(user_mbti, user_job, mbti_detail_df, holland_result_df, job_detail_df, results, client, config, ttl_seconds):
    logging.debug(f"최종 결과 생성 중, 사용자 MBTI: {user_mbti}, 사용자 직업: {user_job}")
    job_embeddings = {}
    for model_name, model in models.items():
        if isinstance(model, SentenceTransformer):
            job_embeddings[model_name] = model.encode(job_detail_df['tokenized_직업 설명'].tolist())
        else:
            tokenizer = tokenizers[model_name]
            job_embeddings[model_name] = create_bert_embedding(job_detail_df['tokenized_직업 설명'].tolist(), model, tokenizer)

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

    user_mbti_emb = mbti_embeddings[user_result['Best Model']][user_mbti_idx].reshape(1, -1)
    job_embs = job_embeddings[user_result['Best Model']]
    similarities = calculate_similarity(user_mbti_emb, job_embs).flatten()

    logging.info(f"User MBTI: {user_mbti}")
    logging.info(f"User MBTI index: {user_mbti_idx}")
    logging.info(f"User MBTI embedding shape: {user_mbti_emb.shape}")
    logging.info(f"Job embeddings shape: {job_embs.shape}")
    logging.info(f"Similarities shape: {similarities.shape}")

    logging.info(f"Calculated similarities for {user_mbti}: min={similarities.min()}, max={similarities.max()}, mean={similarities.mean()}")

    user_job_idx = job_detail_df.index[job_detail_df['직무'] == user_job].tolist()
    if user_job_idx:
        user_job_idx = user_job_idx[0]
        user_job_similarity = similarities[user_job_idx] * 100  # Convert to percentage
    else:
        user_job_similarity = 0

    top_3_jobs_idx = np.argsort(similarities)[-3:][::-1]
    top_3_jobs = job_detail_df.iloc[top_3_jobs_idx]

    top_3_jobs_list = [row['직무'] for _, row in top_3_jobs.iterrows()]
    top_3_similarities = similarities[top_3_jobs_idx] * 100  # Convert to percentage

    logging.info(f"Top 3 jobs indices: {top_3_jobs_idx}")
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
        f"3. {top_3_jobs_list[2]} (유사도: {top_3_similarities[2]:.2f}%)",
        f"사용된 모델: {user_result['Best Model']}"
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


# 메인 함수 수정
def main(user_mbti, user_job):
    config = load_config('json/config.json')
    mongodb_uri = config['mongodb']['uri']
    client = get_mongodb_client(mongodb_uri)

    logging.info("1. 데이터 로딩 및 전처리 시작")
    mbti_detail_df, holland_result_df, job_detail_df = prepare_data(config, client)  # 네 개의 반환값 받기

    logging.info("2. 임베딩 생성 및 유사도 계산 시작")
    results = generate_results(mbti_detail_df, holland_result_df)  # 생성된 임베딩을 전달
    logging.info(f"Generated results for MBTI types: {[r['MBTI'] for r in results]}")

    logging.info("3. 사용자 입력 받기")
    user_mbti = user_mbti.upper()

    logging.info("4. 최종 결과 생성 및 MongoDB에 저장")
    ttl_seconds = 3600
    initial_response, additional_response = final_results(user_mbti, user_job, mbti_detail_df, holland_result_df, job_detail_df, results, client, config, ttl_seconds)
    logging.info("결과가 MongoDB에 저장되었습니다.")
    logging.info(initial_response)
    logging.info(additional_response)

    # return initial_response, additional_response

    return {
        "line1": initial_response[0] if len(initial_response) > 0 else "",
        "line2": initial_response[1] if len(initial_response) > 1 else "",
        "line3": additional_response[0] if len(additional_response) > 0 else "",
        "line4": additional_response[1] if len(additional_response) > 1 else "",
        "line5": additional_response[2] if len(additional_response) > 2 else "",
        "line6": additional_response[3] if len(additional_response) > 3 else "",
        "line7": additional_response[4] if len(additional_response) > 4 else ""
    }

if __name__ == "__main__":
    # 사용자 입력 받기
    user_mbti = input("사용자의 MBTI를 입력하세요: ")
    user_job = input("사용자의 직업을 입력하세요: ")
    main(user_mbti, user_job)