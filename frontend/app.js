const video = document.getElementById("video");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const studentsList = document.getElementById("students-list");
const addStudentForm = document.getElementById("add-student-form");
const addStudentMessage = document.getElementById("add-student-message");

let stream;

// Start camera when "Start Attendance" is clicked
startBtn.addEventListener("click", async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" },
        });
        video.srcObject = stream;
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } catch (err) {
        console.error("Error accessing camera:", err);
    }
});

// Stop camera and process frame when "Stop Attendance" is clicked
stopBtn.addEventListener("click", async () => {
    stream.getTracks().forEach(track => track.stop());
    startBtn.disabled = false;
    stopBtn.disabled = true;

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));

    const formData = new FormData();
    formData.append("frame", blob);

    try {
        const response = await fetch("http://127.0.0.1:5000/process_frame", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();

        studentsList.innerHTML = "";
        if (result.students && result.students.length > 0) {
            result.students.forEach(student => {
                const li = document.createElement("li");
                li.textContent = student;
                studentsList.appendChild(li);
            });
        } else {
            const li = document.createElement("li");
            li.textContent = "No students recognized.";
            studentsList.appendChild(li);
        }
    } catch (err) {
        console.error("Error processing frame:", err);
    }
});

// Handle "Add Student" form submission
addStudentForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("student-name").value;
    const photoFile = document.getElementById("student-photo").files[0];

    if (!photoFile) {
        addStudentMessage.textContent = "Please select a photo.";
        addStudentMessage.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo", photoFile);

    try {
        const response = await fetch("http://127.0.0.1:5000/add_student", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.status === 201) {
            addStudentMessage.textContent = "Student added successfully!";
            addStudentMessage.style.color = "green";
        } else {
            addStudentMessage.textContent = result.error || "Failed to add student.";
            addStudentMessage.style.color = "red";
        }

        addStudentForm.reset();
    } catch (err) {
        console.error("Error adding student:", err);
        addStudentMessage.textContent = "Error adding student.";
        addStudentMessage.style.color = "red";
    }
});
