document.addEventListener('DOMContentLoaded', function() {
    
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(taskForm);
            
            fetch(taskForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json',
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
   
    document.querySelectorAll('.toggle-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                const taskItem = form.closest('.task-item');
                const checkbox = form.querySelector('.checkbox-btn');
                
                if (data.completed) {
                    taskItem.classList.add('completed');
                    checkbox.classList.add('checked');
                    checkbox.innerHTML = '<i class="fas fa-check"></i>';
                } else {
                    taskItem.classList.remove('completed');
                    checkbox.classList.remove('checked');
                    checkbox.innerHTML = '';
                }
            }
        });
    });
    
   
    document.querySelectorAll('.important-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                const starIcon = form.querySelector('.fa-star');
                
                if (data.important) {
                    starIcon.classList.add('important');
                } else {
                    starIcon.classList.remove('important');
                }
            }
        });
    });
    
    
    const modal = document.getElementById('taskModal');
    const newTaskBtn = document.getElementById('new-task-btn');
    const closeBtn = document.querySelector('.close');

    if (newTaskBtn) {
        newTaskBtn.addEventListener('click', function() {
            modal.style.display = 'block';
            document.getElementById('due_date').valueAsDate = new Date();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

   
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', function(e) {
           
            modal.style.display = 'none';
        });
    }

   
    if (modal) {
        modal.addEventListener('shown', function() {
            const taskInput = modal.querySelector('input[name="title"]');
            if (taskInput) {
                taskInput.focus();
            }
        });
    }

  
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});