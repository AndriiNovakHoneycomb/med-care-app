import { useState } from 'react';
import {
  Box,
  Button,
  TextField,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
} from '@mui/x-data-grid';
import {
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import { useQuery  } from '@tanstack/react-query';
import { adminsApi } from '../../services/api.ts';

export default function AdminsPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: admins, isLoading } = useQuery({
    queryKey: ['admins', searchTerm],
    queryFn: () =>
      adminsApi.getAdmins({
        search: searchTerm,
      }),
  });

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
      headerName: 'Admin full name',
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
    </Box>
  );
}