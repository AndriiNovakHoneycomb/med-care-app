import {Alert, Box, Button, Modal, TextField, Paper} from "@mui/material";
import {useForm} from "react-hook-form";
import {yupResolver} from "@hookform/resolvers/yup";
import {useMutation} from "@tanstack/react-query";
import {authApi} from "../../services/api.ts";
import {useState} from "react";
import * as yup from "yup";

const schema = yup.object({
  name: yup.string().required('Full name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string().required('Phone number is required'),
});

type FormData = yup.InferType<typeof schema>;

export default function AddPatientModal({ open, handleClose }: { open: boolean, handleClose: () => void }) {
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  });



  const registerMutation = useMutation({
    mutationFn: (data: FormData) =>
      authApi.register(data.email, data.phone, data.name),
    onSuccess: (response) => {
        console.log('###############', response);
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Registration failed');
    },
  });

  const onSubmit = (data: FormData) => {
    setError(null);
    registerMutation.mutate(data);
  };

  const onCloseModal = () => {
    handleClose();
    reset();
  };

  return (
    <Modal
      open={open}
      onClose={onCloseModal}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
      sx={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 400,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {error && <Alert severity="error">{error}</Alert>}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Box sx={{display: 'flex', flexDirection: 'column', gap: 2}}>
            <TextField
              label="Full Name"
              {...register('name')}
              error={!!errors.name}
              helperText={errors.name?.message}
            />
            <TextField
              label="Email"
              type="email"
              {...register('email')}
              error={!!errors.email}
              helperText={errors.email?.message}
            />
            <TextField
              label="Phone"
              {...register('phone')}
              error={!!errors.phone}
              helperText={errors.phone?.message}
            />
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? 'Creating patient...' : 'Create patient'}
            </Button>
            <Button
              type="button"
              variant="contained"
              size="large"
              onClick={onCloseModal}
            >
              Close
            </Button>
          </Box>
        </form>
      </Paper>
    </Modal>
  );
};