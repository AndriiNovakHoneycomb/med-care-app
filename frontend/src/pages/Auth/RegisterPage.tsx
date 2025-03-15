import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Alert,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../services/api';
import { useAuthStore } from '../../store/authStore';

const schema = yup.object({
  name: yup.string().required('Full name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup
    .string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
});

type FormData = yup.InferType<typeof schema>;

export default function RegisterPage() {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
  });

  const registerMutation = useMutation({
    mutationFn: (data: FormData) =>
      authApi.register(data.email, data.password, data.name),
    onSuccess: (response) => {
      const { token, user } = response.data;
      setAuth(token, user);
      navigate('/patients');
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Registration failed');
    },
  });

  const onSubmit = (data: FormData) => {
    setError(null);
    registerMutation.mutate(data);
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.100',
      }}
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
        <Typography variant="h5" component="h1" gutterBottom align="center">
          Med Care Admin
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          Create your account
        </Typography>

        {error && <Alert severity="error">{error}</Alert>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
              label="Password"
              type="password"
              {...register('password')}
              error={!!errors.password}
              helperText={errors.password?.message}
            />
            <TextField
              label="Confirm Password"
              type="password"
              {...register('confirmPassword')}
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword?.message}
            />
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={registerMutation.isPending}
            >
              {registerMutation.isPending ? 'Creating account...' : 'Create account'}
            </Button>
          </Box>
        </form>

        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Already have an account?
          </Typography>
          <Link href="/login" variant="body2">
            Sign in
          </Link>
        </Box>
      </Paper>
    </Box>
  );
} 