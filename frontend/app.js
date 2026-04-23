//Set local storage variables in case page is refreshed while user is still logged in
let token = localStorage.getItem("token") || "";
let user_name = localStorage.getItem("user_name") || "";
const api_route = "/api";

//Declare SVG icons for chevron and drag handle
const chevron_down = `
    <span class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
    </span>
`

const chevron_up = `
    <span class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
        </svg>
    </span>
`

const bars_3 = `
    <span class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
    </span>
`

// ---=== UI REFRESH ===---
async function updateUI() {
    if (!token) {
        showLoggedOut();
        return;
    }

    try {
        const res = await fetch(`${api_route}/users/me`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Invalid token");

        // token is valid
        showLoggedIn();
        loadTasks();

    } catch (err) {
        // token is bad → clear it
        localStorage.removeItem("token");
        token = "";

        showLoggedOut();
    }
}

// ---=== LOGIN FUNCTION ===---
async function login() {
    const usernameVal = username.value;
    const passwordVal = password.value;

    // Basic frontend validation
    if (!usernameVal || !passwordVal) {
        showToast("Please enter username and password", "error");
        return;
    }

    const formData = new URLSearchParams();
    formData.append("username", usernameVal);
    formData.append("password", passwordVal);

    try {
        const res = await fetch(`${api_route}/login`, {
            method: "POST",
            body: formData
        });

        // Handle invalid login
        if (!res.ok) {
            showToast("Invalid username or password", "error");
            return;
        }

        const data = await res.json();

        // Store token only if valid
        token = data.access_token;
        localStorage.setItem("token", token);

        // Store username AFTER success
        user_name = usernameVal;
        localStorage.setItem("user_name", usernameVal);

        // Clear inputs
        username.value = "";
        password.value = "";

        updateUI();
        showToast("Logged in successfully!", "success");

    } catch (err) {
        showToast("Login failed. Server error.", "error");
    }
}

// ---=== LOGOUT FUNCTION ===---
function logout() {
    token = "";
    localStorage.setItem("token", "");
    user_name = "";
    localStorage.setItem("user_name", "");
    toggleMenu();
    updateUI();
    showToast("Logged out", "success");
}

// ---=== REGISTER FUNCTION ===---
async function register() {
    const usernameVal = document.getElementById("username").value;
    const passwordVal = document.getElementById("password").value;

    if (!usernameVal || !passwordVal) {
        showToast("Please enter a username and password!", "error");
        return;
    }

    const res = await fetch(`${api_route}/users`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: usernameVal,
            password: passwordVal
        })
    });

    if (res.ok) {
        showToast("User registered! You may now login.", "success")
    } else {
        const error = await res.json();
        showToast(error.detail[0].msg, "error");
    }
}

// ---=== CREATE TASK ===---
async function createTask() {
    title_value = document.getElementById("title").value;
    desc_value = document.getElementById("description").value;
    if (!title_value) {
        showToast("Title cannot be empty!", "error");
        return;
    }
    if(!desc_value) {
        showToast("Description cannot be empty!", "error");
        return;
    }
    document.getElementById("title").value = "";
    document.getElementById("description").value ="";
    showToast("Creating Task...", "info");
    toggleTaskForm();
    showSpinner();

    await fetch(`${api_route}/tasks`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title_value,
            description: desc_value
        })
    });

    hideSpinner();
    showToast("Task Created!", "success")
    loadTasks();
}

