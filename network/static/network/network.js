document.addEventListener('DOMContentLoaded', function () {
    // edit button listeners
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.onclick = function () {
            const postId = this.dataset.id;
            const contentDiv = document.querySelector(`#post-content-${postId}`);
            const editArea = document.querySelector(`#edit-area-${postId}`);

            contentDiv.style.display = 'none';
            editArea.style.display = 'block';
        };
    });

    // save button listeners
    document.querySelectorAll('.save-btn').forEach(button => {
        button.onclick = function () {
            const postId = this.dataset.id;
            const textarea = document.querySelector(`#edit-textarea-${postId}`);
            const content = textarea.value;

            fetch(`/projetos/network/edit/${postId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    content: content
                })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.message) {
                        const contentDiv = document.querySelector(`#post-content-${postId}`);
                        const editArea = document.querySelector(`#edit-area-${postId}`);

                        contentDiv.innerHTML = content;
                        contentDiv.style.display = 'block';
                        editArea.style.display = 'none';
                    } else {
                        alert(result.error);
                    }
                });
        };
    });

    // like button listeners
    document.querySelectorAll('.like-btn').forEach(button => {
        button.onclick = function () {
            const postId = this.dataset.id;
            const likeCount = document.querySelector(`#like-count-${postId}`);

            fetch(`/projetos/network/like/${postId}`, {
                method: 'PUT'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.likes !== undefined) {
                        likeCount.innerHTML = result.likes;
                        if (result.liked) {
                            this.className = 'fas fa-heart action-icon like-btn liked';
                            this.style.color = ''; // specific color handled by CSS
                        } else {
                            this.className = 'far fa-heart action-icon like-btn';
                            this.style.color = ''; // specific color handled by CSS
                        }
                    } else {
                        if (result.error === "Authentication required") {
                            window.location.href = "/projetos/network/login";
                        }
                    }
                });
        };
    });

    // sidebar toggle
    const sidebar = document.querySelector('.navbar');
    const toggleBtn = document.querySelector('#sidebar-toggle');
    const body = document.body;

    // load state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        body.classList.add('sidebar-collapsed');
    }

    if (toggleBtn) {
        toggleBtn.onclick = function () {
            body.classList.toggle('sidebar-collapsed');
            const collapsed = body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', collapsed);
        }
    }

    // comment toggles
    document.querySelectorAll('.view-comments-btn').forEach(btn => {
        btn.onclick = function () {
            const postId = this.dataset.id;
            const commentsList = document.querySelector(`#comments-list-${postId}`);
            if (commentsList.style.display === 'none') {
                commentsList.style.display = 'block';
                this.textContent = 'Hide comments';
            } else {
                commentsList.style.display = 'none';
                this.textContent = `View all ${commentsList.children.length} comments`;
            }
        };
    });

    document.querySelectorAll('.comment-toggle-btn').forEach(btn => {
        btn.onclick = function () {
            const postId = this.dataset.id;
            const inputWrapper = document.querySelector(`#comment-input-${postId}`);
            const list = document.querySelector(`#comments-list-${postId}`);

            if (inputWrapper.style.display === 'none') {
                inputWrapper.style.display = 'flex';
                inputWrapper.querySelector('input').focus();
                // also show list if hiding
                if (list) list.style.display = 'block';
            } else {
                inputWrapper.style.display = 'none';
            }
        };
    });

    // post comment
    document.querySelectorAll('.post-comment-btn').forEach(btn => {
        btn.onclick = function () {
            const postId = this.dataset.id;
            const input = document.querySelector(`#comment-input-${postId} input`);
            const content = input.value;
            const commentsList = document.querySelector(`#comments-list-${postId}`);

            if (!content.trim()) return;

            fetch(`/projetos/network/add_comment/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    content: content
                })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.comment) {
                        // append new comment
                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'comment small mb-1';
                        commentDiv.innerHTML = `<strong>${result.comment.user}</strong> ${result.comment.content}`;

                        // ensure list is visible
                        commentsList.style.display = 'block';
                        commentsList.appendChild(commentDiv);

                        // clear input
                        input.value = '';
                    } else {
                        console.error('Error posting comment');
                    }
                });
        };
    });

});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
