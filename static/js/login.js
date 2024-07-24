document.addEventListener("DOMContentLoaded", function() {
    async function loginUser(event) {
        event.preventDefault();

        const userid = document.getElementById('userid').value;
        const password = document.getElementById('password').value;
        const loginError = document.getElementById('login-message');

        if (!userid || !password) {
            loginError.textContent = '아이디와 비밀번호를 모두 입력하세요.';
            loginError.style.color = "red";
            return;
        }

        try {
            const response = await fetch('/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `username=${encodeURIComponent(userid)}&password=${encodeURIComponent(password)}`
            });

            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }

            const data = await response.json();
            if (data.access_token) {
                // 로그인 성공 시 토큰 저장 및 페이지 이동
                document.cookie = `token=${data.access_token}; path=/`;
                loginError.textContent = '로그인에 성공했습니다.';
                loginError.style.color = "green";
                setTimeout(() => {
                    window.location.href = '/main';
                }, 1000); // 1초 후 페이지 이동
            } else {
                loginError.textContent = '아이디와 비밀번호를 다시 확인해주세요.';
                loginError.style.color = "red";
                throw new Error('Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
            loginError.textContent = '아이디와 비밀번호를 다시 확인해주세요.';
            loginError.style.color = "red";
        }
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', loginUser);
    } else {
        console.error("Element with id 'loginForm' not found.");
    }
});
