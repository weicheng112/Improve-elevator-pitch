import React, { useState } from "react";
import "./App.css";
import { signUp, confirmUser, signIn } from "./auth";

const App = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [message, setMessage] = useState("");
  const [confirmationRequired, setConfirmationRequired] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState("");

  const handleSignUp = async () => {
    try {
      await signUp(email, password);
      setMessage(
        "Sign-up successful! A confirmation code has been sent to your email."
      );
      setConfirmationRequired(true);
    } catch (err) {
      setMessage(`Sign-up failed: ${err.message}`);
    }
  };

  const handleConfirm = async () => {
    try {
      await confirmUser(email, confirmationCode);
      setMessage("Confirmation successful! You can now sign in.");
      setConfirmationRequired(false);
    } catch (err) {
      setMessage(`Confirmation failed: ${err.message}`);
    }
  };

  const handleSignIn = async () => {
    try {
      const result = await signIn(email, password);
      setAuthToken(result.getIdToken().getJwtToken());
      setMessage("Sign-in successful!");
    } catch (err) {
      setMessage(`Sign-in failed: ${err.message}`);
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setMessage("You have been logged out.");
  };

  return (
    <div className="container">
      <h1>Video Processing App</h1>
      {!authToken ? (
        <div className="auth-form">
          {confirmationRequired ? (
            <div>
              <input
                type="text"
                placeholder="Enter Confirmation Code"
                value={confirmationCode}
                onChange={(e) => setConfirmationCode(e.target.value)}
                style={{ display: "block", margin: "10px 0" }}
              />
              <button onClick={handleConfirm} style={{ marginRight: "10px" }}>
                Confirm
              </button>
            </div>
          ) : (
            <div>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ display: "block", margin: "10px 0" }}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ display: "block", margin: "10px 0" }}
              />
              <button onClick={handleSignUp} style={{ marginRight: "10px" }}>
                Sign Up
              </button>
              <button onClick={handleSignIn}>Sign In</button>
            </div>
          )}
          {message && <p>{message}</p>}
        </div>
      ) : (
        <div>
          <p>Welcome! You are signed in.</p>
          <button onClick={handleLogout}>Log Out</button>
          <VideoUpload authToken={authToken} />
        </div>
      )}
    </div>
  );
};

const VideoUpload = ({ authToken }) => {
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
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
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
      {videoFile && <p>Selected File: {videoFile.name}</p>}
    </div>
  );
};

export default App;
