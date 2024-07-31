// // 서버로부터 직무 데이터를 가져오는 함수
async function fetchJobs() {
    const response = await fetch('/api/job-fields'); // API 요청을 통해 직무 데이터를 가져옴
    const data = await response.json(); // 응답 데이터를 JSON 형식으로 변환
    console.log('Fetched Jobs:', data); // 가져온 데이터를 콘솔에 출력
    return data; // 데이터를 반환
}

// 서버로부터 직업 설명 데이터를 가져오는 함수
async function fetchJobDetails() {
    const response = await fetch('/api/job-details'); // API 요청을 통해 직업 설명 데이터를 가져옴
    const data = await response.json(); // 응답 데이터를 JSON 형식으로 변환
    console.log('Fetched Job Details:', data); // 가져온 데이터를 콘솔에 출력
    return data; // 데이터를 반환
}

function goBack() {
    window.history.back();
}


// DOMContentLoaded 이벤트가 발생했을 때 실행될 함수
document.addEventListener('DOMContentLoaded', async () => {
    const jobSelect = document.getElementById('job-select'); // 'job-select' 요소를 선택
    const jobTypeSelect = document.getElementById('job-type-select'); // 'job-type-select' 요소를 선택
    const selectedJobElement = document.getElementById('selected-job'); // 'selected-job' 요소를 선택
    const jobDescriptionTextarea = document.getElementById('job-description'); // 'job-description' 요소를 선택
    const jobduties = document.getElementById('job-duties')
    const jobskills = document.getElementById('job-skills')
    const joboutlook = document.getElementById('job-outlook')

    const jobs = await fetchJobs(); // 직무 데이터를 가져옴 
    const jobDetails = await fetchJobDetails(); // 직업 설명 데이터를 가져옴

    // Add this function to handle auto-expanding textareas
    function autoExpandTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    // Add event listeners to automatically expand textareas when their content changes
    const textareas = document.querySelectorAll('.info-group textarea');
    textareas.forEach(textarea => {
        textarea.classList.add('auto-expand');
        textarea.addEventListener('input', () => autoExpandTextarea(textarea));
    });

    // Adjust textarea height on content load
    function adjustTextareas() {
        textareas.forEach(textarea => {
            autoExpandTextarea(textarea);
        });
    }
    
    // Fetch data and adjust textareas afterwards
    adjustTextareas();    

    // 직무 데이터를 Set으로 변환하여 중복 제거
    const uniqueJobs = [...new Set(jobs.map(job => job.직무.trim()))]; // 직무 데이터에서 중복을 제거하여 고유한 직무 목록 생성
    uniqueJobs.forEach(job => {
        const option = document.createElement('option'); // 새로운 <option> 요소 생성
        option.value = job; // <option> 요소의 값 설정
        option.textContent = job; // <option> 요소의 텍스트 설정
        jobSelect.appendChild(option); // 'job-select' 요소에 <option> 요소 추가
    });

    // 'job-select' 요소의 값이 변경되었을 때 실행될 함수
    jobSelect.addEventListener('change', async (event) => {
        const selectedJob = event.target.value; // 선택된 직무 값 가져오기
        if (selectedJob === "직무") {
            jobTypeSelect.innerHTML = '<option value="직종" selected> 직종 선택 </option>'; // 직무가 선택되지 않은 경우 기본 옵션 설정
            return; // 함수 종료
        }

        // 선택된 직무에 해당하는 직종 필터링
        const jobDetails = jobs.filter(job => job.직무.trim() === selectedJob.trim());

        // 직종 선택을 비우고 새로운 옵션 추가
        jobTypeSelect.innerHTML = '<option value="직종" selected> 직종 선택 </option>'; // 'job-type-select' 요소를 초기화
        const uniqueJobTypes = [...new Set(jobDetails.map(detail => detail.직종.trim()))]; // 직종 데이터에서 중복을 제거하여 고유한 직종 목록 생성
        uniqueJobTypes.forEach(jobType => {
            const option = document.createElement('option'); // 새로운 <option> 요소 생성
            option.value = jobType; // <option> 요소의 값 설정
            option.textContent = jobType; // <option> 요소의 텍스트 설정
            jobTypeSelect.appendChild(option); // 'job-type-select' 요소에 <option> 요소 추가
        });
    });

    // 'job-type-select' 요소의 값이 변경되었을 때 실행될 함수
    jobTypeSelect.addEventListener('change', (event) => {
        const selectedJobType = event.target.value; // 선택된 직종 값 가져오기
        selectedJobElement.textContent = selectedJobType; // 선택된 직종 값을 'selected-job' 요소에 입력
        
        // 선택된 직종에 해당하는 직업 설명 찾기
        const selectedJobDetail = jobDetails.find(detail => detail.직종.trim().toLowerCase() === selectedJobType.toLowerCase());
        if (selectedJobDetail) {
            jobDescriptionTextarea.value = selectedJobDetail["직업 설명"]; 
        } else {
            jobDescriptionTextarea.value = ''; // 선택된 직종에 해당하는 직업 설명이 없으면 빈 값으로 설정
        }

        // 선택된 직종에 해당하는 수행 직무 찾기
        const selectedduties = jobDetails.find(detail => detail.직종.trim().toLowerCase() === selectedJobType.toLowerCase());
        if (selectedduties) {
            jobduties.value = selectedduties["수행 직무"]; 
        } else {
            jobduties.value = ''; // 선택된 직종에 해당하는 직업 설명이 없으면 빈 값으로 설정
        }

        // 선택된 직종에 해당하는 필요기술 및 지식 찾기
        const selectedskills = jobDetails.find(detail => detail.직종.trim().toLowerCase() === selectedJobType.toLowerCase());
        if (selectedskills) {
            jobskills.value = selectedskills["필요기술 및 지식"]; 
        } else {
            jobskills.value = ''; // 선택된 직종에 해당하는 직업 설명이 없으면 빈 값으로 설정
        }

        // 선택된 직종에 해당하는 필요기술 및 지식 찾기
        const selectedoutlook = jobDetails.find(detail => detail.직종.trim().toLowerCase() === selectedJobType.toLowerCase());
        if (selectedoutlook) {
            joboutlook.value = selectedoutlook["직업 전망"]; 
        } else {
            joboutlook.value = ''; // 선택된 직종에 해당하는 직업 설명이 없으면 빈 값으로 설정
        }        

        adjustTextareas(); 
    });
});
