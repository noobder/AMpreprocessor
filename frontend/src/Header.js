import { useState, useRef } from "react";
import "./Header.css"

const FileUploader = () => {
  const fileInputRef = useRef(null);
  const [errorData, setErrorData] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(false); // 🔹 New loading state

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file.name);
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setErrorData(result.error_report || null);
        setDataset(result.tdata || null);
        console.log(dataset)
      } else {
        setErrorData(result.error || "An error occurred.");
      }
    } catch (error) {
      setErrorData("Failed to upload the file.");
    }
    finally {
      setLoading(false); // 🔹 Hide loading after response
    }
  };

  return (
    <div className="full">
       {loading && <div className="loading-text"></div>} {/* 🔹 Show loading */}
      <div className="head">Automated Preprocessor</div>
      <div className="but">
        <button onClick={handleButtonClick} disabled={loading}>{loading ? "Uploading..." : "Upload"}</button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>
     
      <div className="screens">
        <div className="screen">
          {errorData && (
            <div className="container">
            <h3>Uploaded File: {uploadedFile}</h3>

              <h3>Error Report:</h3>
              <table className="table">
                <thead>
                  <tr>
                    {Object.keys(errorData).map((key, index) => (
                      <th key={index}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {errorData.Column &&
                    errorData.Column.map((_, index) => (
                      <tr key={index}>
                        {Object.keys(errorData).map((key) => (
                          <td key={key}>{errorData[key][index]}</td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        

        <div className="screen">
          {dataset && (
            <div className="container">
              <h3>Uploaded File: {uploadedFile}</h3>
              <h3>Dataset:</h3>
              <table className="table">
                <thead>
                  <tr>
                    {Object.keys(dataset).map((key, index) => (
                      <th key={index}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataset[Object.keys(dataset)[0]].map((_, index) => (
                    <tr key={index}>
                      {Object.keys(dataset).map((key) => (
                        <td key={key}>{dataset[key][index]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
