// // 로딩창에서 결과창이 뜰때 애니메이션

// 결과더보기 창 확대
document.addEventListener("DOMContentLoaded", async function() {
    console.log('result.js loaded');
    console.log('Window loaded');

    const urlParams = new URLSearchParams(window.location.search);
    const mbti = urlParams.get('mbti');
    const jobcategory = urlParams.get('jobcategory');

    try {
        console.log(`Fetching result for MBTI: ${mbti}, Job Category: ${jobcategory}`);
        const response = await fetch(`http://localhost:8000/api/result?mbti=${encodeURIComponent(mbti)}&jobcategory=${encodeURIComponent(jobcategory)}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Fetch successful:', data);

        document.getElementById('line1').textContent = data.line1;
        document.getElementById('line2').textContent = data.line2;
        document.getElementById('line3').textContent = data.line3;
        document.getElementById('line4').textContent = data.line4;
        document.getElementById('line5').textContent = data.line5;
        document.getElementById('line6').textContent = data.line6;
    } catch (error) {
        console.error('Error fetching result:', error);
    }
});
// 결과더보기 창 확대
const toggleVisibility = () => {
    const sentence = document.getElementById('sentence');
    const ulim = document.getElementById('ulim');
    const Top3 = document.getElementById('Top3');
    const resultBox = document.getElementById('result-box');
    const plusButton = document.getElementById('plus');

    if (sentence.classList.contains('hidden')) {
        sentence.classList.remove('hidden');
        ulim.classList.remove('hidden');
        Top3.classList.remove('hidden');
        resultBox.style.height = 'auto';
        resultBox.scrollTop = resultBox.scrollHeight; // Ensure the box scrolls to show the new content
        plusButton.textContent = '닫기';
    } else {
        sentence.classList.add('hidden');
        ulim.classList.add('hidden');
        Top3.classList.add('hidden');
        resultBox.style.height = '210px';
        plusButton.textContent = '결과 더보기';
    }
};

document.getElementById('plus').addEventListener('click', toggleVisibility);