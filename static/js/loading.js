setTimeout(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const mbti = urlParams.get('mbti');
    const jobCategory = urlParams.get('jobCategory');
    window.location.href = `/result?mbti=${mbti}&jobCategory=${jobCategory}`;
}, 5000);