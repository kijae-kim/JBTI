document.getElementById('delete-user-btn').addEventListener('click', async function () {
    const deleteMessage = document.getElementById('delete-message');
    const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];

    try {
        const response = await fetch('http://localhost:8000/delete_user', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            deleteMessage.textContent = result.message;
            deleteMessage.style.color = "green";
        } else {
            const errorResult = await response.json();
            deleteMessage.textContent = errorResult.detail;
            deleteMessage.style.color = "red";
        }
    } catch (error) {
        console.error('Error:', error);
        deleteMessage.textContent = '회원 탈퇴 중 오류가 발생했습니다.';
        deleteMessage.style.color = "red";
    }
});