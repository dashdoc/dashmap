import React, { useEffect, useState } from 'react';
import {
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  VStack,
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  HStack,
  IconButton,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { DeleteIcon } from '@chakra-ui/icons';
import axios from 'axios';

interface Trip {
  id: number;
  vehicle: number;
  vehicle_license_plate: string;
  name: string;
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled';
  planned_start_date: string;
  planned_start_time: string;
  notes: string;
}

interface Stop {
  id: number;
  name: string;
}

interface TripStop {
  id: number;
  stop: Stop;
  order: number;
  planned_arrival_time: string;
}

interface TripDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  trip: Trip | null;
  onTripUpdated: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api';

export const TripDetailsDrawer: React.FC<TripDetailsDrawerProps> = ({
  isOpen,
  onClose,
  trip,
  onTripUpdated,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    vehicle: '',
    status: 'draft' as Trip['status'],
    planned_start_date: '',
    planned_start_time: '',
    notes: '',
  });
  const [tripStops, setTripStops] = useState<TripStop[]>([]);
  const [stops, setStops] = useState<Stop[]>([]);
  const [newStop, setNewStop] = useState({ stopId: '', time: '' });
  const [error, setError] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  const fetchTripDetails = async () => {
    if (!trip) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/trips/${trip.id}/`);
      const data = response.data;
      setFormData({
        name: data.name,
        vehicle: data.vehicle.toString(),
        status: data.status,
        planned_start_date: data.planned_start_date,
        planned_start_time: data.planned_start_time,
        notes: data.notes || '',
      });
      setTripStops(data.trip_stops || []);
    } catch (err) {
      console.error('Error fetching trip details:', err);
    }
  };

  const fetchStops = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stops/`);
      setStops(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching stops:', err);
    }
  };

  useEffect(() => {
    if (isOpen && trip) {
      fetchTripDetails();
      fetchStops();
      setError('');
      setNewStop({ stopId: '', time: '' });
    }
  }, [isOpen, trip]);

  const handleChange = (field: string) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }));
  };

  const handleSave = async () => {
    if (!trip) return;
    setIsSaving(true);
    setError('');
    try {
      await axios.put(`${API_BASE_URL}/trips/${trip.id}/`, {
        ...formData,
        vehicle: parseInt(formData.vehicle),
      });
      onTripUpdated();
      onClose();
    } catch (err) {
      const errorMessage = (err as { response?: { data?: { error?: string } } }).response?.data?.error ||
        'Failed to update trip';
      setError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddStop = async () => {
    if (!trip || !newStop.stopId || !newStop.time) return;
    setIsAdding(true);
    setError('');
    try {
      await axios.post(`${API_BASE_URL}/trip-stops/`, {
        trip: trip.id,
        stop: parseInt(newStop.stopId),
        order: tripStops.length + 1,
        planned_arrival_time: newStop.time,
      });
      await fetchTripDetails();
      onTripUpdated();
      setNewStop({ stopId: '', time: '' });
    } catch (err) {
      console.error('Error adding stop:', err);
      setError('Failed to add stop');
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteStop = async (id: number) => {
    try {
      await axios.delete(`${API_BASE_URL}/trip-stops/${id}/`);
      await fetchTripDetails();
      onTripUpdated();
    } catch (err) {
      console.error('Error deleting stop:', err);
      setError('Failed to delete stop');
    }
  };

  const availableStops = stops.filter(
    s => !tripStops.some(ts => ts.stop.id === s.id)
  );

  return (
    <Drawer isOpen={isOpen} placement="right" onClose={onClose} size="lg">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>Trip Details</DrawerHeader>

        <DrawerBody>
          <VStack spacing={4} align="stretch">
            {error && (
              <Alert status="error">
                <AlertIcon />
                {error}
              </Alert>
            )}

            <FormControl>
              <FormLabel>Trip Name</FormLabel>
              <Input value={formData.name} onChange={handleChange('name')} />
            </FormControl>

            <FormControl>
              <FormLabel>Vehicle</FormLabel>
              <Input value={trip?.vehicle_license_plate || ''} isDisabled />
            </FormControl>

            <FormControl>
              <FormLabel>Status</FormLabel>
              <Select value={formData.status} onChange={handleChange('status')}>
                <option value="draft">Draft</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </Select>
            </FormControl>

            <HStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Start Date</FormLabel>
                <Input
                  type="date"
                  value={formData.planned_start_date}
                  onChange={handleChange('planned_start_date')}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Start Time</FormLabel>
                <Input
                  type="time"
                  value={formData.planned_start_time}
                  onChange={handleChange('planned_start_time')}
                />
              </FormControl>
            </HStack>

            <FormControl>
              <FormLabel>Notes</FormLabel>
              <Textarea
                value={formData.notes}
                onChange={handleChange('notes')}
                rows={3}
              />
            </FormControl>

            <Box mt={4}>
              <Heading size="md" mb={2}>Stops</Heading>
              {tripStops.length === 0 ? (
                <Box>No stops added.</Box>
              ) : (
                <Table size="sm">
                  <Thead>
                    <Tr>
                      <Th>#</Th>
                      <Th>Stop</Th>
                      <Th>Planned Arrival</Th>
                      <Th></Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {tripStops.map(ts => (
                      <Tr key={ts.id}>
                        <Td>{ts.order}</Td>
                        <Td>{ts.stop.name}</Td>
                        <Td>{ts.planned_arrival_time}</Td>
                        <Td>
                          <IconButton
                            aria-label="Remove stop"
                            icon={<DeleteIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteStop(ts.id)}
                          />
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              )}

              <HStack mt={4} spacing={2}>
                <Select
                  placeholder="Select stop"
                  value={newStop.stopId}
                  onChange={e => setNewStop(prev => ({ ...prev, stopId: e.target.value }))}
                >
                  {availableStops.map(stop => (
                    <option key={stop.id} value={stop.id}>{stop.name}</option>
                  ))}
                </Select>
                <Input
                  type="time"
                  value={newStop.time}
                  onChange={e => setNewStop(prev => ({ ...prev, time: e.target.value }))}
                />
                <Button
                  colorScheme="blue"
                  onClick={handleAddStop}
                  isLoading={isAdding}
                >
                  Add Stop
                </Button>
              </HStack>
            </Box>
          </VStack>
        </DrawerBody>

        <DrawerFooter>
          <Button variant="outline" mr={3} onClick={onClose}>
            Close
          </Button>
          <Button colorScheme="blue" onClick={handleSave} isLoading={isSaving}>
            Save Changes
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
};

