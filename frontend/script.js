let latestResultData = null;

document.addEventListener("DOMContentLoaded", function () {

document.getElementById("riskForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    console.log("FORM SUBMITTED");

    const resultSection = document.getElementById("result");
    resultSection.classList.add("hidden");

    const imageFile = document.getElementById("image").files[0];

    if (!imageFile) {
        alert("Please upload a retinal image.");
        return;
    }

    const formData = new FormData();
    formData.append("file", imageFile);
    formData.append("age", document.getElementById("age").value);
    formData.append("sex", document.getElementById("sex").value);
    formData.append("sys_bp", document.getElementById("sys_bp").value);
    formData.append("dia_bp", document.getElementById("dia_bp").value);
    formData.append("diabetes", document.getElementById("diabetes").value);

    try {
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error.");
        }

	const data = await response.json();

	// Merge prediction + input details
	latestResultData = {
  		age: document.getElementById("age").value,
  	  	sex: document.getElementById("sex").value,
  	  	sys_bp: document.getElementById("sys_bp").value,
    	  	dia_bp: document.getElementById("dia_bp").value,
    		diabetes: document.getElementById("diabetes").value,
 	   	risk_percentage: data.risk_percentage,
  	  	risk_category: data.risk_category,
 	   	explanation: data.explanation,
  	  	recommendations: data.recommendations
	};


        document.getElementById("riskPercentage").innerText =
            data.risk_percentage ? data.risk_percentage.toFixed(2) : "0.00";

        const categoryElement = document.getElementById("riskCategory");
        categoryElement.innerText = data.risk_category || "Unknown";
        categoryElement.classList.remove("low", "moderate", "high");

        if (data.risk_category === "Low Risk") {
            categoryElement.classList.add("low");
        } else if (data.risk_category === "Moderate Risk") {
            categoryElement.classList.add("moderate");
        } else if (data.risk_category === "High Risk") {
            categoryElement.classList.add("high");
        }

        document.getElementById("explanation").innerText =
            data.explanation || "";

        const recList = document.getElementById("recommendations");
        recList.innerHTML = "";

        if (Array.isArray(data.recommendations)) {
            data.recommendations.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                recList.appendChild(li);
            });
        }

        resultSection.classList.remove("hidden");

    } catch (error) {
        console.error(error);
        alert("Something went wrong.");
    }
});


/* ===========================
   DOWNLOAD REPORT
=========================== */

document.getElementById("downloadReport").addEventListener("click", async function() {

    if (!latestResultData) {
        alert("Please assess risk first.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/download-report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(latestResultData)
        });

        if (!response.ok) {
            throw new Error("Failed to generate report");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "Retinal_CVD_Risk_Report.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();

        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error(error);
        alert("Report download failed.");
    }
});

});

