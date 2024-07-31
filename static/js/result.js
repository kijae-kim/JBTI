// // 로딩창에서 결과창이 뜰때 애니메이션

// 결과더보기 창 확대
document.addEventListener("DOMContentLoaded", async function() {

    const urlParams = new URLSearchParams(window.location.search);
    const mbti = urlParams.get('mbti');
    const jobcategory = urlParams.get('jobCategory');

    const response = await fetch(`https://port-0-jbti-lytt5wni284bca4f.sel4.cloudtype.app/api/result?mbti=${encodeURIComponent(mbti)}&jobcategory=${encodeURIComponent(jobcategory)}`);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();

    document.getElementById('line1').textContent = data.line1;
    document.getElementById('line2').textContent = data.line2;
    document.getElementById('line4').textContent = data.line4;
    document.getElementById('line5').textContent = data.line5;
    document.getElementById('line6').textContent = data.line6;
});

// 결과더보기 창 확대
const toggleVisibility = () => {
    const sentence = document.getElementById('sentence');
    const Top3 = document.getElementById('Top3');
    const resultBox = document.getElementById('result-box');
    const plusButton = document.getElementById('plus');

    if (sentence.classList.contains('hidden')) {
        sentence.classList.remove('hidden');
        Top3.classList.remove('hidden');
        resultBox.classList.add('scrollable');
        plusButton.textContent = '닫기';
    } else {
        sentence.classList.add('hidden');
        Top3.classList.add('hidden');
        resultBox.classList.remove('scrollable');
        plusButton.textContent = '결과 더보기';
    }
};

document.getElementById('plus').addEventListener('click', toggleVisibility);
