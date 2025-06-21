document.addEventListener('DOMContentLoaded', function() {
    // Handle like button clicks
    document.querySelectorAll('.like-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            const currentUser = window.getCurrentUser();
            if (!currentUser) {
                alert('Por favor, aguarde enquanto seu usuário é registrado.');
                return;
            }

            const postId = this.getAttribute('data-post-id');
            const formData = new FormData();
            formData.append('user_id', currentUser.user_id);

            fetch(`/like/${postId}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else if (data.likes !== undefined) {
                    this.querySelector('.like-count').textContent = data.likes;
                    this.classList.add('text-blue-600');
                    this.disabled = true;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle comment section toggle
    document.querySelectorAll('.comment-btn').forEach(function(button) {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            const commentSection = document.getElementById(`comments-${postId}`);
            
            if (commentSection.style.display === "none" || commentSection.style.display === "") {
                // Load existing comments
                fetch(`/comments/${postId}`)
                    .then(response => response.json())
                    .then(comments => {
                        const container = document.getElementById(`existing-comments-${postId}`);
                        container.innerHTML = '';

                        // Organize comments into a hierarchy
                        const commentMap = new Map();
                        const rootComments = [];

                        comments.forEach(comment => {
                            commentMap.set(comment.id, {
                                ...comment,
                                replies: []
                            });
                        });

                        comments.forEach(comment => {
                            if (comment.parent_id) {
                                const parentComment = commentMap.get(comment.parent_id);
                                if (parentComment) {
                                    parentComment.replies.push(commentMap.get(comment.id));
                                }
                            } else {
                                rootComments.push(commentMap.get(comment.id));
                            }
                        });

                        // Function to render a comment and its replies
                        function renderComment(comment, level = 0) {
                            const commentDiv = document.createElement('div');
                            commentDiv.className = 'bg-gray-50 rounded p-3 mb-2';
                            if (level > 0) {
                                commentDiv.classList.add('ml-6', 'border-l-2', 'border-gray-200');
                            }
                            
                            // Create comment content
                            let commentHtml = `
                                <div class="flex justify-between items-start">
                                    <div class="flex items-center space-x-2">
                                        <span class="font-medium text-gray-900">${comment.username}</span>
                                        ${comment.parent_id ? `
                                            <span class="text-sm text-gray-500">
                                                respondeu a ${commentMap.get(comment.parent_id)?.username || 'comentário'}
                                            </span>
                                        ` : ''}
                                    </div>
                                    <span class="text-sm text-gray-500">${comment.created_at}</span>
                                </div>
                                <p class="text-gray-700 mt-1">${comment.content}</p>
                                <button class="reply-btn text-sm text-gray-500 hover:text-gray-700 mt-2" 
                                        data-comment-id="${comment.id}">
                                    Responder
                                </button>
                            `;

                            commentDiv.innerHTML = commentHtml;
                            container.appendChild(commentDiv);

                            // Add reply form handler
                            const replyBtn = commentDiv.querySelector('.reply-btn');
                            if (replyBtn) {
                                replyBtn.addEventListener('click', function() {
                                    const currentUser = window.getCurrentUser();
                                    if (!currentUser) {
                                        alert('Por favor, aguarde enquanto seu usuário é registrado.');
                                        return;
                                    }

                                    // Remove any existing reply forms
                                    document.querySelectorAll('.reply-form').forEach(form => form.remove());
                                    document.querySelectorAll('.reply-btn').forEach(btn => btn.style.display = 'block');

                                    const replyForm = document.createElement('form');
                                    replyForm.className = 'mt-2 space-y-2 reply-form ml-6';
                                    replyForm.innerHTML = `
                                        <input type="hidden" name="parent_id" value="${comment.id}">
                                        <div class="flex space-x-2">
                                            <input type="text" name="comment" placeholder="Sua resposta..." required
                                                   class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-black focus:ring-black sm:text-sm">
                                            <button type="submit" 
                                                    class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black">
                                                Enviar
                                            </button>
                                        </div>
                                    `;
                                    
                                    // Insert reply form after the comment
                                    commentDiv.appendChild(replyForm);
                                    replyBtn.style.display = 'none';

                                    // Handle reply form submission
                                    replyForm.addEventListener('submit', function(e) {
                                        e.preventDefault();
                                        handleCommentSubmit(this, postId);
                                    });
                                });
                            }

                            // Render replies
                            if (comment.replies && comment.replies.length > 0) {
                                comment.replies.forEach(reply => {
                                    renderComment(reply, level + 1);
                                });
                            }
                        }

                        // Render root comments
                        rootComments.forEach(comment => {
                            renderComment(comment);
                        });

                        commentSection.style.display = "block";
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                commentSection.style.display = "none";
            }
        });
    });

    // Handle comment form submissions
    function handleCommentSubmit(form, postId) {
        const currentUser = window.getCurrentUser();
        if (!currentUser) {
            alert('Por favor, aguarde enquanto seu usuário é registrado.');
            return;
        }

        const formData = new FormData(form);
        formData.set('username', currentUser.username);

        fetch(`/comment/${postId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                // Refresh comments
                document.querySelector(`.comment-btn[data-post-id="${postId}"]`).click();
                form.reset();
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    document.querySelectorAll('.comment-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const postId = this.getAttribute('data-post-id');
            handleCommentSubmit(this, postId);
        });
    });
});
