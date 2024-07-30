// 전화번호에 자동으로 000-0000-0000

document.getElementById('idSearchForm').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const name = document.getElementById('name').value;
    const password = document.getElementById('password').value;
    const hp = document.getElementById('hp').value;
    const data = { name, password, hp };

    fetch('/search_userid', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('당신의 아이디는: ' + result.userid);
        } else {
            alert('일치하는 정보가 없습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('서버와의 통신 중 오류가 발생했습니다.');
    });
});

function goBack() {
    window.history.back();
}    