import api from './api'

export const getAvailability = (date, doctorId) =>
  api.get('/availability', {
    params: { date, ...(doctorId ? { doctor_id: doctorId } : {}) },
  }).then(({ data }) => data)
