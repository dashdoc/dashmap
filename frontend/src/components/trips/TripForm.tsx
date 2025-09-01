import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Alert,
  AlertIcon,
  Select,
  Textarea,
  SimpleGrid,
} from '@chakra-ui/react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

interface Trip {
  id: number;
  vehicle: number;
  vehicle_license_plate: string;
  dispatcher: number;
  dispatcher_name: string;
  name: string;
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled';
  planned_start_date: string;
  planned_start_time: string;
  actual_start_datetime?: string | null;
  actual_end_datetime?: string | null;
  notes: string;
  driver_notified: boolean;
  created_at: string;
  updated_at: string;
}

interface Vehicle {
  id: number;
  license_plate: string;
  make: string;
  model: string;
  driver_name: string;
  is_active: boolean;
}

interface TripFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  trip?: Trip | null;
}

const API_BASE_URL = 'http://localhost:8000/api';

export const TripForm: React.FC<TripFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
  trip,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    vehicle: '',
    status: 'draft' as Trip['status'],
    planned_start_date: '',
    planned_start_time: '',
    notes: '',
  });
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingVehicles, setLoadingVehicles] = useState(false);
  
  const { user } = useAuth();

  const fetchVehicles = async () => {
    try {
      setLoadingVehicles(true);
      const response = await axios.get(`${API_BASE_URL}/vehicles/`, {
        params: { company: user?.company_id }
      });
      const activeVehicles = (response.data.results || response.data).filter(
        (vehicle: Vehicle) => vehicle.is_active
      );
      setVehicles(activeVehicles);
    } catch (err) {
      console.error('Error fetching vehicles:', err);
    } finally {
      setLoadingVehicles(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchVehicles();
    }
  }, [isOpen, user?.company_id]);

  useEffect(() => {
    if (trip) {
      setFormData({
        name: trip.name,
        vehicle: trip.vehicle.toString(),
        status: trip.status,
        planned_start_date: trip.planned_start_date,
        planned_start_time: trip.planned_start_time,
        notes: trip.notes,
      });
    } else {
      setFormData({
        name: '',
        vehicle: '',
        status: 'draft',
        planned_start_date: '',
        planned_start_time: '',
        notes: '',
      });
    }
    setError('');
  }, [trip, isOpen]);

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const tripData = {
        ...formData,
        vehicle: parseInt(formData.vehicle),
        dispatcher: user?.id,
      };

      if (trip) {
        await axios.put(`${API_BASE_URL}/trips/${trip.id}/`, tripData);
      } else {
        await axios.post(`${API_BASE_URL}/trips/`, tripData);
      }

      onSuccess();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 
                          (trip ? 'Failed to update trip' : 'Failed to create trip');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {trip ? 'Edit Trip' : 'Add New Trip'}
        </ModalHeader>
        <ModalCloseButton />
        
        <form onSubmit={handleSubmit}>
          <ModalBody>
            <VStack spacing={4}>
              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} width="100%">
                <FormControl isRequired>
                  <FormLabel>Trip Name</FormLabel>
                  <Input
                    type="text"
                    value={formData.name}
                    onChange={handleChange('name')}
                    placeholder="Morning Route"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Vehicle</FormLabel>
                  <Select
                    value={formData.vehicle}
                    onChange={handleChange('vehicle')}
                    placeholder="Select vehicle"
                    disabled={loadingVehicles}
                  >
                    {vehicles.map((vehicle) => (
                      <option key={vehicle.id} value={vehicle.id}>
                        {vehicle.license_plate} - {vehicle.make} {vehicle.model} ({vehicle.driver_name})
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Status</FormLabel>
                  <Select
                    value={formData.status}
                    onChange={handleChange('status')}
                  >
                    <option value="draft">Draft</option>
                    <option value="planned">Planned</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Start Date</FormLabel>
                  <Input
                    type="date"
                    value={formData.planned_start_date}
                    onChange={handleChange('planned_start_date')}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Start Time</FormLabel>
                  <Input
                    type="time"
                    value={formData.planned_start_time}
                    onChange={handleChange('planned_start_time')}
                  />
                </FormControl>
              </SimpleGrid>

              <FormControl>
                <FormLabel>Notes</FormLabel>
                <Textarea
                  value={formData.notes}
                  onChange={handleChange('notes')}
                  placeholder="Trip notes and special instructions"
                  rows={3}
                />
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              type="submit"
              isLoading={isLoading}
              loadingText={trip ? 'Updating...' : 'Creating...'}
            >
              {trip ? 'Update Trip' : 'Create Trip'}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};