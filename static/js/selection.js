function toggleMbtiDropdown() {
    const mbtiList = document.getElementById('mbti-list');
    mbtiList.style.display = mbtiList.style.display === 'block' ? 'none' : 'block';
}

function selectMbti(element) {
    const mbtiButton = document.querySelector('.mbti-dropdown .dropdown-button');
    mbtiButton.textContent = element.textContent + ' ';
    const triangle = document.createElement('span');
    triangle.className = 'triangle';
    triangle.innerHTML = '&#9660;';
    mbtiButton.appendChild(triangle);
    document.getElementById('mbti-list').style.display = 'none';
}

function toggleJobCategory() {
    const jobCategoryList = document.getElementById('job-category-list');
    jobCategoryList.style.display = jobCategoryList.style.display === 'block' ? 'none' : 'block';
}

function selectJobCategory(element) {
    const jobCategoryButton = document.querySelector('.job-category-dropdown .dropdown-button');
    jobCategoryButton.textContent = element.textContent + ' ';
    const triangle = document.createElement('span');
    triangle.className = 'triangle';
    triangle.innerHTML = '&#9660;';
    jobCategoryButton.appendChild(triangle);
    document.getElementById('job-category-list').style.display = 'none';
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
    const mbti = document.querySelector('.mbti-dropdown .dropdown-button').textContent.trim().split(' ')[0];
    const jobCategory = document.querySelector('.job-category-dropdown .dropdown-button').textContent.trim().split(' ')[0];
    window.location.href = `/loading?mbti=${mbti}&jobCategory=${jobCategory}`;
});