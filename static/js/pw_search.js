document.getElementById('pwSearchForm').addEventListener('submit', function(event) {
    event.preventDefault(); 

    
    const userid = document.getElementById('userid').value;
    const name = document.getElementById('name').value;
    const hp = document.getElementById('hp').value;

    
    const data = { userid, name, hp };

    
    fetch('/search_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('당신의 비밀번호는: ' + result.password);
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