document.addEventListener("DOMContentLoaded", function() {
    async function fetchUserInfo() {
        const cookieString = document.cookie.split('; ').find(row => row.startsWith('token='));
        if (!cookieString) {
            console.error('No token found');
            return;
        }
        const token = cookieString.split('=')[1];
        const userInfoEndpoint = '/api/users/me';
        
        try {
            const response = await fetch(userInfoEndpoint, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }

            const data = await response.json();
            document.getElementById('name').textContent = data.name;
            document.getElementById('hp').textContent = data.hp;
            document.getElementById('userid').textContent = data.userid;
            document.getElementById('email').textContent = data.email;
        } catch (error) {
            console.error('Error:', error);
        }
    }
    fetchUserInfo();  
});



document.getElementById('delete-user-btn').addEventListener('click', async function () {
    const deleteMessage = document.getElementById('delete-message');
    const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];
    
    console.log('회원 탈퇴 버튼 클릭됨');
    console.log('토큰:', token);

    try {
        const response = await fetch('/delete_user', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('응답 상태 코드:', response.status);

        if (response.ok) {
            const result = await response.json();
            deleteMessage.textContent = result.message;
            deleteMessage.style.color = "green";
            console.log('회원 탈퇴 성공:', result.message);
            alert('회원 탈퇴가 완료되었습니다.');
            window.location.href = '/';  // 로그인 페이지로 리다이렉트
        } else {
            const errorResult = await response.json();
            deleteMessage.textContent = errorResult.detail;
            deleteMessage.style.color = "red";
            console.log('회원 탈퇴 실패:', errorResult.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        deleteMessage.textContent = '회원 탈퇴 중 오류가 발생했습니다.';
        deleteMessage.style.color = "red";
    }
});

document.getElementById('logout-button').addEventListener('click', function() {    
    document.cookie = 'token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    window.location.href = '/';
});

document.getElementById('main').addEventListener('click', function() {
    window.location.href = '/main'; 
});

document.getElementById('job_info').addEventListener('click', function() {
    window.location.href = '/job_info'; 
});

document.getElementById('info_edit').addEventListener('click', function() {
    window.location.href = '/info_edit';
});