// ---=== LOAD TASKS ===---
async function loadTasks() {
    const res = await fetch(`${api_route}/tasks`, {
        headers: { "Authorization": `Bearer ${token}` }
    });

    const tasks = await res.json();
    const container = document.getElementById("tasks");
    container.innerHTML = "";

    tasks.forEach((task, index) => {
        const div = document.createElement("div");
        div.className = "task-card";
        div.style.animationDelay = `${index * 0.05}s`;
        div.id = `task-${task.id}`;
        div.dataset.id = task.id;

        if (task.completed) {
            div.classList.add("completed");
        }

        const generate_btn = !task.ai_generated ? `
             <button onclick="generateAI(${task.id})">Generate AI Summary</button>
        ` : "AI Generated";

        const aiSection = task.ai_generated ? `
            <div class="ai-container">
                <div class="ai-card">
                    <strong>AI Summary</strong>
                    <p>${task.ai_summary || "No summary available"}</p>
                </div>

                <div class="ai-card">
                    <strong>AI Breakdown</strong>
                    <ul>
                        ${(task.ai_breakdown || "").split("|").map(s => `<li>${s}</li>`).join("")}
                    </ul>
                </div>
            </div>
        ` : "";

        const completedCheckbox = `
            <input title="Task Completed?" class="task-check" type="checkbox"
                ${task.completed ? "checked" : ""}
                onclick="event.stopPropagation(); toggleComplete(${task.id})">
        `;

        div.innerHTML = `
            <div onclick="toggleTask(${task.id})" class="task-header">
                <div class="left-group">
                    ${completedCheckbox}
                    <span class="drag-handle">${bars_3}</span>
                </div>

                <div class="center-group">
                    <div class="task-title">${task.title}</div>
                </div>
                <div class="right-group">
                    <button class="toggle-btn" onclick="event.stopPropagation();toggleTask(${task.id});" id="toggle-${task.id}">
                        ${chevron_down}
                    </button>
                </div>
            </div>

            <div id="content-${task.id}" class="task-content">
                <div id="view-${task.id}">
                    <div>${task.description}</div>

                    <div class="task-actions">
                        ${generate_btn}
                        <button onclick="showEdit(${task.id})">Edit</button>

                        <span id="delete-${task.id}">
                            <button onclick="showDeleteConfirm(${task.id})">Delete</button>
                        </span>
                        <span id="confirm-${task.id}" style="display:none;">
                            <span>Are you sure?</span>
                            <button onclick="confirmDelete(${task.id})">Confirm</button>
                            <button onclick="cancelDelete(${task.id})">Cancel</button>
                        </span>
                    </div>
                </div>

                <div id="edit-${task.id}" style="display:none;">
                    Title:
                    <input id="edit-title-${task.id}" value="${task.title}">
                    Description:
                    <input id="edit-desc-${task.id}" value="${task.description}">

                    <button onclick="updateTask(${task.id})">Save</button>
                    <button onclick="cancelEdit(${task.id})">Cancel</button>
                </div>

                ${aiSection}
            </div>
        `;

        container.appendChild(div);
    });
    //Uses SortableJS to let the user drag and drop tasks to re-order
    const sort_container = document.getElementById("tasks");

    let originalOrder = [];

    new Sortable(sort_container, {
        forceFallback: true,
        fallbackClass: "drag-dragging",
        fallbackOnBody: true,
        swapThreshold: 0.65,
        animation: 200,
        easing: "cubic-bezier(0.22, 1, 0.36, 1)",
        ghostClass: "drag-ghost",
        chosenClass: "drag-chosen",
        dragClass: "drag-dragging",
        handle: ".drag-handle",

        onStart: function () {
            originalOrder = [...container.querySelectorAll(".task-card")]
            .map(el => el.dataset.id);
        },

        onEnd: function (evt) {
            const newOrder = [...container.querySelectorAll(".task-card")]
            .map(el => el.dataset.id);

        const changed = originalOrder.length !== newOrder.length ||
            originalOrder.some((id, index) => id !== newOrder[index]);

        if (!changed) {
            console.log("Order unchanged, skipping API call");
            return;
        }

        saveTaskOrder(newOrder);
        showToast("Task order updated", "success");
        }
    });
    showToast("Tasks successfully reloaded!", "success")
}

// ---=== SET TASK ORDER ===---
async function saveTaskOrder(taskIds) {
    await fetch(`${api_route}/tasks/reorder`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(taskIds)
    });
}

