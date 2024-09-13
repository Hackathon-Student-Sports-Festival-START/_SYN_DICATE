document.addEventListener('DOMContentLoaded', () => {
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        alert('Требуется авторизация');
        window.location.href = '../login/index.html'; // Перенаправление на страницу входа
    } else {
        fetchProfileData(); // Загрузка данных профиля
        fetchEvents(); // Загрузка данных мероприятий
    }
});

function fetchProfileData() {
    const accessToken = localStorage.getItem('accessToken'); // Получаем токен из localStorage

    fetch('http://localhost:8000/profile', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`, // Используем токен для авторизации
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    alert('Сессия истекла. Пожалуйста, войдите снова.');
                    window.location.href = '/login.html'; // Перенаправление на страницу входа
                } else {
                    throw new Error('Ошибка получения данных профиля');
                }
            }
            return response.json();
        })
        .then(data => {
            // Заполняем HTML элементами
            document.getElementById('name-display').innerText = data.name || 'Имя не указано';
            document.getElementById('last-name-display').innerText = data.last_name || 'Фамилия не указана'; // Добавлено для фамилии
            document.getElementById('university-display').innerText = data.university || 'Университет не указан';
            document.getElementById('email-display').innerText = data.email || 'Email не указан';
            document.getElementById('phone-display').innerText = data.phone || 'Телефон не указан';
        })
        .catch(error => {
            console.error('Ошибка при получении данных профиля:', error);
            alert('Не удалось загрузить данные профиля. Пожалуйста, попробуйте снова.');
        });
}
function editProfile() {
    const fields = [
        { id: 'name-display', type: 'text', placeholder: 'Имя' },
        { id: 'last-name-display', type: 'text', placeholder: 'Фамилия' },
        { id: 'university-display', type: 'text', placeholder: 'Университет' },
        { id: 'email-display', type: 'email', placeholder: 'Email' },
        { id: 'phone-display', type: 'tel', placeholder: 'Телефон' }
    ];

    // Превращаем текстовые элементы в поля ввода
    fields.forEach(field => {
        const element = document.getElementById(field.id);
        const currentValue = element.innerText;
        const inputElement = `
            <div class="input-container" id="${field.id}-container">
                <input type="${field.type}" id="${field.id}-input" value="${currentValue}" placeholder="${field.placeholder}">
                <span class="delete-btn" onclick="deleteField('${field.id}-input')">
                    <img src="cross.svg" alt="Delete">
                </span>
            </div>`;
        element.outerHTML = inputElement;
    });

    document.querySelector('.edit-btn').style.display = 'none';
    document.querySelector('.save-btn').style.display = 'inline-block';
}

function saveProfile() {
    const fields = [
        { id: 'name-display', label: '' },
        { id: 'last-name-display', label: '' },
        { id: 'university-display', label: '' },
        { id: 'email-display', label: 'Email' },
        { id: 'phone-display', label: 'Телефон' }
    ];

    const updatedData = {};

    // Собираем данные из полей ввода
    fields.forEach(field => {
        const inputElement = document.getElementById(`${field.id}-input`);
        updatedData[field.id.replace('-display', '')] = inputElement.value;
        const newValue = inputElement.value;
        const paragraphElement = `<p id="${field.id}">${newValue}</p>`;
        document.getElementById(`${field.id}-container`).outerHTML = paragraphElement;
    });

    // Отправляем данные на сервер
    const accessToken = localStorage.getItem('accessToken');
    fetch('http://localhost:8000/profile', {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedData) // Отправляем обновленные данные
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сохранения данных профиля');
            }
            return response.json();
        })
        .then(data => {
            alert('Профиль успешно обновлен');
        })
        .catch(error => {
            console.error('Ошибка при сохранении данных профиля:', error);
            alert('Не удалось сохранить данные профиля. Попробуйте снова.');
        });

    document.querySelector('.edit-btn').style.display = 'inline-block';
    document.querySelector('.save-btn').style.display = 'none';
}


