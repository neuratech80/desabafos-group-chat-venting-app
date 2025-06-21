document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO connection
    const socket = io();
    let currentUser = null;

    // Generate anonymous user on connection
    socket.on('connect', function() {
        socket.emit('register_user', { anonymous: true });
    });

    // Handle user registration response
    socket.on('user_registered', function(data) {
        currentUser = data;
        // Update all username inputs with the formatted username
        document.querySelectorAll('input[name="username"]').forEach(input => {
            input.value = data.username;
            input.type = 'hidden';
        });
        
        // Show user ID in the header
        const userIdElement = document.getElementById('user-id');
        if (userIdElement) {
            userIdElement.textContent = data.username;
        }
    });

    // Handle new post event
    socket.on('new_post', function(post) {
        const postsContainer = document.querySelector('.space-y-6');
        if (postsContainer) {
            const postElement = createPostElement(post);
            postsContainer.insertBefore(postElement, postsContainer.firstChild);
        }
    });

    function createPostElement(post) {
        const div = document.createElement('div');
        div.className = 'bg-white rounded-lg shadow p-6';
        div.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-medium text-gray-900">${post.username}</h3>
                <span class="text-sm text-gray-500">${post.created_at}</span>
            </div>
            ${post.content ? `<p class="text-gray-700 mb-4">${post.content}</p>` : ''}
            ${post.image_path ? `<img src="${post.image_path}" alt="Imagem do post" class="rounded-lg max-h-96 w-full object-cover mb-4">` : ''}
            <div class="flex items-center space-x-4 border-t pt-4">
                <button class="like-btn flex items-center text-sm text-gray-500 hover:text-gray-700" data-post-id="${post.id}">
                    <span class="like-count mr-1">0</span> Curtidas
                </button>
                <button class="comment-btn text-sm text-gray-500 hover:text-gray-700" data-post-id="${post.id}">
                    <span class="comment-count mr-1">0</span> Comentários
                </button>
            </div>
            <div class="comment-section mt-4" id="comments-${post.id}" style="display: none;">
                <div class="existing-comments space-y-2" id="existing-comments-${post.id}"></div>
                <form class="comment-form mt-4 space-y-2" data-post-id="${post.id}">
                    <input type="hidden" name="username" value="${currentUser ? currentUser.username : ''}">
                    <div class="flex space-x-2">
                        <input type="text" name="comment" placeholder="Escreva um comentário..." 
                               class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black sm:text-sm">
                        <button type="submit" 
                                class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black">
                            Enviar
                        </button>
                    </div>
                </form>
            </div>
        `;
        return div;
    }

    // Update active users count
    socket.on('update_users', function(data) {
        const activeUsersElement = document.getElementById('active-users');
        if (activeUsersElement) {
            activeUsersElement.textContent = data.active_users;
            activeUsersElement.classList.add('scale-110');
            setTimeout(() => {
                activeUsersElement.classList.remove('scale-110');
            }, 200);
        }
    });

    // Update total vent count
    socket.on('update_vent_count', function(data) {
        const ventCountElement = document.getElementById('vent-count');
        if (ventCountElement) {
            ventCountElement.textContent = data.vent_count;
            ventCountElement.classList.add('scale-110');
            setTimeout(() => {
                ventCountElement.classList.remove('scale-110');
            }, 200);
        }
    });

    // Handle connection errors
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
    });

    // Expose socket and currentUser to window for use in main.js
    window.socket = socket;
    window.getCurrentUser = function() {
        return currentUser;
    };
});
