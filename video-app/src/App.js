import React, { useState } from "react";
import "./App.css";

const App = () => {
  const [videoFile, setVideoFile] = useState(null);

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!videoFile) {
      alert("Please select a file first.");
      return;
    }

    try {
      const response = await fetch("https://your-api-endpoint/process-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName: videoFile.name }),
      });
      const data = await response.json();
      alert(`Response from API: ${JSON.stringify(data)}`);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file.");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Video Processing App</h1>
      <div>
        <label
          style={{
            cursor: "pointer",
            color: "blue",
            textDecoration: "underline",
          }}
        >
          Select Video File
          <input
            type="file"
            accept="video/*"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
        </label>
        <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
          Upload Video
        </button>
      </div>
      {videoFile && <p>Selected File: {videoFile.name}</p>}
    </div>
  );
};

export default App;
