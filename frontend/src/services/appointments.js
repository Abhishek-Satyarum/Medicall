import api from './api'

export const getAppointments = (params) =>
  api.get('/appointments', { params }).then(({ data }) => data)

export const cancelAppointment = (appointmentId, phoneNumber) =>
  api.post('/appointments/cancel', {
    appointment_id: appointmentId,
    phone_number: phoneNumber,
  }).then(({ data }) => data)
