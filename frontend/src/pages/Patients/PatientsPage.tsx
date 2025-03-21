import { useState } from 'react';
import {
  Box,
  Button,
  Tab,
  Tabs,
  TextField,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
} from '@mui/x-data-grid';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { patientsApi } from '../../services/api';
import PatientModal from "../../components/ModalWindow/PatientModal.tsx";
import DocumentModal from "../../components/ModalWindow/DocumentModal.tsx";
import {UsersStatus} from "../../constants.ts";

interface Patient {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: 'Approved' | 'Unapproved';
  agreementLink: string;
}

export default function PatientsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [tabValue, setTabValue] = useState<any>(UsersStatus.APPROVED);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [isPatientModalOpen, setIsPatientModalOpen] = useState<boolean>(false);
  const [patientModalModeCreate, setPatientModalModeCreate] = useState<boolean>(false);
  const [isDocumentModalOpen, setIsDocumentModalOpen] = useState<boolean>(false);
  const queryClient = useQueryClient();

  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients', tabValue, searchTerm],
    queryFn: () =>
      patientsApi.getPatients({
        status: tabValue,
        search: searchTerm,
      }),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => patientsApi.approvePatient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => patientsApi.deletePatient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, patient: Patient) => {
    setAnchorEl(event.currentTarget);
    setSelectedPatient(patient);
  };


  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedPatient(null);
  };

  const handleEdit = () => {
    setIsPatientModalOpen(true);
    setPatientModalModeCreate(false);
    setAnchorEl(null);
  };

  const handleChangeApprove = () => {
    if (selectedPatient) {
      approveMutation.mutate(selectedPatient.id);
      handleMenuClose();
    }
  };

  const handleDelete = () => {
    if (selectedPatient) {
      deleteMutation.mutate(selectedPatient.id);
      handleMenuClose();
    }
  };

  const handleDownloadAgreement = async () => {
      try {
        const response = await patientsApi.downloadAgreement();
        if (response && response.link) {
          const a = document.createElement('a');
          a.href = response.link;
          a.download = `Agreement.pdf`;
          a.style.display = 'none';
          a.target = '_blank';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      } catch (error) {
        console.error('Error downloading document:', error);
      }
    };

  const columns: GridColDef[] = [
    { 
      field: 'id',
      headerName: 'No.',
      width: 70,
      sortable: false,
      filterable: false,
      renderCell: (params) => {
        const index = params.api
          .getSortedRowIds()
          .indexOf(params.id) + 1;
        return index;
      },
    },
    {
      field: 'full_name',
      headerName: 'Patient full name',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Box
          sx={{
            backgroundColor:
              params.value === 'Approved' ? 'success.light' : 'error.light',
            color: 'white',
            textAlign: 'center',
            height: 'inherit',
            borderRadius: 1,
          }}
        >
          {params.value}
        </Box>
      ),
    },
    { field: 'email', headerName: 'Email', flex: 1, minWidth: 200 },
    { field: 'phone', headerName: 'Phone number', width: 150 },
    {
      field: 'agreementLink',
      headerName: 'Agreement link',
      width: 150,
      renderCell: (params: GridRenderCellParams) => (
        <Button
          variant="text"
          onClick={(e) => {
            console.log('params', params);
            e.stopPropagation();
            handleDownloadAgreement();
          }}
        >
          Agreement
        </Button>
      ),
    },
    {
      field: 'actions',
      headerName: '',
      width: 50,
      renderCell: (params: GridRenderCellParams) => (
        <IconButton onClick={(e) => {
          e.stopPropagation();
          handleMenuClick(e, params.row);
        }}>
          <MoreVertIcon />
        </IconButton>
      ),
    },
  ];

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
        >
          <Tab
            value={UsersStatus.APPROVED}
            label={`Approved (${(patients ?? []).filter((patient: any) => patient.status === UsersStatus.APPROVED).length})`}
          />
          <Tab
            value={UsersStatus.UNAPPROVED}
            label={`Unapproved (${(patients ?? []).filter((patient: any) => patient.status === UsersStatus.UNAPPROVED).length})`}
          />
        </Tabs>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          size="small"
          placeholder="Search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ width: 300 }}
        />
        <Button
          variant="outlined"
          startIcon={<FilterListIcon />}
          size="small"
        >
          Filters
        </Button>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="small"
          onClick={() => 
            {
              setIsPatientModalOpen(true);
              setPatientModalModeCreate(true);
            }
          }
        >
          New patient
        </Button>
      </Box>

      <DataGrid
        rows={(patients ?? []).filter((patient: any) => patient.status === tabValue)}
        columns={columns}
        loading={isLoading}
        autoHeight
        disableRowSelectionOnClick
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
        onRowClick={(params) => {
          setSelectedPatient(params.row);
          setIsDocumentModalOpen(true)
        }}
      />

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleChangeApprove}>{tabValue === UsersStatus.UNAPPROVED ? 'Approve' : 'Unapprove'}</MenuItem>
        <MenuItem onClick={handleEdit}>Edit</MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          Delete
        </MenuItem>
      </Menu>
      <PatientModal
        patient={selectedPatient}
        createMode={patientModalModeCreate}
        open={isPatientModalOpen}
        handleClose={() => setIsPatientModalOpen(false)}
      />
      <DocumentModal
        patient={selectedPatient}
        open={isDocumentModalOpen}
        handleClose={() => setIsDocumentModalOpen(false)}
      />
    </Box>
  );
} 