// ---=== EDIT TASKS ===---
async function updateTask(id) {
    const title = document.getElementById(`edit-title-${id}`).value;
    const description = document.getElementById(`edit-desc-${id}`).value;

    const btn = event.target;
    btn.disabled = true;
    btn.innerText = "Editing..."
    showSpinner();

    await fetch(`${api_route}/tasks/${id}`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            description: description
        })
    });

    hideSpinner();
    showToast("Successfully edited task!", "success")
    btn.disabled = false;
    btn.innerText = "Save"
    await loadTasks(); // refresh UI
    toggleTask(id)
}

// ---=== GENERATE AI ===---
async function generateAI(id) {
    showSpinner();

    await fetch(`${api_route}/tasks/${id}/generate-ai`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    hideSpinner();
    showToast("AI generated", "success");
    await loadTasks();
    toggleTask(id);
}

// ---=== DELETE TASK ===---
async function confirmDelete(id) {
    await fetch(`${api_route}/tasks/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });

    showToast("Task deleted", "success");
    loadTasks();
}

// ---=== DELETE ACCOUNT ===---
async function deleteAccount() {
    if (!confirm("Are you sure you want to delete your account? This cannot be undone!")) return;

    await fetch(`${api_route}/users/me`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    showToast("User account and all user tasks successfully deleted.", "success")
    // log out user
    logout();
}

// ---=== TOGGLE COMPLETE ===---
async function toggleComplete(taskId) {
    const res = await fetch(`${api_route}/tasks/${taskId}/toggle`, {
        method: "PUT",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await res.json(); // { completed: true/false }

    const taskCard = document.getElementById(`task-${taskId}`);

    if (!taskCard) return;

    if (data.completed) {
        taskCard.classList.add("completed");
    } else {
        taskCard.classList.remove("completed");
    }
}

// ---=== TOAST NOTIFICATIONS ===---
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerText = message;

    container.appendChild(toast);

    // trigger animation
    setTimeout(() => {
        toast.classList.add("show");
    }, 10);

    // remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove("show");

        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

/*
==================================
== Toggles and helper functions ==
==================================
*/
function showLoggedIn() {
    document.getElementById("login-section").style.display = "none";
    document.getElementById("app-section").style.display = "block";
    document.getElementById("page-title").innerText += " - " + user_name;
    document.getElementById("page-header").innerText += " - " + user_name;
}

function showLoggedOut() {
    document.getElementById("login-section").style.display = "block";
    document.getElementById("app-section").style.display = "none";
    document.getElementById("page-title").innerText = "Clean Tasks";
    document.getElementById("page-header").innerText = "Clean Tasks";
}

function showEdit(id) {
    document.getElementById(`view-${id}`).style.display = "none";
    document.getElementById(`edit-${id}`).style.display = "block";
}

function cancelEdit(id) {
    document.getElementById(`view-${id}`).style.display = "block";
    document.getElementById(`edit-${id}`).style.display = "none";
}

function showSpinner() {
    document.getElementById("overlay").style.display = "flex";
    document.body.style.overflow = "hidden";
}

function hideSpinner() {
    document.getElementById("overlay").style.display = "none";
    document.body.style.overflow = "auto";
}

function showDeleteConfirm(id) {
    document.getElementById(`delete-${id}`).style.display = "none";
    document.getElementById(`confirm-${id}`).style.display = "inline";
}

function cancelDelete(id) {
    document.getElementById(`delete-${id}`).style.display = "inline";
    document.getElementById(`confirm-${id}`).style.display = "none";
}

function toggleTask(id) {
    const content = document.getElementById(`content-${id}`);
    const button = document.getElementById(`toggle-${id}`);
    const isToggle = content.classList.toggle("open");

    if (isToggle) {
        button.innerHTML = chevron_up;
    } else {
        button.innerHTML = chevron_down;
    }
}

function toggleTaskForm() {
    const form = document.getElementById("task-form");
    form.style.display = form.style.display === "none" ? "block" : "none";
    const button = document.getElementById("fab-add-task");
    button.classList.toggle("open");
}

function toggleMenu() {
    const menu = document.getElementById("side-menu");
    menu.classList.toggle("open");
}

//Page load update in case of existing token.
updateUI();