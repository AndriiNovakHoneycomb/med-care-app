import { useState } from 'react';
import {
  Box,
  Button,
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
import { adminsApi } from '../../services/api.ts';

interface Patient {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: 'Approved' | 'Unapproved';
  agreementLink: string;
}

export default function AdminsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const queryClient = useQueryClient();

  const { data: admins, isLoading } = useQuery({
    queryKey: ['admins', searchTerm],
    queryFn: () =>
      adminsApi.getAdmins({
        search: searchTerm,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => adminsApi.deleteAdmin(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admins'] });
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

  const handleDelete = () => {
    if (selectedPatient) {
      deleteMutation.mutate(selectedPatient.id);
      handleMenuClose();
    }
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    {
      field: 'name',
      headerName: 'Admin name & surname',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'email',
      headerName: 'Email',
      flex: 1,
      minWidth: 200,
    },
    { field: 'phone', headerName: 'Phone number', width: 150 },
    {
      field: 'agreementLink',
      headerName: 'Agreement link',
      width: 150,
      renderCell: (params: GridRenderCellParams) => (
        <Button
          variant="text"
          href={params.value}
          target="_blank"
          rel="noopener noreferrer"
        >
          Agreement {params.row.id}
        </Button>
      ),
    },
    {
      field: 'actions',
      headerName: '',
      width: 50,
      renderCell: (params: GridRenderCellParams) => (
        <IconButton onClick={(e) => handleMenuClick(e, params.row)}>
          <MoreVertIcon />
        </IconButton>
      ),
    },
  ];

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
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
        >
          New Admin
        </Button>
      </Box>

      <DataGrid
        rows={admins ?? []}
        columns={columns}
        loading={isLoading}
        autoHeight
        disableRowSelectionOnClick
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
      />

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>Edit</MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
}