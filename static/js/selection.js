function goBack() {
    window.history.back();
}

function toggleMbtiDropdown() {
    const mbtiList = document.getElementById('mbti-list');
    mbtiList.style.display = mbtiList.style.display === 'block' ? 'none' : 'block';
}


// mbti 이미지
function selectMbti(element) {
    const mbtiButton = document.querySelector('.mbti-dropdown .dropdown-button');
    mbtiButton.textContent = element.textContent + ' ';
    const triangle = document.createElement('span');
    triangle.className = 'triangle';
    triangle.innerHTML = '&#9660;';
    mbtiButton.appendChild(triangle);
    document.getElementById('mbti-list').style.display = 'none';
    
    // 이미지 로드
    const mbtiImage = document.getElementById('mbti-image');
    mbtiImage.src = `/static/icon/character/${element.textContent}.png`;
    mbtiImage.style.display = 'block';
}


function toggleJobCategory() {
    const jobCategoryList = document.getElementById('job-category-list');
    const mbtiList = document.getElementById('mbti-list');

    // 다른 카테고리를 닫음
    mbtiList.style.display = 'none';

    // 현재 카테고리를 토글
    jobCategoryList.style.display = jobCategoryList.style.display === 'block' ? 'none' : 'block';
}

const jobCategoryImages = {
    "경영·행정·사무직": "manage",
    "금융·보험직": "finance",
    "인문·사회과학 연구직": "research",
    "자연·생명과학 연구직": "research2",
    "정보통신 연구개발직 및 공학기술직": "developer",
    "건설·채굴 연구개발직 및 공학기술직": "construction",
    "제조 연구개발직 및 공학기술직": "manufacturing",
    "사회복지·종교직": "teacher",
    "교육직": "teacher",
    "법률직": "lawyer",
    "경찰·소방·교도직": "firefighter",
    "군인": "soldier",
    "보건·의료직": "doctor",
    "예술·디자인·방송직": "_broadcasting",
    "스포츠·레크리에이션직": "_broadcasting",
    "경호·경비직": "bodygard",
    "돌봄 서비스직(간병·육아)": "cleaning-1",
    "청소 및 기타 개인서비스직": "cleaning-1",
    "미용·예식 서비스직": "musician",
    "여행·숙박·오락 서비스직": "musician",
    "영업·판매직": "transfort",
    "운전·운송직": "transfort",
    "건설·채굴직": "construction",
    "식품 가공·생산직": "_blue_collar",
    "인쇄·목재·공예 및 기타 설치·정비·생산직": "_blue_collar",
    "제조 단순직": "_blue_collar",
    "기계 설치·정비·생산직": "_blue_collar",
    "금속·재료 설치·정비·생산직(판금·단조·주조·용접·도장 등)": "sculptor",
    "전기·전자 설치·정비·생산직": "manufacturing2",
    "정보통신 설치·정비직": "manufacturing",
    "화학·환경 설치·정비·생산직": "clothing",
    "섬유·의복 생산직": "clothing",
    "농림어업직": "farmer"
};

// JobCategory 카테고리
function selectJobCategory(element) {
    const jobCategoryButton = document.querySelector('.job-category-dropdown .dropdown-button');
    jobCategoryButton.textContent = element.textContent + ' ';
    const triangle = document.createElement('span');
    triangle.className = 'triangle';
    triangle.innerHTML = '&#9660;';
    jobCategoryButton.appendChild(triangle);
    document.getElementById('job-category-list').style.display = 'none';    

    const jobImage = document.getElementById('job-image');
    const selectedCategory = element.textContent;
    if (jobCategoryImages[selectedCategory]) {
        jobImage.src = `/static/icon/job_character/${jobCategoryImages[selectedCategory]}.png`;
        jobImage.style.display = 'block';
    } else {
        jobImage.style.display = 'none';
    }
}

// mbti-job_name 선택 결과 보내기
function Mbti(element) {
    document.getElementById('mbti-list').value = element.innerText;
}

function JobCategory(element) {
    document.getElementById('job-category-list').value = element.innerText;
}

// 결과보기 버튼 클릭
document.getElementById('result-button').addEventListener('click', function() {
    const mbtiButton = document.querySelector('.mbti-dropdown .dropdown-button');
    const jobCategoryButton = document.querySelector('.job-category-dropdown .dropdown-button');

    const mbti = mbtiButton.textContent.trim().split(' ')[0];
    const jobcategory = jobCategoryButton.textContent.trim().split(' ')[0];

    if (mbti === 'MBTI' || jobcategory === '%EC%A7%81%EA%B5%B0') {
        alert('카테고리를 선택하세요');
        return;
    }
    
    window.location.href = `/loading?mbti=${mbti}&jobCategory=${jobcategory}`;
});
