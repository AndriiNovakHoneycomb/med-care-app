import { Alert, Box, Button, Modal, Paper, Typography, LinearProgress, List, ListItem, ListItemText, Divider } from "@mui/material";
import { useState, useEffect } from "react";
import axios from "axios";

import { documentsApi } from '../../services/api';

interface UploadedFile {
  id: string;
  fileName: string;
  fileUrl: string;
}

export default function FileUploadModal({
  patient,
  open,
  handleClose,
}: {
  patient: any;
  open: boolean;
  handleClose: () => void;
}) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  // Fetch uploaded files when modal opens
  useEffect(() => {
    if (open) {
      fetchUploadedFiles();
    }
  }, [open]);

  const fetchUploadedFiles = async () => {
    try {

      //const data = documentsApi.getDocuments(patient.id);
      const data = {
        "files": [
          { "id": "1", "fileName": "document1.docx", "fileUrl": "https://s3.amazonaws.com/..." },
          { "id": "2", "fileName": "report.docx", "fileUrl": "https://s3.amazonaws.com/..." }
        ]
      }
      setUploadedFiles(data.files); // Expecting { files: [...] }
    } catch (err) {
      console.error(err);
      setError("Failed to fetch uploaded files");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setUploadProgress(0);
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
        setError("Only .docx files are allowed");
        return;
      }
      if (file.size > 5 * 1024 * 1024) { // 5 MB size limit
        setError("File size exceeds 5MB limit");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file");
      return;
    }
    try {
      setIsUploading(true);

      // 1. Request pre-signed URL from backend
      const { data } = await axios.post("/api/get-presigned-url", {
        fileName: selectedFile.name,
        fileType: selectedFile.type,
      });
      const { url, key } = data;

      // 2. Upload file directly to S3
      await axios.put(url, selectedFile, {
        headers: { "Content-Type": selectedFile.type },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total ?? 1));
          setUploadProgress(percent);
        },
      });

    //   await axios.post("/api/save-uploaded-file", {
    //     patientId,
    //     fileKey: key,
    //     fileName: selectedFile.name,
    //   });

      setIsUploading(false);
      setSelectedFile(null);
      fetchUploadedFiles(); // Refresh file list
    } catch (err: any) {
      console.error(err);
      setIsUploading(false);
      setError(err.response?.data?.message || "Upload failed");
    }
  };

  const handleCloseModal = () => {
    setError(null);
    setSelectedFile(null);
    setUploadProgress(0);
    setIsUploading(false);
    setUploadedFiles([]);
    handleClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleCloseModal}
      aria-labelledby="file-upload-modal"
      sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: "100%",
          maxWidth: 500,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        <Typography variant="h6">Uploaded Documents</Typography>

        {error && <Alert severity="error">{error}</Alert>}

        {/* Uploaded Files List */}
        <List>
          {uploadedFiles.length === 0 ? (
            <Typography variant="body2">No uploaded files yet.</Typography>
          ) : (
            uploadedFiles.map((file) => (
              <ListItem key={file.id} disablePadding>
                <ListItemText
                  primary={
                    <a href={file.fileUrl} target="_blank" rel="noopener noreferrer">
                      {file.fileName}
                    </a>
                  }
                />
              </ListItem>
            ))
          )}
        </List>

        <Divider />

        {/* File Selection */}
        <Button variant="outlined" component="label" disabled={isUploading}>
          Select .docx File
          <input
            type="file"
            hidden
            accept=".docx"
            onChange={handleFileChange}
          />
        </Button>

        {selectedFile && (
          <Typography variant="body2">
            Selected File: {selectedFile.name}
          </Typography>
        )}

        {isUploading && <LinearProgress variant="determinate" value={uploadProgress} />}

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
        >
          {isUploading ? `Uploading ${uploadProgress}%...` : "Upload"}
        </Button>

        <Button variant="contained" onClick={handleCloseModal} disabled={isUploading}>
          Close
        </Button>
      </Paper>
    </Modal>
  );
}
