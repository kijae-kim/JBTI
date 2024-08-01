// // 로딩창에서 결과창이 뜰때 애니메이션

// 결과더보기 창 확대
document.addEventListener("DOMContentLoaded", async function() {

    const urlParams = new URLSearchParams(window.location.search);
    const mbti = urlParams.get('mbti');
    const jobcategory = urlParams.get('jobCategory');

    const response = await fetch(`/api/result?mbti=${encodeURIComponent(mbti)}&jobcategory=${encodeURIComponent(jobcategory)}`);
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

// 다운로드
document.getElementById('download').addEventListener('click', function() {
    // Select the part of the .result-box excluding the .box section
    const resultBox = document.querySelector('.result-box');
    const box = document.querySelector('.box');
    
    // Temporarily hide the .box section
    box.style.display = 'none';

    // Temporarily set height to auto to capture the full content
    resultBox.style.height = 'auto';
    resultBox.style.overflow = 'visible';

    html2canvas(resultBox, { useCORS: true }).then(canvas => {
        // Restore the display of .box section and revert styles
        box.style.display = 'flex';
        resultBox.style.height = '';
        resultBox.style.overflow = '';

        // Create an image from the canvas
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        link.download = 'result.png';
        link.click();
    });
});


document.getElementById('home').addEventListener('click', function() {
    window.location.href = '/main';
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
