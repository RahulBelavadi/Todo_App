  const todoForm = document.getElementById('todoForm');
  const taskList = document.getElementById('taskList');
  const emptyMessage = document.getElementById('emptyMessage');

  document.addEventListener('DOMContentLoaded', () => {
    const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
    tasks.forEach(task => addTaskToDOM(task));
    updateEmptyMessage();
  });

  function updateEmptyMessage() {
    emptyMessage.style.display = taskList.children.length === 0 ? 'block' : 'none';
  }

  function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, options);
  }

  function addTaskToDOM(task) {
    const li = document.createElement('li');
    li.className = 'bg-gray-400 rounded-2xl p-3 shadow-md flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 sm:gap-0 transition hover:shadow-blue-200';

    const leftDiv = document.createElement('div');
    leftDiv.className = 'flex flex-col gap-1 max-w-[70%]';

    const nameEl = document.createElement('h3');
    nameEl.className = 'text-indigo-900 font-bold text-[18px] flex items-center gap-2';
    nameEl.innerHTML = `<i class="fas fa-check-circle text-indigo-600"></i> ${task.name}`;

    const descEl = document.createElement('p');
    descEl.className = 'text-indigo-800 text-[16px] leading-snug whitespace-pre-line';
    descEl.textContent = task.description;

    const deadlineEl = document.createElement('span');
    deadlineEl.className = 'inline-block mt-1 text-indigo-700 bg-indigo-200 rounded-full px-2 py-0.5 text-[11px] font-medium tracking-wide w-max shadow-inner';
    deadlineEl.textContent = `Deadline: ${formatDate(task.deadline)}`;

    leftDiv.appendChild(nameEl);
    leftDiv.appendChild(descEl);
    leftDiv.appendChild(deadlineEl);

    const rightDiv = document.createElement('div');
    rightDiv.className = 'flex items-center gap-3';

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'text-indigo-600 hover:text-indigo-900 transition text-xl p-2 rounded-full hover:bg-red-400 active:scale-90';
    deleteBtn.setAttribute('aria-label', 'Delete task');
    deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';

    deleteBtn.addEventListener('click', () => {
      li.classList.add('opacity-0', 'scale-95', 'transition-all');
      setTimeout(() => {
        taskList.removeChild(li);
        removeTaskFromStorage(task);
        updateEmptyMessage();
      }, 300);
    });

    rightDiv.appendChild(deleteBtn);

    li.appendChild(leftDiv);
    li.appendChild(rightDiv);

    taskList.prepend(li);
  }

  function saveTaskToStorage(task) {
    const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
    tasks.push(task);
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }

  function removeTaskFromStorage(task) {
    const tasks = JSON.parse(localStorage.getItem('tasks')) || [];
    const updatedTasks = tasks.filter(t => t.name !== task.name || t.deadline !== task.deadline);
    localStorage.setItem('tasks', JSON.stringify(updatedTasks));
  }

  todoForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const taskName = todoForm.taskName.value.trim();
    const taskDescription = todoForm.taskDescription.value.trim();
    const taskDeadline = todoForm.taskDeadline.value;

    if (!taskName || !taskDescription || !taskDeadline) return;

    const task = { name: taskName, description: taskDescription, deadline: taskDeadline };

    addTaskToDOM(task);
    saveTaskToStorage(task);

    todoForm.reset();
    updateEmptyMessage();
  });

  updateEmptyMessage();

