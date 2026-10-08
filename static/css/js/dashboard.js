// --- Core API Logic ---
async function addStudentAndGenerateGroup() {
    // 1. Get input values
    const studentName = document.getElementById("studentName").value;
    const communication = document.getElementById("Communication_Skills").value;
    const leadership = document.getElementById("Leadership").value;
    const technical = document.getElementById("Technical_Skill").value;
    const teamwork = document.getElementById("Teamwork").value;
    const problemSolving = document.getElementById("Problem_Solving_Skill").value;
    const creativity = document.getElementById("Creativity_Skill").value;
    const adaptability = document.getElementById("Adaptability_Skill").value;
    const attendance = document.getElementById("Attendance").value;

    // Basic Validation
    if (!studentName || !attendance) {
        alert("Please fill in at least Name and Attendance.");
        return;
    }

    const studentData = {
        name: studentName,
        Communication_Skills: communication,
        Leadership: leadership,
        Technical_Skill: technical,
        Teamwork: teamwork,
        Problem_Solving_Skill: problemSolving,
        Creativity_Skill: creativity,
        Adaptability_Skill: adaptability,
        Attendance: attendance
    };

    try {
        // Add student
        const addRes = await fetch("http://127.0.0.1:5000/add_student", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(studentData)
        });
        
        if (!addRes.ok) throw new Error('Failed to add student');
        
        const addData = await addRes.json();
        console.log("Student added:", addData);

        // Generate groups
        const groupRes = await fetch("http://127.0.0.1:5000/generate_groups", {
            method: "POST"
        });
        
        if (!groupRes.ok) {
            const errorData = await groupRes.json();
            throw new Error(errorData.error || 'Failed to generate groups');
        }

        const groupData = await groupRes.json();
        console.log("Groups generated:", groupData);

        // Display groups
        displayGroups(groupData.groups);
        
        // Clear form
        document.querySelectorAll('input').forEach(input => input.value = '');

    } catch (error) {
        console.error("Error:", error);
        alert("Error: " + error.message);
    }
}

// --- UI Rendering Logic ---
function displayGroups(groups) {
    const groupsDiv = document.getElementById("groupsDisplay");
    groupsDiv.innerHTML = ""; // clear previous

    if (!groups || groups.length === 0) {
        groupsDiv.innerHTML = "<p>No groups generated.</p>";
        return;
    }

    groups.forEach(g => {
        const groupElem = document.createElement("div");
        // Updated class to match the styled CSS (.group-card)
        groupElem.classList.add("group-card"); 
        
        // Assumes g.Group_Number is A, B, C etc. and g.Members is an array
        groupElem.innerHTML = `
            <h4>Group ${g.Group_Number}</h4>
            <ul>${g.Members.map(m => `<li>${m}</li>`).join('')}</ul>
        `;
        groupsDiv.appendChild(groupElem);
    });
}