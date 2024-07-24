document.addEventListener('DOMContentLoaded', function() {
    const hpInput = document.getElementById('hp');
    if (hpInput) {
        hpInput.addEventListener('input', function (event) {
            const value = event.target.value;
            const cleanValue = value.replace(/[^0-9]/g, '');
            let formattedValue = '';
            for (let i = 0; i < cleanValue.length && i < 11; i++) {
                if ((i === 3 || i === 7) && cleanValue.length > i) {
                    formattedValue += '-';
                }
                formattedValue += cleanValue[i];
            }
            event.target.value = formattedValue;
        });
    }

    const passwordReInput = document.getElementById('password_re');
    const message = document.getElementById('message');
    if (passwordReInput) {
        passwordReInput.addEventListener('blur', function () {
            const passwordInput = document.getElementById('password');
            const password = passwordInput.value;
            const passwordRe = passwordReInput.value;
            if (password === passwordRe && password !== '') {
                message.textContent = '비밀번호가 확인되었습니다.';
                message.style.color = 'green';
            } else {
                message.textContent = '비밀번호가 다릅니다.';
                message.style.color = 'red';
            }
        });
    }
});

function sendit() {
    const userid = document.getElementById('userid');
    const condi_ID = /^[A-Za-z0-9]{4,20}$/;
    if (!condi_ID.test(userid.value)) {
        alert('아이디는 4자 이상 20자이하의 영문자로 입력하세요.');
        userid.focus();
        return false;
    }

    const userpw = document.getElementById('password');
    const expPwText = /^(?=.*[A-Za-z])(?=.*[~!@#$%^&*+=-])(?=.*[0-9]).{4,20}$/;
    if (!expPwText.test(userpw.value)) {
        alert('비밀번호는 4자리 이상 20자리 이하의 영문자, 숫자, 특수문자를 1자 이상 포함해야합니다.');
        userpw.focus();
        return false;
    }

    const userpw_re = document.getElementById('password_re');
    if (userpw.value !== userpw_re.value) {
        alert('비밀번호가 다릅니다!');
        userpw_re.focus();
        return false;
    }

    const name = document.getElementById('name');
    const expName = /^[가-힣]+$/;
    if (!expName.test(name.value)) {
        alert('한글을 입력해주세요.');
        name.focus();
        return false;
    }

    const hp = document.getElementById('hp');
    const expHp = /^\d{3}-\d{3,4}-\d{4}$/;
    if (!expHp.test(hp.value)) {
        alert('정수 3자리-(정수 3자리 or 4자리)-정수 4자리');
        hp.focus();
        return false;
    }

    const email = document.getElementById('email');
    const expEmail = /^[A-Za-z0-9\-_]+@[A-Za-z0-9]+\.[A-Za-z\.]+$/;
    if (!expEmail.test(email.value)) {
        alert('이메일을 다시 입력해주세요.');
        email.focus();
        return false;
    }

    const agreeTerms = document.getElementById('agree-terms');
    const agreePrivacy = document.getElementById('agree-privacy');

    if (!agreeTerms.checked) {
        alert('서비스 이용약관에 동의하셔야 합니다.');
        agreeTerms.focus();
        return false;
    }

    if (!agreePrivacy.checked) {
        alert('개인정보 수집 및 이용에 동의하셔야 합니다.');
        agreePrivacy.focus();
        return false;
    }

    return true;
}

function registerUser(event) {
    event.preventDefault();

    if (!sendit()) {
        const registerMessage = document.getElementById('register-message');
        registerMessage.textContent = '입력 정보를 다시 확인해주세요.';
        return;
    }

    const user = {
        userid: document.getElementById('userid').value,
        password: document.getElementById('password').value,
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        hp: document.getElementById('hp').value
    };

    fetch('/api/users/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => { throw new Error(data.detail); });
        }
        return response.json();
    })
    .then(data => {
        const registerMessage = document.getElementById('register-message');
        if (data.detail === "Email already registered") {
            document.getElementById("error-message").textContent = data.detail;
        } else {
            alert("회원가입이 성공적으로 완료되었습니다.");
            location.href = '/'; // 회원가입이 성공하면 로그인 페이지로 이동
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const registerMessage = document.getElementById('register-message');
        registerMessage.textContent = '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.';
    });
}

document.getElementById('register-form').addEventListener('submit', registerUser);