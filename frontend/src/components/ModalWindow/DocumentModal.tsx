import { 
  Alert, 
  Box, 
  Button, 
  Modal, 
  Paper, 
  Typography, 
  LinearProgress, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction,
  IconButton,
  Divider 
} from "@mui/material";
import { useState, useEffect } from "react";
import { useQuery, useMutation } from '@tanstack/react-query';
import { patientsApi } from '../../services/api';
import { 
  Download as DownloadIcon,
  Summarize as SummarizeIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import { format } from 'date-fns';

interface Document {
  id: string;
  title: string;
  file_path: string;
  uploaded_at: string;
}

interface DocumentModalProps {
  patient: any;
  open: boolean;
  handleClose: () => void;
}

export default function DocumentModal({ patient, open, handleClose }: DocumentModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  // Fetch documents query
  const { 
    data: documents = [], 
    isLoading, 
    refetch 
  } = useQuery({
    queryKey: ['patient-documents', patient?.id],
    queryFn: () => {
      console.log('Fetching documents for patient ID:', patient);
      if (!patient?.id) return Promise.resolve([]);
      return patientsApi.getPatientDocuments(patient.id);
    },
    enabled: Boolean(patient?.id) && open,
  });

  // Generate summary mutation
  const generateSummaryMutation = useMutation({
    mutationFn: () => {
      if (!patient?.id) return Promise.resolve(null);
      return patientsApi.generateDocumentsSummary(patient.id);
    },
    onSuccess: (data) => {
      if (!data) return;
      
      // Create a blob from the response data
      const blob = new Blob([data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `patient_${patient.id}_medical_summary.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setUploadProgress(0);
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.match('application/pdf|image/jpeg|image/png|application/msword|application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
        setError("Only PDF, DOCX, JPG, and PNG files are allowed");
        return;
      }
      if (file.size > 10 * 1024 * 1024) { // 10 MB size limit
        setError("File size exceeds 10MB limit");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !patient?.id) {
      setError("Please select a file");
      return;
    }
    
    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', selectedFile.name);
      
      await patientsApi.uploadDocument(patient.id, formData);
      
      setIsUploading(false);
      setSelectedFile(null);
      refetch(); // Refresh document list
    } catch (err: any) {
      console.error(err);
      setIsUploading(false);
      setError(err.response?.data?.message || "Upload failed");
    }
  };

  const handleDownload = async (documentId: string) => {
    try {
      const response = await patientsApi.downloadDocument(documentId);
      const blob = new Blob([response], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${documentId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading document:', error);
      setError("Failed to download document");
    }
  };

  const handleGenerateSummary = () => {
    generateSummaryMutation.mutate();
  };

  const handleCloseModal = () => {
    setError(null);
    setSelectedFile(null);
    setUploadProgress(0);
    setIsUploading(false);
    handleClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleCloseModal}
      aria-labelledby="document-modal"
      sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: "100%",
          maxWidth: 600,
          maxHeight: "90vh",
          overflow: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        <Typography variant="h6">Patient Documents</Typography>

        {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}
        {generateSummaryMutation.error && (
          <Alert severity="error">Error generating summary. Please try again.</Alert>
        )}

        {/* Documents List */}
        {isLoading ? (
          <LinearProgress />
        ) : documents.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center">
            No documents uploaded yet.
          </Typography>
        ) : (
          <List>
            {documents.map((doc: Document) => (
              <ListItem
                key={doc.id}
                divider
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={doc.title}
                  secondary={format(new Date(doc.uploaded_at), 'PPP')}
                  primaryTypographyProps={{
                    sx: { fontWeight: 500 }
                  }}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    aria-label="download"
                    onClick={() => handleDownload(doc.id)}
                    sx={{
                      '&:hover': {
                        color: 'primary.main',
                      },
                    }}
                  >
                    <DownloadIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}

        <Divider />

        {/* Upload Section */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="outlined"
            component="label"
            disabled={isUploading}
            startIcon={<UploadIcon />}
          >
            Select File
            <input
              type="file"
              hidden
              accept=".pdf,.docx,.jpg,.jpeg,.png"
              onChange={handleFileChange}
            />
          </Button>

          {selectedFile && (
            <Typography variant="body2" sx={{ flex: 1 }}>
              Selected: {selectedFile.name}
            </Typography>
          )}

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            startIcon={<UploadIcon />}
          >
            {isUploading ? `Uploading ${uploadProgress}%...` : "Upload"}
          </Button>
        </Box>

        {isUploading && <LinearProgress variant="determinate" value={uploadProgress} />}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateSummary}
            disabled={generateSummaryMutation.isPending || !documents.length}
            startIcon={<SummarizeIcon />}
          >
            Generate Summary
          </Button>

          <Button variant="outlined" onClick={handleCloseModal} disabled={isUploading}>
            Close
          </Button>
        </Box>
      </Paper>
    </Modal>
  );
}
